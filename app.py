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
