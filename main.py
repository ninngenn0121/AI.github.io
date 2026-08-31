import os
from flask import Flask, render_template_string, request, redirect, url_for
from google import genai

app = Flask(__name__)

# Render環境変数からAPIキーを取得
api_key = os.environ.get("ARUPAKA_KEY")
MODEL_NAME = "gemini-3.6-flash"

# 会話履歴を保持するリスト
chat_history = []

SYSTEM_PROMPT = "あなたはフレンドリーで親しみやすいAIアシスタントです。丁寧に分かりやすく回答してください。"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI チャット</title>
    <style>
        body { font-family: sans-serif; background: #f4f4f9; padding: 20px; max-width: 600px; margin: 0 auto; }
        h1 { text-align: center; color: #333; }
        .chat-box { background: white; padding: 15px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); min-height: 300px; margin-bottom: 20px; }
        .msg { margin-bottom: 12px; padding: 10px 14px; border-radius: 8px; line-height: 1.5; font-size: 0.95em; }
        .user { background: #e3f2fd; border-left: 4px solid #2196f3; }
        .ai { background: #f1f8e9; border-left: 4px solid #8bc34a; }
        .speaker { font-weight: bold; margin-bottom: 4px; font-size: 0.85em; color: #555; }
        .form-box { display: flex; gap: 10px; }
        input[type="text"] { flex: 1; padding: 12px; border: 1px solid #ccc; border-radius: 6px; font-size: 1em; }
        button { padding: 12px 20px; background: #007bff; color: white; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; }
        button:hover { background: #0056b3; }
        .clear-btn { display: block; text-align: right; margin-bottom: 10px; color: #888; text-decoration: none; font-size: 0.85em; }
    </style>
</head>
<body>
    <h1>🤖 AI チャット</h1>
    <a href="/clear" class="clear-btn">🗑️ 会話をリセット</a>

    <div class="chat-box">
        {% if not history %}
            <p style="text-align: center; color: #aaa;">メッセージを入力してAIとお話ししてみましょう！</p>
        {% endif %}

        {% for chat in history %}
            <div class="msg {{ chat.role }}">
                <div class="speaker">{{ chat.speaker }}</div>
                <div>{{ chat.text }}</div>
            </div>
        {% endfor %}
    </div>

    <form action="/chat" method="post" class="form-box">
        <input type="text" name="message" placeholder="メッセージを入力..." required autofocus>
        <button type="submit">送信</button>
    </form>
</body>
</html>
"""

@app.route("/", methods=["GET", "HEAD"])
def index():
    if request.method == "HEAD":
        return "", 200
    return render_template_string(HTML_TEMPLATE, history=chat_history)

@app.route("/chat", methods=["GET", "POST"])
def chat():
    if request.method == "POST":
        user_msg = request.form.get("message", "").strip()
        
        if user_msg and api_key:
            # ユーザーの発言を追加
            chat_history.append({"speaker": "👤 あなた", "text": user_msg, "role": "user"})
            
            try:
                client = genai.Client(api_key=api_key)
                # AIへ送信して返答を取得
                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=user_msg,
                    config={"system_instruction": SYSTEM_PROMPT}
                )
                ai_reply = response.text
                # AIの発言を追加
                chat_history.append({"speaker": "🤖 AI", "text": ai_reply, "role": "ai"})
            except Exception as e:
                chat_history.append({"speaker": "⚠️ エラー", "text": f"返答を取得できませんでした: {e}", "role": "ai"})
                
        return redirect(url_for("index"))
    
    # GETでアクセスされた場合はTOPへ戻す
    return redirect(url_for("index"))

@app.route("/clear")
def clear():
    """チャット履歴のリセット"""
    chat_history.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
