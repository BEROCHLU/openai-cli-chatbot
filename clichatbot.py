#!/usr/bin/env python3
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

from openai import OpenAI
from rich.console import Console
from rich.markdown import Markdown

import settings

client = OpenAI()
console = Console()


def get_api_params(
    messages: list, model: str, temperature: float, effort: Optional[str], response_id: Optional[str]
) -> dict:
    # 基本パラメータ
    params = {
        "input": messages,
        "model": model,
        "temperature": temperature,
        "max_output_tokens": 16384,
        "stream": False,
        "previous_response_id": response_id,
    }
    """
    if response_id:
        params["previous_response_id"] = response_id
    """
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


def main():
    MODEL: str = settings.MODEL
    TEMPERATURE: float = settings.TEMPERATURE
    REASONING_EFFORT: Optional[str] = settings.REASONING_EFFORT

    # 推論モデルなら model + reasoning_effort
    if re.match(r"^(gpt-5(?!-chat)|o[1-9])", MODEL):
        MODEL_LABEL = "-".join([MODEL, REASONING_EFFORT])
    else:
        MODEL_LABEL = MODEL

    response_id = None
    transcript = []  # 会話ログ（ローカル保持用）

    while True:
        user_input = input("user: ").strip()
        if not user_input:
            break

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

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": user_input,
                    }
                ],
            }
        ]

        if not response_id:
            messages = developer_prompt + messages

        # コマンド"!save"が入力された場合、その時点で会話履歴を即時保存する
        if user_input.strip() == "!save":
            save_transcript(transcript, MODEL_LABEL)
            continue  # 会話を継続するためループを続行

        api_params = get_api_params(messages, MODEL, TEMPERATURE, REASONING_EFFORT, response_id)
        response = client.responses.create(**api_params)

        console.print(f"[bold green]assistant[/bold green]:")
        console.print(Markdown(response.output_text))

        response_id = response.id
        transcript.append({"user": user_input, "assistant": response.output_text})
    # while True
    save_transcript(transcript, MODEL_LABEL)


if __name__ == "__main__":
    main()
