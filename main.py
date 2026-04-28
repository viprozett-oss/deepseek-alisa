import os
from fastapi import FastAPI, Request
import requests

app = FastAPI()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

@app.post("/webhook")
async def webhook(request: Request):
    try:
        body = await request.json()
        user_text = body.get("request", {}).get("original_utterance", "")
        
        if not user_text:
            return {
                "version": "1.0",
                "response": {
                    "text": "Скажи что-нибудь!",
                    "end_session": False
                }
            }
        
        # Максимально быстрый запрос к DeepSeek
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": user_text}],
                "max_tokens": 50,      # Очень короткий ответ
                "temperature": 0.5     # Меньше креатива = быстрее
            },
            timeout=2.5  # Жёсткий таймаут!
        )
        
        if response.status_code == 200:
            data = response.json()
            answer = data["choices"][0]["message"]["content"]
        else:
            answer = f"Ошибка API: {response.status_code}"
            
    except requests.exceptions.Timeout:
        answer = "DeepSeek не успел ответить. Попробуй спросить короче."
    except Exception as e:
        answer = f"Ошибка: {str(e)}"
    
    return {
        "version": "1.0",
        "response": {
            "text": answer,
            "end_session": False
        }
    }
