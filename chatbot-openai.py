#!/usr/bin/env python
import os
import re
import settings

from datetime import datetime
from openai import OpenAI
from rich.console import Console
from rich.markdown import Markdown

API_KEY = os.environ.get("OPENAI_API_KEY")  # 環境変数に設定したAPIキーを取得
MODEL = settings.MODEL
TEMPERATURE = settings.TEMPERATURE
REASONING_EFFORT = settings.REASONING_EFFORT

client = OpenAI(api_key=API_KEY)
console = Console()

# 会話の初期コンテキストとして system メッセージを設定
conversation = [
    {"role": "system", "content": "You are a helpful assistant"},
]

api_params = {
    "model": MODEL,
    "messages": conversation,
    "temperature": TEMPERATURE,
    "max_completion_tokens": 16384,  # max_tokens(Deprecated)と違い、出力トークンのみの制限
}

# モデル別設定
if re.match(r"^o[1-9]", MODEL):
    api_params["temperature"] = 1.0
    api_params["reasoning_effort"] = REASONING_EFFORT
    api_params["max_completion_tokens"] = 99999
elif re.match(r"^gpt-4\.1", MODEL):
    api_params["max_completion_tokens"] = 32768


# 会話履歴保存処理を関数化
def save_conversation(history, save_dir="./history"):
    os.makedirs(save_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    history_file = os.path.join(save_dir, f"{api_params['model']}_{timestamp}.md")

    try:
        with open(history_file, "w", encoding="utf-8") as f:
            # 会話履歴の出力
            for msg in history:
                f.write(f'{msg["role"].capitalize()}: {msg["content"]}\n\n')
        console.print(f"[bold blue]Conversation history saved to {history_file}[/bold blue]")
    except Exception as e:
        console.print(f"[bold red]Failed to save conversation history: {e}[/bold red]")


# メインループ（ユーザーとの会話を処理）
while True:
    # ユーザーからの入力を取得
    user_input = input("User: ")
    if not user_input:
        break

    # コマンド"!save"が入力された場合、その時点で会話履歴を即時保存する
    if user_input.strip() == "!save":
        save_conversation(conversation)  # 会話を保存（会話は終了せず継続）
        continue  # 会話を継続するためループを続行

    # 質問とファイルパスを | で区切る
    args = user_input.split(" | ")

    # 最初の引数を質問として扱う
    user_question = args[0].strip()
    file_contents = ""

    # 2つ目以降の引数があればファイルパスとして処理（複数ファイル対応）
    if len(args) >= 2:
        file_paths = args[1:]  # 2つ目以降の引数をすべてファイルパスとして扱う
        for file_path in file_paths:
            file_path = file_path.strip()
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    file_contents += f"\n\n--- File: {file_path} ---\n\n"
                    file_contents += file.read()
                console.print(f"[bold blue]Completed loading the file: '{file_path}'[/bold blue]")
            except Exception as e:
                console.print(f"[bold red]Error loading file '{file_path}': {e}[/bold red]")
                break

    # AIの応答を会話履歴に追加
    if file_contents:
        conversation.append({"role": "user", "content": f"{user_question}\n\n{file_contents}"})
    else:
        conversation.append({"role": "user", "content": user_question})

    # API 呼び出し（タイムアウトや例外に備えエラーハンドリング）
    try:
        response = client.chat.completions.create(**api_params, stream=True)

        console.print("[bold green]Assistant:[/bold green]")

        assistant_reply = ""
        for chunk in response:
            delta = chunk.choices[0].delta
            if hasattr(delta, "content") and delta.content:
                assistant_reply += delta.content
                console.print(delta.content, end="", style="white")
        console.print("\n")

        conversation.append({"role": "assistant", "content": assistant_reply})
    except Exception as e:
        console.print(f"[bold red]Error occurred: {e}[/bold red]\n")
        continue


# 最後に会話を終了する際に、履歴をファイルへ保存（会話が実質なかった場合は保存しない）
if len(conversation) > 1:
    save_conversation(conversation)  # 会話を最後にまとめて保存
