import os
from flask import Flask, render_template_string
from google import genai

app = Flask(__name__)

# Renderの環境変数から API KEY (ARUPAKA_KEY) を取得
api_key = os.environ.get("ARUPAKA_KEY")

# 最も安定している gemini-1.5-flash を指定
MODEL_NAME = "gemini-1.5-flash"

SYSTEM_PROMPT_A = "あなたはポジティブで元気なAIロボットです。短く返答してください。"
SYSTEM_PROMPT_B = "あなたは少し皮肉屋で冷静なAIです。相手の言葉に短くツッコミを入れてください。"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI vs AI Chat</title>
    <style>
        body { font-family: sans-serif; background: #f4f4f9; padding: 20px; max-width: 600px; margin: 0 auto; }
        h1 { text-align: center; color: #333; }
        .chat-box { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .msg { margin-bottom: 15px; padding: 10px 15px; border-radius: 8px; line-height: 1.4; }
        .ai-a { background: #e3f2fd; border-left: 5px solid #2196f3; }
        .ai-b { background: #ffebee; border-left: 5px solid #f44336; }
        .speaker { font-weight: bold; margin-bottom: 5px; font-size: 0.9em; }
        .reload-btn { display: block; width: 100%; text-align: center; padding: 10px; background: #4caf50; color: white; border: none; border-radius: 6px; font-size: 16px; cursor: pointer; text-decoration: none; margin-top: 20px; }
    </style>
</head>
<body>
    <h1>🤖 AI × 🧐 AI の会話</h1>
    <div class="chat-box">
        {% for chat in logs %}
            <div class="msg {{ chat.css_class }}">
                <div class="speaker">{{ chat.speaker }}</div>
                <div>{{ chat.text }}</div>
            </div>
        {% endfor %}
    </div>
    <a href="/" class="reload-btn">もう一度会話させる 🔄</a>
</body>
</html>
"""

@app.route("/")
def index():
    if not api_key:
        return "エラー: ARUPAKA_KEY が設定されていません。RenderのEnvironmentを確認してください。", 500

    client = genai.Client(api_key=api_key)
    chat_logs = []

    current_message = "やあ！今日は何をして遊ぶ？"
    chat_logs.append({"speaker": "🤖 AI_A", "text": current_message, "css_class": "ai-a"})

    # AI_Bの返答
    response_b = client.models.generate_content(
        model=MODEL_NAME,
        contents=current_message,
        config={"system_instruction": SYSTEM_PROMPT_B}
    )
    reply_b = response_b.text
    chat_logs.append({"speaker": "🧐 AI_B", "text": reply_b, "css_class": "ai-b"})

    # AI_Aの返答
    response_a = client.models.generate_content(
        model=MODEL_NAME,
        contents=reply_b,
        config={"system_instruction": SYSTEM_PROMPT_A}
    )
    reply_a = response_a.text
    chat_logs.append({"speaker": "🤖 AI_A", "text": reply_a, "css_class": "ai-a"})

    return render_template_string(HTML_TEMPLATE, logs=chat_logs)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
