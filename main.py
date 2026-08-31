import os
import time
import threading
from datetime import datetime
from flask import Flask, render_template_string, request
from google import genai

app = Flask(__name__)

# Renderの環境変数から API KEY (ARUPAKA_KEY) を取得
api_key = os.environ.get("ARUPAKA_KEY")
MODEL_NAME = "gemini-2.5-flash"

# 会話履歴を保持するメモリ（リスト）
conversation_history = []

SYSTEM_PROMPT_A = "あなたはポジティブで元気なAIロボットです。短く返答してください。"
SYSTEM_PROMPT_B = "あなたは少し皮肉屋で冷静なAIです。相手の言葉に短くツッコミを入れてください。"

def run_ai_conversation():
    """10分ごとにバックグラウンドで呼び出される会話生成処理"""
    global conversation_history
    if not api_key:
        print("API KEYが設定されていません。")
        return

    try:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 自動会話生成スタート...")
        client = genai.Client(api_key=api_key)
        
        current_message = "やあ！最近何か面白いことあった？"
        new_logs = []
        new_logs.append({"speaker": "🤖 AI_A", "text": current_message, "css_class": "ai-a"})

        # AI_Bの返答
        response_b = client.models.generate_content(
            model=MODEL_NAME,
            contents=current_message,
            config={"system_instruction": SYSTEM_PROMPT_B}
        )
        reply_b = response_b.text
        new_logs.append({"speaker": "🧐 AI_B", "text": reply_b, "css_class": "ai-b"})

        time.sleep(2) # 負荷軽減のためのウェイト

        # AI_Aの返答
        response_a = client.models.generate_content(
            model=MODEL_NAME,
            contents=reply_b,
            config={"system_instruction": SYSTEM_PROMPT_A}
        )
        reply_a = response_a.text
        new_logs.append({"speaker": "🤖 AI_A", "text": reply_a, "css_class": "ai-a"})

        # 新しい会話を履歴の先頭に追加
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        conversation_history.insert(0, {"timestamp": timestamp, "logs": new_logs})
        
        # 履歴が大きくなりすぎないよう最新10回分だけ保持
        conversation_history = conversation_history[:10]
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 会話生成完了！")

    except Exception as e:
        print(f"自動会話エラー: {e}")

def start_scheduler():
    """10分（600秒）ごとに自動実行するループタイマー"""
    # 起動直後にまず1回実行
    run_ai_conversation()
    while True:
        time.sleep(600)  # 10分待機 (600秒)
        run_ai_conversation()

# バックグラウンドでタイマーを起動
threading.Thread(target=start_scheduler, daemon=True).start()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="60"> <!-- 60秒ごとにページを自動更新 -->
    <title>AI vs AI</title>
    <style>
        body { font-family: sans-serif; background: #f4f4f9; padding: 20px; max-width: 600px; margin: 0 auto; }
        h1 { text-align: center; color: #333; font-size: 1.5em; }
        .info { text-align: center; color: #666; font-size: 0.85em; margin-bottom: 20px; }
        .session { background: white; padding: 15px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 20px; }
        .time { font-size: 0.8em; color: #888; font-weight: bold; border-bottom: 1px solid #eee; padding-bottom: 5px; margin-bottom: 10px; }
        .msg { margin-bottom: 10px; padding: 8px 12px; border-radius: 8px; line-height: 1.4; font-size: 0.95em; }
        .ai-a { background: #e3f2fd; border-left: 4px solid #2196f3; }
        .ai-b { background: #ffebee; border-left: 4px solid #f44336; }
        .speaker { font-weight: bold; margin-bottom: 3px; font-size: 0.85em; }
    </style>
</head>
<body>
    <h1>🤖 AI × 🧐 AI 自動ラジオ</h1>
    <div class="info">10分ごとに自動で新しい会話が生成されます（画面は1分ごとに自動更新）</div>
    
    {% if not history %}
        <div class="session">最初の会話を生成中です...少々お待ちください。</div>
    {% endif %}

    {% for session in history %}
        <div class="session">
            <div class="time">🕒 {{ session.timestamp }}</div>
            {% for chat in session.logs %}
                <div class="msg {{ chat.css_class }}">
                    <div class="speaker">{{ chat.speaker }}</div>
                    <div>{{ chat.text }}</div>
                </div>
            {% endfor %}
        </div>
    {% endfor %}
</body>
</html>
"""

@app.route("/", methods=["GET", "HEAD"])
def index():
    if request.method == "HEAD":
        return "", 200
    return render_template_string(HTML_TEMPLATE, history=conversation_history)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
