import os
import asyncio
import requests
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode
from aiogram.utils import executor

# =============================
# Environment
# =============================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BITRIX_WEBHOOK_BASE = os.getenv("BITRIX_WEBHOOK_BASE")  # пример: https://b24-xxx/rest/1/xxxxx
OPENLINE_ID = os.getenv("OPENLINE_ID", "1")  # ID открытой линии в Bitrix
BOT_ID = int(os.getenv("BOT_ID", "21"))  # ID бота в Bitrix

# =============================
# Telegram Bot setup
# =============================
bot = Bot(token=TELEGRAM_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())

# =============================
# FastAPI setup
# =============================
app = FastAPI()

# =============================
# Простое хранилище связей
# Telegram user_id <-> Bitrix chat_id
# =============================
TELEGRAM_CHAT_MAP = {}  # telegram_user_id -> bitrix_chat_id

# =============================
# Вспомогательная функция Bitrix
# =============================
def bitrix_call(method: str, data: dict):
    url = f"{BITRIX_WEBHOOK_BASE}/{method}"
    r = requests.post(url, data=data, timeout=10)
    r.raise_for_status()
    return r.json()

# =============================
# 1️⃣ Telegram -> эхо + Bitrix
# =============================
@dp.message_handler()
async def telegram_echo(message: types.Message):
    user_id = message.from_user.id
    text = message.text

    # 1) Эхо в Telegram
    await message.answer(f"🤖 Эхо: {text}")

    # 2) Отправка в Bitrix Open Lines
    # Если ещё нет chat_id — создаём новый
    if user_id not in TELEGRAM_CHAT_MAP:
        resp = bitrix_call(
            "im.openlines.chat.start",
            {
                "LINE_ID": OPENLINE_ID,
                "USER_ID": user_id,  # можно использовать как external id
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

    # фильтруем только сообщения
    if event != "ONIMBOTMESSAGEADD":
        return {"ok": True}

    message = data.get("MESSAGE", {})
    chat_id = message.get("CHAT_ID")
    text = message.get("TEXT", "")
    author_id = message.get("AUTHOR_ID")

    # если сообщение от оператора — отправляем в Telegram
    if author_id and int(author_id) > 0:
        # ищем telegram_user_id по chat_id
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
# 3️⃣ FastAPI + aiogram run
# =============================
async def start():
    # запускаем aiogram polling
    loop = asyncio.get_event_loop()
    from aiogram import executor as ag_executor

    ag_executor.start_polling(dp, loop=loop)

# =============================
# Если Render запускает FastAPI напрямую
# =============================
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
