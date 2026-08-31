import os
from flask import Flask, render_template_string
from google import genai

app = Flask(__name__)

# Renderの環境変数から API KEY (ARUPAKA_KEY) を取得
api_key = os.environ.get("ARUPAKA_KEY")
client = genai.Client(api_key=api_key)

MODEL_NAME = "gemini-3.6-flash"

SYSTEM_PROMPT_A = "あなたはポジティブで元気なAIロボットです。短くポップに返答してください。"
SYSTEM_PROMPT_B = "あなたは少し皮肉屋で冷静なAIです。相手の言葉に短くツッコミを入れてください。"

# HTMLテンプレート（簡易チャットデザイン）
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
    chat_logs = []
    chat_history_a = []
    chat_history_b = []

    current_message = "やあ！今日は何をして遊ぶ？"
    chat_logs.append({"speaker": "🤖 AI_A", "text": current_message, "css_class": "ai-a"})

    # 交互に4ターン会話
    for _ in range(4):
        # AI_B
        chat_history_b.append({"role": "user", "parts": [{"text": current_message}]})
        response_b = client.models.generate_content(
            model=MODEL_NAME,
            contents=chat_history_b,
            config={"system_instruction": SYSTEM_PROMPT_B}
        )
        reply_b = response_b.text
        chat_logs.append({"speaker": "🧐 AI_B", "text": reply_b, "css_class": "ai-b"})
        chat_history_b.append({"role": "model", "parts": [{"text": reply_b}]})

        # AI_A
        chat_history_a.append({"role": "user", "parts": [{"text": reply_b}]})
        response_a = client.models.generate_content(
            model=MODEL_NAME,
            contents=chat_history_a,
            config={"system_instruction": SYSTEM_PROMPT_A}
        )
        current_message = response_a.text
        chat_logs.append({"speaker": "🤖 AI_A", "text": current_message, "css_class": "ai-a"})
        chat_history_a.append({"role": "model", "parts": [{"text": current_message}]})

    return render_template_string(HTML_TEMPLATE, logs=chat_logs)

if __name__ == "__main__":
    # Renderが指定するポート番号で起動
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
