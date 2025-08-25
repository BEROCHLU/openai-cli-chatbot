import os
from openai import OpenAI
import base64

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# ローカル画像をbase64エンコード
with open("showa.jpg", "rb") as f:
    img_base64 = base64.b64encode(f.read()).decode("utf-8")

# API呼び出し
response = client.chat.completions.create(
    model="gpt-4.1",  # gpt-4o / gpt-4o-mini / gpt-4.1 / gpt-5 など
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "この画像について説明してください",
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"},
                },
            ],
        }
    ],
)

print(response.choices[0].message.content)
