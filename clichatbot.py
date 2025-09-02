#!/usr/bin/env python3
import re
from openai import OpenAI
from rich.console import Console
from rich.markdown import Markdown


def get_api_params(messages: str, model: str, temperature: float, effort: str, response_id: str) -> dict:
    # 基本パラメータ
    params = {
        "input": messages,
        "model": model,
        "temperature": temperature,
        "max_output_tokens": 16384,
        "stream": False,
    }

    if not response_id:  # 初回
        params["instructions"] = (
            "You are a helpful assistant. "
            "Since the conversation will be saved in Markdown format, "
            "make your responses well-structured and easy to read in Markdown."
        )
    else:
        params["previous_response_id"] = response_id

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


def main():
    client = OpenAI()
    console = Console()

    response_id = None

    while True:
        user_input = input("user: ").strip()
        if not user_input:
            break

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

        api_params = get_api_params(messages, "gpt-5-mini", 0.5, "low", response_id)
        response = client.responses.create(**api_params)

        console.print(f"[bold green]assistant[/bold green]:")
        console.print(Markdown(response.output_text))
        response_id = response.id


if __name__ == "__main__":
    main()
