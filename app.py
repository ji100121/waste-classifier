
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/", methods=["GET"])
def home():
    return "Waste classifier server is running!"

@app.route("/classify", methods=["POST"])
def classify():
    if "image" not in request.files:
        return jsonify({"error": "사진이 없습니다."}), 400

    return jsonify({
        "category": "플라스틱"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
