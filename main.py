import os
from flask import Flask, render_template_string, request, redirect, url_for
from groq import Groq

app = Flask(__name__)

api_key = os.environ.get("GROQ_API_KEY")
MODEL_NAME = "llama-3.3-70b-versatile"

chat_history = []
SYSTEM_PROMPT = "あなたはフレンドリーで親しみやすいAIアシスタントです。日本語で丁寧に分かりやすく回答してください。"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Groq AI チャット</title>
    <style>
        body { font-family: sans-serif; background: #f4f4f9; padding: 20px; max-width: 600px; margin: 0 auto; }
        h1 { text-align: center; color: #333; }
        .chat-box { background: white; padding: 15px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); min-height: 300px; margin-bottom: 20px; }
        .msg { margin-bottom: 12px; padding: 10px 14px; border-radius: 8px; line-height: 1.5; font-size: 0.95em; }
        .user { background: #e3f2fd; border-left: 4px solid #2196f3; }
        .ai { background: #f1f8e9; border-left: 4px solid #8bc34a; }
        .error-msg { background: #ffebee; border-left: 4px solid #f44336; color: #c62828; }
        .speaker { font-weight: bold; margin-bottom: 4px; font-size: 0.85em; color: #555; }
        .form-box { display: flex; gap: 10px; }
        input[type="text"] { flex: 1; padding: 12px; border: 1px solid #ccc; border-radius: 6px; font-size: 1em; }
        button { padding: 12px 20px; background: #007bff; color: white; border: none; border-radius: 6px; font-weight: bold; cursor: pointer; }
        button:hover { background: #0056b3; }
        button:disabled { background: #cccccc; cursor: not-allowed; }
        .clear-btn { display: block; text-align: right; margin-bottom: 10px; color: #888; text-decoration: none; font-size: 0.85em; }
    </style>
</head>
<body>
    <h1>⚡ Groq AI チャット</h1>
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

    <form action="/chat" method="post" class="form-box" onsubmit="preventDoubleSubmit(this)">
        <input type="text" id="msgInput" name="message" placeholder="メッセージを入力..." required autofocus>
        <button type="submit" id="submitBtn">送信</button>
    </form>

    <script>
        function preventDoubleSubmit(form) {
            const btn = document.getElementById('submitBtn');
            const input = document.getElementById('msgInput');
            btn.disabled = true;
            btn.innerText = '送信中...';
            input.readOnly = true;
        }
    </script>
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
            chat_history.append({"speaker": "👤 あなた", "text": user_msg, "role": "user"})
            
            try:
                client = Groq(api_key=api_key)
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_msg}
                    ]
                )
                ai_reply = response.choices[0].message.content
                chat_history.append({"speaker": "🤖 AI", "text": ai_reply, "role": "ai"})
            except Exception as e:
                chat_history.append({"speaker": "⚠️ システム", "text": f"エラーが発生しました: {e}", "role": "error-msg"})
                
        return redirect(url_for("index"))
    
    return redirect(url_for("index"))

@app.route("/clear")
def clear():
    chat_history.clear()
    return redirect(url_for("index"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
