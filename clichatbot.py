#!/usr/bin/env python3
import base64
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
from openai import OpenAI
from rich.console import Console
from rich.markdown import Markdown

import settings

client = OpenAI()
console = Console()


def get_api_params(
    messages: list, model: str, temperature: float, stream: bool, effort: str, response_id: Optional[str]
) -> dict:
    # 基本パラメータ
    params = {
        "input": messages,
        "model": model,
        "temperature": temperature,
        "max_output_tokens": 16384,
        "stream": stream,
        "previous_response_id": response_id,
    }

    # gpt-4.1 系
    if re.match(r"^gpt-4\.1", model):
        params["max_output_tokens"] = 32768

    # gpt-5 系 (chat-latestを除く)
    elif re.match(r"^gpt-5(?!-chat)", model):
        params.update(
            {
                "temperature": 1.0,
                "max_output_tokens": 128000,
                "reasoning": {"effort": effort},
            }
        )

    # o3～o9
    elif re.match(r"^o[3-9]", model):
        eff = "low" if effort == "minimal" else effort
        params.update(
            {
                "temperature": 1.0,
                "max_output_tokens": 100000,
                "reasoning": {"effort": eff},
            }
        )

    return params


def save_transcript(transcript: list, model_label: str, save_dir="./history") -> None:
    os.makedirs(save_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    history_file = Path(save_dir) / f"{model_label}_{timestamp}.md"

    try:
        with open(history_file, "w", encoding="utf-8") as f:
            # 会話履歴の出力
            for speaker in transcript:
                f.write(f"user: {speaker['user']}\nassistant: {speaker['assistant']}\n")

        console.print(f"[bold blue]Conversation history saved to {history_file}[/bold blue]")
    except Exception as e:
        console.print(f"[bold red]Failed to save conversation history: {e}[/bold red]")


def attach_filecontents(file_paths):
    lst_filecontents = []

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
                    "type": "input_text",
                    "text": file_content,
                }

                console.print(f"[bold green]Converted XLSX to JSON successfully: '{file_path}'[/bold green]")

            elif file_ext in [".jpg", ".jpeg", ".png"]:
                # 画像はbase64に変換
                with open(file_path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("utf-8")

                mime_type = "image/jpeg" if file_ext in [".jpg", ".jpeg"] else "image/png"
                file_content = {
                    "type": "input_image",
                    "image_url": f"data:{mime_type};base64,{b64}",
                }

                console.print(f"[bold magenta]Image loaded and encoded: '{file_path}'[/bold magenta]")

            elif file_ext == ".pdf":
                # pdfもbase64に変換
                with open(file_path, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("utf-8")

                file_content = {
                    "type": "input_file",
                    "filename": file_name,
                    "file_data": f"data:application/pdf;base64,{b64}",
                }

                console.print(f"[bold orange1]pdf loaded and encoded: '{file_path}'[/bold orange1]")

            else:  # text-based
                with open(file_path, "r", encoding="utf-8") as file:
                    file_content = f"\n\n--- File: {file_path} ---\n\n"
                    file_content += file.read()

                file_content = {
                    "type": "input_text",
                    "text": file_content,
                }

                console.print(f"[bold blue]Completed loading the file: '{file_path}'[/bold blue]")
            # if file_ext == ".xlsx":
            lst_filecontents.append(file_content)

        except Exception as e:
            console.print(f"[bold red]Error processing file '{file_path}': {e}[/bold red]")
            break
    # for file_path in file_paths:
    return lst_filecontents


def main():
    MODEL: str = settings.MODEL
    TEMPERATURE: float = settings.TEMPERATURE
    STREAM: bool = settings.STREAM
    REASONING_EFFORT: Optional[str] = settings.REASONING_EFFORT

    # 推論モデルなら model + reasoning_effort
    if re.match(r"^(gpt-5(?!-chat)|o[3-9])", MODEL):
        MODEL_LABEL = "-".join([MODEL, REASONING_EFFORT])
    else:
        MODEL_LABEL = MODEL

    response_id = None
    transcript = []  # 会話ログ（ローカル保持用）
    lst_filecontents = []
    developer_prompt = [
        {
            "role": "developer",
            "content": (
                "You are a helpful assistant. "
                "Since the conversation will be saved in Markdown format, "
                "make your responses well-structured and easy to read in Markdown."
            ),
        }
    ]

    while True:
        user_input = input("user: ").strip()
        if not user_input:
            break
        elif user_input.strip() == "!save":
            save_transcript(transcript, MODEL_LABEL)
            continue

        args = user_input.split(" ^ ")  # 質問とファイルパスを ^ で区切る
        user_question = args[0].strip()  # 最初の引数を質問として扱う
        user_index = 0

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": user_question,
                    }
                ],
            }
        ]

        if response_id is None:
            messages = developer_prompt + messages
            user_index = 1

        # 2つ目以降の引数があればファイルパスとして処理（複数ファイル対応）
        if len(args) >= 2:
            file_paths = args[1:]
            lst_filecontents = attach_filecontents(file_paths)
            messages[user_index]["content"].extend(lst_filecontents)  # type: ignore

        api_params = get_api_params(messages, MODEL, TEMPERATURE, STREAM, REASONING_EFFORT, response_id)
        response = client.responses.create(**api_params)

        console.print(f"[bold green]{MODEL_LABEL} assistant[/bold green]:")

        if STREAM:
            for event in response:
                if event.type == "response.output_text.delta":
                    console.print(event.delta, end="")
                elif event.type == "response.completed":
                    console.print("")
                    response_id = event.response.id
                    transcript.append({"user": user_input, "assistant": event.response.output_text})
        else:
            console.print(Markdown(response.output_text))
            response_id = response.id
            transcript.append({"user": user_input, "assistant": response.output_text})
    # while True
    if transcript:
        save_transcript(transcript, MODEL_LABEL)


if __name__ == "__main__":
    main()
