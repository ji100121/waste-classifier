
import os
import json
import base64
import urllib.request
import urllib.error
from flask import Flask, request

app = Flask(__name__)

CATEGORIES = [
    "플라스틱",
    "종이",
    "일반쓰레기",
    "캔",
    "비닐",
    "유리",
    "라벨이 있는 플라스틱병"
]

@app.route("/", methods=["GET"])
def home():
    return "Waste classifier server is running!"

@app.route("/classify", methods=["POST"])
def classify():
    image_data = request.get_data()

    if not image_data:
        return "사진이 없습니다.", 400

    api_key = os.environ.get("OPENAI_API_KEY")

    if not api_key:
        return "서버에 API 키가 설정되지 않았습니다.", 500

    image_base64 = base64.b64encode(image_data).decode("ascii")
    image_url = "data:image/jpeg;base64," + image_base64

    prompt = """
    당신은 쓰레기 분류 전문가입니다.
    첨부된 사진을 보고 가장 적절한 분류 하나를 선택하세요.

    선택 가능한 분류:
    플라스틱, 종이, 일반쓰레기, 캔, 비닐, 유리,
    라벨이 있는 플라스틱병

    라벨이 붙어 있는 플라스틱병이 보이면
    '라벨이 있는 플라스틱병'을 우선 선택하세요.
    판단이 어려우면 가장 가까운 분류를 선택하세요.
    반드시 위 목록의 분류명 하나만 출력하세요.
    설명이나 다른 문장은 출력하지 마세요.
    """

    payload = {
        "model": "gpt-4.1-mini",
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": prompt
                    },
                    {
                        "type": "input_image",
                        "image_url": image_url,
                        "detail": "low"
                    }
                ]
            }
        ],
        "max_output_tokens": 50
    }

    req = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode("utf-8"))

        answer = ""

        for item in result.get("output", []):
            if item.get("type") == "message":
                for part in item.get("content", []):
                    if part.get("type") == "output_text":
                        answer += part.get("text", "")

        category = answer.strip()

        if category not in CATEGORIES:
            return "분류 실패", 200, {
                "Content-Type": "text/plain; charset=utf-8"
            }

        return category, 200, {
            "Content-Type": "text/plain; charset=utf-8"
        }

    except urllib.error.HTTPError as error:
        print("OpenAI API 오류:", error.read().decode("utf-8", errors="replace"))
        return "AI 분석 오류", 502

    except Exception as error:
        print("서버 오류:", str(error))
        return "서버 오류", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
