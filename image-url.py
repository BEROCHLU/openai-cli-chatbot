import os
from openai import OpenAI

API_KEY = os.environ.get("OPENAI_API_KEY")  # 環境変数に設定したAPIキーを取得
client = OpenAI(api_key=API_KEY)


res = client.responses.create(
    model="gpt-4o",
    input=[
        {
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": "この画像を日本語で説明してください。",
                },
                {
                    "type": "input_image",
                    "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e7/Everest_North_Face_toward_Base_Camp_Tibet_Luca_Galuzzi_2006.jpg",
                },
            ],
        }
    ],
)
print(res.output_text)
