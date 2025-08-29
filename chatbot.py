from openai import OpenAI

client = OpenAI()

response = client.responses.create(
    model="gpt-5",
    input=[
        {
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": "ドキュメントを分析して要約しろ。",
                },
                {
                    "type": "input_file",
                    "file_url": "http://pleasecov.g2.xrea.com/xlcy/public/static/remote/Apple-24Q2.xlsx",
                },
            ],
        },
    ],
)

print(response.output_text)
