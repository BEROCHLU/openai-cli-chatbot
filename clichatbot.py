#!/usr/bin/env python3
from openai import OpenAI
from rich.console import Console


def main():
    client = OpenAI()
    console = Console()

    response_id = None

    while True:
        user_input = input("user: ").strip()
        if not user_input:
            break

        response = client.responses.create(
            model="gpt-4.1",
            input=[
                {
                    "role": "user",
                    "content": user_input,
                }
            ],
            previous_response_id=response_id,
        )

        console.print(f"[bold green]assistant[/bold green]: {response.output_text}")
        response_id = response.id


if __name__ == "__main__":
    main()
