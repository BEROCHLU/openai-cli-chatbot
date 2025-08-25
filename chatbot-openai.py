#!/usr/bin/env python
import os
import re
import settings
import json
import pandas as pd
from datetime import datetime
from openai import OpenAI
from rich.console import Console
from rich.markdown import Markdown

MODEL = settings.MODEL
TEMPERATURE = settings.TEMPERATURE
REASONING_EFFORT = settings.REASONING_EFFORT

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))  # 環境変数に設定したAPIキーを取得
console = Console()
history = []

api_params = {
    "model": MODEL,
    "messages": history,
    "temperature": TEMPERATURE,
    "max_completion_tokens": 16384,  # max_tokens(Deprecated)と違い、出力トークンのみの制限
    "stream": True,
}

model_label = "_".join([MODEL, str(TEMPERATURE)])

# モデル別output設定
if re.match(r"^gpt-4\.1", MODEL):
    api_params["max_completion_tokens"] = 32768
elif re.match(r"(^gpt-5-chat-latest$|^gpt-4o-mini$|^gpt-4o$)", MODEL):  # gpt-5-chat-latestはchatモデル
    pass
elif re.match(r"^gpt-5", MODEL):  # gpt-5は推論モデル
    api_params["temperature"] = 1.0
    api_params["reasoning_effort"] = REASONING_EFFORT
    api_params["max_completion_tokens"] = 128000

    model_label = "_".join([MODEL, REASONING_EFFORT])
elif re.match(r"^o[1-9]", MODEL):
    if REASONING_EFFORT == "minimal":  # minimalはgpt-5のみ有効
        REASONING_EFFORT = "low"
        print(
            f'The parameter reasoning.effort was changed to "low" because "minimal" is reserved for gpt-5 or gpt-5-mini.'
        )

    api_params["temperature"] = 1.0
    api_params["reasoning_effort"] = REASONING_EFFORT
    api_params["max_completion_tokens"] = 99999

    model_label = "_".join([MODEL, REASONING_EFFORT])


# 会話履歴保存処理を関数化
def save_conversation(history, save_dir="./history"):
    os.makedirs(save_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    history_file = os.path.join(save_dir, f"{model_label}_{timestamp}.md")

    try:
        with open(history_file, "w", encoding="utf-8") as f:
            # 会話履歴の出力
            for msg in history:
                f.write(f'{msg["role"]}: {msg["content"]}\n\n')

        console.print(f"[bold blue]Conversation history saved to {history_file}[/bold blue]")
    except Exception as e:
        console.print(f"[bold red]Failed to save conversation history: {e}[/bold red]")


# メインループ（ユーザーとの会話を処理）
while True:
    # ユーザーからの入力を取得
    user_input = input("user: ")
    if not user_input:
        break

    # コマンド"!save"が入力された場合、その時点で会話履歴を即時保存する
    if user_input.strip() == "!save":
        save_conversation(history)  # 会話を保存（会話は終了せず継続）
        continue  # 会話を継続するためループを続行

    # 質問とファイルパスを | で区切る
    args = user_input.split(" | ")

    # 最初の引数を質問として扱う
    user_question = args[0].strip()
    file_contents = ""

    # 2つ目以降の引数があればファイルパスとして処理（複数ファイル対応・xlsx→JSON変換対応）
    if len(args) >= 2:
        file_paths = args[1:]
        for file_path in file_paths:
            file_path = file_path.strip()
            file_ext = os.path.splitext(file_path)[1].lower()

            try:
                if file_ext == ".xlsx":
                    # エクセルの場合はJSONに変換
                    sheets_dict = pd.read_excel(file_path, sheet_name=None)
                    json_data = {sheet: df.to_dict(orient="records") for sheet, df in sheets_dict.items()}
                    json_str = json.dumps(json_data, ensure_ascii=False, indent=2)

                    file_contents += f"\n\n--- Converted JSON from Excel file: {file_path} ---\n\n"
                    file_contents += json_str

                    console.print(f"[bold green]Converted XLSX to JSON successfully: '{file_path}'[/bold green]")

                else:
                    # 通常ファイルはそのまま処理
                    with open(file_path, "r", encoding="utf-8") as file:
                        file_contents += f"\n\n--- File: {file_path} ---\n\n"
                        file_contents += file.read()

                    console.print(f"[bold blue]Completed loading the file: '{file_path}'[/bold blue]")

            except Exception as e:
                console.print(f"[bold red]Error processing file '{file_path}': {e}[/bold red]")
                break

    # AIの応答を会話履歴に追加
    if file_contents:
        history.append({"role": "user", "content": f"{user_question}\n\n{file_contents}"})
    else:
        history.append({"role": "user", "content": user_question})

    # API 呼び出し（タイムアウトや例外に備えエラーハンドリング）
    try:
        completion = client.chat.completions.create(**api_params)

        console.print(f"[bold green]{model_label} assistant:[/bold green]")

        completion_reply = ""
        for chunk in completion:
            if chunk.choices[0].delta.content is not None:
                console.print(chunk.choices[0].delta.content, end="", style="white")
                completion_reply += chunk.choices[0].delta.content

        console.print("\n")

        history.append({"role": "assistant", "content": completion_reply})
    except Exception as e:
        console.print(f"[bold red]Error occurred: {e}[/bold red]\n")
        save_conversation(history)
        continue


# 最後に会話を終了する際に、履歴をファイルへ保存（会話が実質なかった場合は保存しない）
if len(history) > 1:
    save_conversation(history)  # 会話を最後にまとめて保存
