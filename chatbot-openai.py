#!/usr/bin/env python
import base64
import json
import os
import re
from datetime import datetime
from pathlib import Path

import pandas as pd
from openai import OpenAI
from rich.console import Console

import settings

MODEL = settings.MODEL
TEMPERATURE = settings.TEMPERATURE
REASONING_EFFORT = settings.REASONING_EFFORT

client = OpenAI()
console = Console()
history = [
    {
        "role": "system",
        "content": (
            "You are a helpful assistant. "
            "Since the conversation will be saved in Markdown format, "
            "make your responses well-structured and easy to read in Markdown."
        ),
    }
]


def get_api_params(model: str, temperature: float, reasoning_effort: str) -> dict:
    params = {
        "model": model,
        "messages": history,
        "temperature": temperature,
        "max_completion_tokens": 16384,
        "stream": True,
    }

    # gpt-4.1 系
    if re.match(r"^gpt-4\.1", model):
        params["max_completion_tokens"] = 32768

    # gpt-5 系 (chat-latestを除く)
    elif re.match(r"^gpt-5(?!-chat)", model):
        params.update(
            {
                "temperature": 1.0,
                "reasoning_effort": reasoning_effort,
                "max_completion_tokens": 128000,
            }
        )

    # o1～o9
    elif re.match(r"^o[1-9]", model):
        eff = "low" if reasoning_effort == "minimal" else reasoning_effort
        params.update(
            {
                "temperature": 1.0,
                "reasoning_effort": eff,
                "max_completion_tokens": 100000,
            }
        )

    return params


# ─── API パラメータ取得 ＆ model_label 設定 ────────────────────
api_params = get_api_params(MODEL, TEMPERATURE, REASONING_EFFORT)
# 推論モデルなら model + reasoning_effort
if re.match(r"^(gpt-5(?!-chat)|o[1-9])", MODEL):
    model_label = "-".join([MODEL, REASONING_EFFORT])
else:
    model_label = MODEL


def save_conversation(history, save_dir="./history"):
    os.makedirs(save_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    history_file = Path(save_dir) / f"{model_label}_{timestamp}.md"

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

    # 質問とファイルパスを ^ で区切る
    args = user_input.split(" ^ ")

    # 最初の引数を質問として扱う
    user_question = args[0].strip()
    lst_file_contents = []

    # 2つ目以降の引数があればファイルパスとして処理（複数ファイル対応・xlsx→JSON変換対応）
    if len(args) >= 2:
        file_paths = args[1:]

        for file_path in file_paths:
            file_path = file_path.strip()
            file_name = Path(file_path).name
            file_ext = Path(file_path).suffix.lower()

            try:
                if file_ext == ".xlsx":
                    # エクセルの場合はJSONに変換
                    sheets_dict = pd.read_excel(file_path, sheet_name=None)
                    json_data = {sheet: df.to_dict(orient="records") for sheet, df in sheets_dict.items()}
                    json_str = json.dumps(json_data, ensure_ascii=False, indent=2)

                    file_content = f"\n\n--- Converted JSON from Excel file: {file_path} ---\n\n"
                    file_content += json_str

                    file_content = {
                        "type": "text",
                        "text": file_content,
                    }

                    console.print(f"[bold green]Converted XLSX to JSON successfully: '{file_path}'[/bold green]")

                elif file_ext in [".jpg", ".jpeg", ".png"]:
                    # 画像はbase64に変換
                    with open(file_path, "rb") as f:
                        b64 = base64.b64encode(f.read()).decode("utf-8")

                    mime_type = "image/jpeg" if file_ext in [".jpg", ".jpeg"] else "image/png"
                    file_content = {
                        "type": "image_url",
                        "image_url": {"url": f"data:{mime_type};base64,{b64}"},
                    }

                    console.print(f"[bold magenta]Image loaded and encoded: '{file_path}'[/bold magenta]")

                elif file_ext == ".pdf":
                    # pdfもbase64に変換
                    with open(file_path, "rb") as f:
                        b64 = base64.b64encode(f.read()).decode("utf-8")

                    file_content = {
                        "type": "file",
                        "file": {
                            "filename": file_name,
                            "file_data": f"data:application/pdf;base64,{b64}",
                        },
                    }

                    console.print(f"[bold orange1]pdf loaded and encoded: '{file_path}'[/bold orange1]")

                else:  # text-based
                    with open(file_path, "r", encoding="utf-8") as file:
                        file_content = f"\n\n--- File: {file_path} ---\n\n"
                        file_content += file.read()

                    file_content = {
                        "type": "text",
                        "text": file_content,
                    }

                    console.print(f"[bold blue]Completed loading the file: '{file_path}'[/bold blue]")
                # if文が終わったらfile_contentをappend
                lst_file_contents.append(file_content)

            except Exception as e:
                console.print(f"[bold red]Error processing file '{file_path}': {e}[/bold red]")
                break

    # role: userのcontentを作成
    if lst_file_contents:

        user_contents = [
            {
                "type": "text",
                "text": user_question,
            }
        ]

        user_contents.extend(lst_file_contents)
        history.append({"role": "user", "content": user_contents})  # type: ignore
    else:
        history.append({"role": "user", "content": user_question})

    # API 呼び出し
    try:
        api_params["messages"] = history  # 念のためにhistoryを追加
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
