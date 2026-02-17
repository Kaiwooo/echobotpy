import os
import requests
from fastapi import FastAPI, Request

app = FastAPI()

# Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# Bitrix REST
BITRIX_REST_URL = os.getenv("BITRIX_REST_URL")  # https://your.bitrix24.ru/rest/1/xxx/
BOT_ID = os.getenv("BOT_ID")                     # id бота, который в Open Lines зарегистрирован

# Простое хранение соответствия telegram_user_id <-> bitrix_chat_id
CHAT_MAP = {}

@app.post("/telegram")
async def telegram_webhook(request: Request):
    """Обработка сообщений из Telegram"""
    update = await request.json()
    if "message" not in update:
        return {"status": "ignored"}

    message = update["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "")

    if not text:
        return {"status": "ignored"}

    # Проверяем есть ли уже чат с Open Lines
    bitrix_chat_id = CHAT_MAP.get(chat_id)
    if not bitrix_chat_id:
        # создаем чат через imopenlines.message.add
        bitrix_chat_id = create_openlines_chat(text)
        CHAT_MAP[chat_id] = bitrix_chat_id

    # Отправляем сообщение клиента в Open Lines
    send_to_openlines(bitrix_chat_id, text)

    return {"status": "ok"}


@app.post("/bitrix")
async def bitrix_webhook(request: Request):
    """Обработка входящих событий из Bitrix"""
    data = await request.json()
    payload = data.get("data", {})

    author_id = str(payload.get("AUTHOR_ID", ""))
    dialog_id = payload.get("DIALOG_ID")
    message = payload.get("MESSAGE", "")

    # Игнорируем сообщения оператора
    if author_id != "0":
        return {"status": "operator_ignored"}

    # Можно сюда добавить логи или отправку в Telegram, если нужно
    print(f"Клиент написал в Open Lines: {message}")
    return {"status": "ok"}


def create_openlines_chat(initial_message: str):
    """Создать чат в Open Lines и вернуть chat_id"""
    url = f"{BITRIX_REST_URL}/imopenlines.message.add"
    payload = {
        "BOT_ID": BOT_ID,
        "MESSAGE": initial_message
    }
    r = requests.post(url, json=payload)
    res = r.json()
    # возвращаем chat_id для дальнейших сообщений
    return res.get("result", {}).get("CHAT_ID")


def send_to_openlines(chat_id, text):
    url = f"{BITRIX_REST_URL}/imopenlines.message.add"
    payload = {
        "BOT_ID": BOT_ID,
        "DIALOG_ID": chat_id,
        "MESSAGE": text
    }
    r = requests.post(url, json=payload)
    print("SEND TO OPEN LINES:", r.text)
