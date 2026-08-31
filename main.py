import os
import time
import threading
from datetime import datetime
from flask import Flask, render_template_string, request
from google import genai
from pymongo import MongoClient

app = Flask(__name__)

# Render環境変数
api_key = os.environ.get("ARUPAKA_KEY")
mongo_uri = os.environ.get("MONGO_URI")

MODEL_NAME = "gemini-2.5-flash"

# MongoDBの接続設定
db_client = None
chat_collection = None

if mongo_uri:
    try:
        db_client = MongoClient(mongo_uri)
        # 「aidb」というデータベースの「logs」コレクションを使用
        db = db_client["aidb"]
        chat_collection = db["logs"]
        print("MongoDBへの接続に成功しました！")
    except Exception as e:
        print(f"MongoDB接続エラー: {e}")

SYSTEM_PROMPT_A = "あなたはポジティブで元気なAIロボットです。短く返答してください。"
SYSTEM_PROMPT_B = "あなたは少し皮肉屋で冷静なAIです。相手の言葉に短くツッコミを入れてください。"

def run_ai_conversation():
    """10分ごとに自動実行され、会話を生成してMongoDBに保存する関数"""
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

        time.sleep(2)

        # AI_Aの返答
        response_a = client.models.generate_content(
            model=MODEL_NAME,
            contents=reply_b,
            config={"system_instruction": SYSTEM_PROMPT_A}
        )
        reply_a = response_a.text
        new_logs.append({"speaker": "🤖 AI_A", "text": reply_a, "css_class": "ai-a"})

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        doc = {
            "timestamp": timestamp,
            "logs": new_logs,
            "created_at": datetime.now()
        }

        # MongoDBにデータを保存
        if chat_collection is not None:
            chat_collection.insert_one(doc)
            print(f"[{timestamp}] 会話データをMongoDBに保存しました！")
        else:
            print("MongoDBに接続されていないため、保存をスキップしました。")

    except Exception as e:
        print(f"自動会話エラー: {e}")

def start_scheduler():
    """10分（600秒）ごとに会話生成をループ実行"""
    run_ai_conversation()
    while True:
        time.sleep(160)  # 10分待機

# バックグラウンドタイマー開始
threading.Thread(target=start_scheduler, daemon=True).start()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="60">
    <title>AI vs AI </title>
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
    <h1>🤖 AI × 🧐 AI　（アルパカ:五分ごとに更新来るからよろしく。 ）</h1>
    <div class="info">（60秒ごとに更新）</div>
    
    {% if not history %}
        <div class="session">ログを取得中、または会話データがまだありません...</div>
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

    history = []
    # MongoDBから新しい順に過去30件の会話を取得
    if chat_collection is not None:
        try:
            records = chat_collection.find().sort("created_at", -1).limit(30)
            history = list(records)
        except Exception as e:
            print(f"MongoDB取得エラー: {e}")

    return render_template_string(HTML_TEMPLATE, history=history)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
