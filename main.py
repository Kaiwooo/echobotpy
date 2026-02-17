import os
import requests
import asyncio
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

# =============================
# ENV переменные
# =============================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BITRIX_WEBHOOK_BASE = os.getenv("BITRIX_WEBHOOK_BASE")  # https://b24-xxx/rest/1/xxxxx
OPENLINE_ID = os.getenv("OPENLINE_ID", "1")  # ID открытой линии
BOT_ID = int(os.getenv("BOT_ID", "21"))  # ID бота в Bitrix

# =============================
# Telegram Bot setup
# =============================
storage = MemoryStorage()
bot = Bot(token=TELEGRAM_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(storage=storage)

# =============================
# FastAPI setup
# =============================
app = FastAPI()

# =============================
# Хранилище связей
# telegram_user_id -> bitrix_chat_id
# =============================
TELEGRAM_CHAT_MAP = {}

# =============================
# Вспомогательная функция для Bitrix
# =============================
def bitrix_call(method: str, data: dict):
    url = f"{BITRIX_WEBHOOK_BASE}/{method}"
    r = requests.post(url, data=data, timeout=10)
    r.raise_for_status()
    return r.json()

# =============================
# 1️⃣ Telegram -> Эхо + Bitrix
# =============================
@dp.message()
async def telegram_echo(message: types.Message):
    user_id = message.from_user.id
    text = message.text

    # 1) Эхо в Telegram
    await message.answer(f"🤖 Эхо: {text}")

    # 2) Отправка в Bitrix Open Lines
    if user_id not in TELEGRAM_CHAT_MAP:
        resp = bitrix_call(
            "im.openlines.chat.start",
            {
                "LINE_ID": OPENLINE_ID,
                "USER_ID": user_id,  # external id для связи
            },
        )
        chat_id = resp.get("result", {}).get("CHAT", {}).get("ID")
        if not chat_id:
            print("Ошибка при создании chat_id в Bitrix:", resp)
            return
        TELEGRAM_CHAT_MAP[user_id] = chat_id
    else:
        chat_id = TELEGRAM_CHAT_MAP[user_id]

    # 3) Отправка сообщения в Open Line
    bitrix_call(
        "im.message.add",
        {
            "CHAT_ID": chat_id,
            "MESSAGE": text,
        },
    )

# =============================
# 2️⃣ FastAPI webhook для Bitrix
# =============================
@app.post("/bitrix/webhook")
async def bitrix_webhook(request: Request):
    payload = await request.json()
    event = payload.get("event")
    data = payload.get("data", {})

    # Только сообщения
    if event != "ONIMBOTMESSAGEADD":
        return {"ok": True}

    message = data.get("MESSAGE", {})
    chat_id = message.get("CHAT_ID")
    text = message.get("TEXT", "")
    author_id = message.get("AUTHOR_ID")

    # Если от оператора → отправляем в Telegram
    if author_id and int(author_id) > 0:
        telegram_user_id = None
        for t_id, c_id in TELEGRAM_CHAT_MAP.items():
            if c_id == chat_id:
                telegram_user_id = t_id
                break
        if telegram_user_id:
            await bot.send_message(telegram_user_id, f"💬 Оператор: {text}")
        else:
            print("Не найден telegram_user_id для chat_id", chat_id)

    return {"ok": True}

# =============================
# 3️⃣ Запуск Telegram polling + FastAPI
# =============================
async def start_polling():
    import logging
    logging.basicConfig(level=logging.INFO)
    from aiogram import executor
    executor.start_polling(dp)

# =============================
# Render запускает FastAPI
# =============================
if __name__ == "__main__":
    import uvicorn
    # Запуск FastAPI на Render
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
