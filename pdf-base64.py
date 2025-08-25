import os
from openai import OpenAI
import base64

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# ローカル画像をbase64エンコード
"""
with open(".file/現地費用.pdf", "rb") as f:
    b64 = base64.b64encode(f.read()).decode("utf-8")
"""

with open(".file/test.pdf", "rb") as f:
    b64 = base64.b64encode(f.read()).decode("utf-8")

response = client.chat.completions.create(
    model="gpt-4.1",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "これは何？",
                },
                {
                    "type": "file",
                    "file": {
                        "filename": "unko.pdf",
                        "file_data": f"data:application/pdf;base64,{b64}",
                    },
                },
            ],
        },
    ],
)

print(response.choices[0].message.content)
