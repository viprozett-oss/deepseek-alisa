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
                    "text": "Привет! Я DeepSeek. Скажи что-нибудь!",
                    "end_session": False
                }
            }
        
        if not DEEPSEEK_API_KEY:
            return {
                "version": "1.0",
                "response": {
                    "text": "Ошибка: API ключ не настроен. Добавь DEEPSEEK_API_KEY в переменные окружения на Render.",
                    "end_session": True
                }
            }
        
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": user_text}],
                "max_tokens": 100
            },
            timeout=3.0
        )
        
        # Проверяем, что ответ успешный
        if response.status_code == 200:
            data = response.json()
            # Проверяем, что есть поле choices (оно есть только при успехе)
            if "choices" in data and len(data["choices"]) > 0:
                answer = data["choices"][0]["message"]["content"]
            else:
                answer = f"Странный ответ от DeepSeek: {data}"
        else:
            # DeepSeek вернул ошибку
            answer = f"Ошибка от DeepSeek API: {response.status_code} - {response.text[:200]}"
    
    except requests.exceptions.Timeout:
        answer = "DeepSeek не успел ответить. Попробуй спросить короче."
    except Exception as e:
        answer = f"Ошибка: {str(e)[:200]}"
    
    return {
        "version": "1.0",
        "response": {
            "text": answer,
            "end_session": False
        }
    }
