import os
from flask import Flask, render_template_string, request
from google import genai

app = Flask(__name__)

# Renderの環境変数から API KEY (ARUPAKA_KEY) を取得
api_key = os.environ.get("ARUPAKA_KEY")

# 新しいSDKで正しく動作する標準モデル
MODEL_NAME = "gemini-2.5-flash"

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
        .error-msg { background: #fff3cd; color: #856404; padding: 10px; border-radius: 6px; margin-bottom: 10px; }
    </style>
</head>
<body>
    <h1>🤖 AI × 🧐 AI の会話</h1>
    <div class="chat-box">
        {% if error %}
            <div class="error-msg">⚠️ {{ error }}</div>
        {% endif %}
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

@app.route("/", methods=["GET", "HEAD"])
def index():
    # Renderの疎通確認(HEADリクエスト)のときは重い処理をスキップ
    if request.method == "HEAD":
        return "", 200

    if not api_key:
        return render_template_string(HTML_TEMPLATE, logs=[], error="ARUPAKA_KEY が設定されていません。"), 500

    chat_logs = []
    error_detail = None
    
    SYSTEM_PROMPT_A = "あなたはポジティブで元気なAIロボットです。短く返答してください。"
    SYSTEM_PROMPT_B = "あなたは少し皮肉屋で冷静なAIです。相手の言葉に短くツッコミを入れてください。"

    try:
        client = genai.Client(api_key=api_key)
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

    except Exception as e:
        error_detail = f"API実行中にエラーが発生しました（一時的な回数制限などの可能性があります）: {str(e)}"

    return render_template_string(HTML_TEMPLATE, logs=chat_logs, error=error_detail)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
