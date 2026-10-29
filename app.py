
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Waste classifier server is running!"

@app.route("/classify", methods=["POST"])
def classify():
    # 앱인벤터가 보낸 사진 파일 받기
    image_data = request.get_data()

    # 사진이 없으면 오류 반환
    if not image_data:
        return jsonify({
            "error": "사진이 없습니다."
        }), 400

    # 현재는 연결 테스트용 결과
    return jsonify({
        "category": "플라스틱"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
