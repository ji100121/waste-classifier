
import os
import base64

from flask import Flask, request, Response
from openai import OpenAI

app = Flask(__name__)

# AI 분류 결과.
CATEGORIES = [
    "재활용",
    "일반쓰레기",
    "비닐",
    "라벨이 붙은 플라스틱"
]


@app.route("/", methods=["GET"])
def home():
    return "Waste classifier server is running!"


@app.route("/classify", methods=["POST"])
def classify():

    # 앱인벤터에서 보낸 이미지 받기
    image_bytes = request.get_data()

    if not image_bytes:
        return Response(
            "사진이 없습니다.",
            status=400,
            content_type="text/plain; charset=utf-8"
        )

    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        return Response(
            "API 키가 없습니다.",
            status=500,
            content_type="text/plain; charset=utf-8"
        )

    try:
        client = OpenAI(api_key=api_key)

        image_base64 = base64.b64encode(
            image_bytes
        ).decode("utf-8")

        image_url = (
            "data:image/jpeg;base64," + image_base64
        )

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": """
너는 쓰레기 분리배출을 돕는 AI야.

사진 속 주요 쓰레기 하나를 분류해.

반드시 다음 네 가지 결과 중 하나만 반환해.

재활용
일반쓰레기
비닐
라벨이 붙은 플라스틱

분류 기준:

1. 플라스틱, 캔, 유리, 종이 등은
   재활용으로 분류해.

2. 깨끗한 비닐봉지나 비닐 포장재는
   비닐로 분류해.

3. 오염된 휴지 등 재활용이 어려운
   쓰레기는 일반쓰레기로 분류해.

4. 플라스틱병에 제거 가능한 라벨이
   붙어 있는 것이 보이면
   라벨이 붙은 플라스틱으로 분류해.

5. 라벨이 없는 플라스틱병은
   재활용으로 분류해.

6. 라벨이 붙은 플라스틱병은
   다른 분류보다 우선해서 판단해.

7. 사진에서 라벨이 확인되지 않으면
   라벨이 있다고 추측하지 마.

반드시 네 가지 중 하나의 문구만 반환해.
설명, JSON, 기호는 추가하지 마.
"""
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "이 쓰레기를 분류해 줘."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
            ],
            max_tokens=100
        )

        result = (
            response.choices[0].message.content
            or ""
        ).strip()

        if result not in CATEGORIES:
            return Response(
                "분류 결과 오류",
                status=500,
                content_type="text/plain; charset=utf-8"
            )

        return Response(
            result,
            content_type="text/plain; charset=utf-8"
        )

    except Exception as e:
        print("Classification error:", str(e))

        return Response(
            "서버 오류",
            status=500,
            content_type="text/plain; charset=utf-8"
        )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 10000))
    )
