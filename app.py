
import os
import base64

from flask import Flask, request, Response
from openai import OpenAI

app = Flask(__name__)

# AI 분류 종류
CATEGORIES = [
    "플라스틱",
    "일반쓰레기",
    "비닐"
]

# OpenAI 모델
MODEL = "gpt-4.1-mini"


@app.route("/", methods=["GET"])
def home():
    return "Waste classifier server is running!"


@app.route("/classify", methods=["POST"])
def classify():

    # 1. 앱인벤터에서 보낸 사진 받기
    image_bytes = request.get_data()

    if not image_bytes:
        return Response(
            "사진이 없습니다.",
            status=400,
            content_type="text/plain; charset=utf-8"
        )

    # 2. API 키 확인
    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        return Response(
            "API 키가 설정되지 않았습니다.",
            status=500,
            content_type="text/plain; charset=utf-8"
        )

    try:
        client = OpenAI(api_key=api_key)

        # 3. 이미지 Base64 변환
        image_base64 = base64.b64encode(
            image_bytes
        ).decode("utf-8")

        image_url = (
            "data:image/jpeg;base64,"
            + image_base64
        )

        # 4. AI 분류 지시문
        prompt = """
당신은 쓰레기 분류 AI입니다.

사진 속 쓰레기를 다음 3가지 중
정확히 하나로 분류하세요.

1. 플라스틱
2. 일반쓰레기
3. 비닐

분류 기준:

[플라스틱]
- 페트병
- 플라스틱 컵
- 플라스틱 용기
- 플라스틱 뚜껑
- 플라스틱 포장 용기
- 라벨이 붙은 플라스틱병도 플라스틱

[비닐]
- 비닐봉지
- 비닐 포장재
- 비닐 랩
- 얇고 유연한 비닐류

[일반쓰레기]
- 플라스틱과 비닐이 아닌 물건
- 휴지
- 음식물 등이 묻은 일반 폐기물
- 종이, 캔, 유리 등 별도 분류가 없는 물건

중요 규칙:
- 반드시 3가지 중 하나만 선택하세요.
- 설명이나 추가 문장은 작성하지 마세요.
- 반드시 한국어로 답하세요.
- 출력은 아래 중 하나여야 합니다.

플라스틱
일반쓰레기
비닐
"""

        # 5. OpenAI 이미지 분석
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
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
            temperature=0,
            max_tokens=30
        )

        # 6. AI 결과 가져오기
        result = (
            response.choices[0].message.content
            or ""
        ).strip()

        # 7. 결과 확인
        if result not in CATEGORIES:
            app.logger.warning(
                "Unexpected AI result: %s", result
            )

            return Response(
                "분류 결과 오류",
                status=502,
                content_type="text/plain; charset=utf-8"
            )

        # 8. 앱인벤터로 결과 전송
        return Response(
            result,
            status=200,
            content_type="text/plain; charset=utf-8"
        )

    except Exception:
        app.logger.exception("Classification failed")

        return Response(
            "서버 오류",
            status=500,
            content_type="text/plain; charset=utf-8"
        )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))

    app.run(
        host="0.0.0.0",
        port=port
    )
