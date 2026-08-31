import os
import time
from google import genai

# Renderの環境変数から API KEY (ARUPAKA_KEY) を取得
api_key = os.environ.get("ARUPAKA_KEY")
client = genai.Client(api_key=api_key)

MODEL_NAME = "gemini-2.5-flash"

# AIのキャラクター設定
SYSTEM_PROMPT_A = "あなたはポジティブで元気なAIロボットです。短く返答してください。"
SYSTEM_PROMPT_B = "あなたは少し皮肉屋で冷静なAIです。相手の言葉に短くツッコミを入れてください。"

chat_history_a = []
chat_history_b = []

current_message = "やあ！今日は何をして遊ぶ？"
print(f"🤖 AI_A: {current_message}", flush=True)

# 交互に5ターン会話
for i in range(5):
    time.sleep(2)
    # AI_Bの返答
    chat_history_b.append({"role": "user", "parts": [{"text": current_message}]})
    response_b = client.models.generate_content(
        model=MODEL_NAME,
        contents=chat_history_b,
        config={"system_instruction": SYSTEM_PROMPT_B}
    )
    reply_b = response_b.text
    print(f"🧐 AI_B: {reply_b}", flush=True)
    chat_history_b.append({"role": "model", "parts": [{"text": reply_b}]})

    time.sleep(2)
    # AI_Aの返答
    chat_history_a.append({"role": "user", "parts": [{"text": reply_b}]})
    response_a = client.models.generate_content(
        model=MODEL_NAME,
        contents=chat_history_a,
        config={"system_instruction": SYSTEM_PROMPT_A}
    )
    current_message = response_a.text
    print(f"🤖 AI_A: {current_message}", flush=True)
    chat_history_a.append({"role": "model", "parts": [{"text": current_message}]})

print("--- 会話終了 ---", flush=True)
