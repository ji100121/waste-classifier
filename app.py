import os
import json
import base64
import urllib.request
import urllib.error
from flask import Flask, request

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

CATEGORIES = [
    "플라스틱",
    "종이",
    "일반쓰레기",
    "캔",
    "비닐",
    "유리",
    "라벨이 있는 플라스틱병",
]


def plain_text(message, status=200):
    return message, status, {"Content-Type": "text/plain; charset=utf-8"}


@app.route("/", methods=["GET"])
def home():
    return "Waste classifier server is running!"


@app.route("/classify", methods=["POST"])
def classify():
    # MIT App Inventor Web1.PostFile sends raw image bytes.
    image_data = request.get_data()
    if not image_data:
        return plain_text("사진이 없습니다.", 400)

    if image_data.startswith(b"\xff\xd8\xff"):
        image_type = "image/jpeg"
    elif image_data.startswith(b"\x89PNG\r\n\x1a\n"):
        image_type = "image/png"
    elif image_data.startswith(b"RIFF") and image_data[8:12] == b"WEBP":
        image_type = "image/webp"
    else:
        return plain_text("지원하지 않는 이미지 형식입니다.", 400)

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return plain_text("서버에 API 키가 설정되지 않았습니다.", 500)

    image_base64 = base64.b64encode(image_data).decode("ascii")
    image_url = "data:" + image_type + ";base64," + image_base64

    prompt = (
        "당신은 쓰레기 분류 전문가입니다. 첨부된 사진에서 주된 쓰레기를 "
        "다음 일곱 분류 중 정확히 하나로 분류하세요: "
        + ", ".join(CATEGORIES)
        + ". 라벨이 붙은 플라스틱병은 '라벨이 있는 플라스틱병'을 우선 선택하세요. "
        "분류명 하나만 정확히 출력하고 다른 설명은 하지 마세요."
    )

    payload = {
        "model": "gpt-4.1-mini",
        "input": [
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {"type": "input_image", "image_url": image_url, "detail": "low"},
                ],
            }
        ],
        "max_output_tokens": 50,
    }

    req = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json",
        },
        method="POST",
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
            return plain_text("분류 실패")
        return plain_text(category)

    except urllib.error.HTTPError as error:
        print("OpenAI API 오류:", error.code, error.read().decode("utf-8", errors="replace"))
        return plain_text("AI 분석 오류", 502)
    except Exception as error:
        print("서버 오류:", str(error))
        return plain_text("서버 오류", 500)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
