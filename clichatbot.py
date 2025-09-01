#!/usr/bin/env python3
from openai import OpenAI
from rich.console import Console
from rich.markdown import Markdown


def main():
    client = OpenAI()
    console = Console()

    response_id = None
    messages = [
        {
            "role": "developer",
            "content": (
                "You are a helpful assistant."
                "Since the conversation will be saved in Markdown format,"
                "make your responses well-structured and easy to read in Markdown."
            ),
        }
    ]

    while True:
        user_input = input("user: ").strip()
        if not user_input:
            break

        messages.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": user_input,
                    }
                ],
            }
        )

        response = client.responses.create(
            model="gpt-5-chat-latest",
            temperature=0.5,
            max_output_tokens=16384,
            stream=False,
            input=messages,
            previous_response_id=response_id,
        )

        console.print(f"[bold green]assistant[/bold green]:")
        console.print(Markdown(response.output_text))
        response_id = response.id


if __name__ == "__main__":
    main()
