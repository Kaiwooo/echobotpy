import os
import logging
import requests
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.session.aiohttp import AiohttpSession

# --- Настройки ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # токен вашего Telegram-бота
BITRIX_REST_URL = os.getenv("BITRIX_REST_URL")  # https://b24-.../rest/1/.../
BITRIX_BOT_ID = int(os.getenv("BITRIX_BOT_ID", 0))  # ID бота в Bitrix
BITRIX_LINE_ID = int(os.getenv("BITRIX_LINE_ID", 1))  # ID открытой линии

logging.basicConfig(level=logging.INFO)

# --- Инициализация бота и диспетчера ---
storage = MemoryStorage()
bot = Bot(token=TELEGRAM_TOKEN, session=AiohttpSession())
dp = Dispatcher(storage=storage)

# --- FastAPI приложение ---
app = FastAPI()

# --- Функция для отправки сообщения в Bitrix Open Line ---
def send_to_bitrix(user_id: str, message: str):
    if not BITRIX_REST_URL or not BITRIX_BOT_ID:
        logging.warning("BITRIX_REST_URL или BITRIX_BOT_ID не настроены")
        return
    data = {
        "BOT_ID": BITRIX_BOT_ID,
        "LINE_ID": BITRIX_LINE_ID,
        "MESSAGE": f"{message} (из Telegram @{user_id})"
    }
    try:
        resp = requests.post(f"{BITRIX_REST_URL}/imopenlines.message.add", json=data)
        logging.info(f"Отправка в Bitrix: {resp.status_code} {resp.text}")
    except Exception as e:
        logging.exception("Ошибка при отправке сообщения в Bitrix")

# --- Обработчик входящих сообщений от Telegram ---
@dp.message()
async def echo_message(message: types.Message):
    # 1. Эхо-ответ пользователю
    await message.answer(message.text)
    # 2. Отправка сообщения в Bitrix
    send_to_bitrix(message.from_user.username or str(message.from_user.id), message.text)

# --- Webhook для Telegram ---
@app.post("/telegram")
async def telegram_webhook(request: Request):
    try:
        update = types.Update(**await request.json())
        await dp.feed_update(bot, update)
    except Exception as e:
        logging.exception("Ошибка в webhook Telegram")
    return {"ok": True}

# --- Webhook для Bitrix ---
@app.post("/bitrix")
async def bitrix_webhook(request: Request):
    """
    Обработка сообщений от Bitrix.
    Если оператор пишет пользователю, бот пересылает в Telegram.
    """
    data = await request.json()
    try:
        # проверяем, что это сообщение оператора
        msg = data.get("data", {}).get("PARAMS", {}).get("MESSAGE", "")
        user_id = data.get("data", {}).get("PARAMS", {}).get("USER_ID")
        telegram_username = data.get("data", {}).get("PARAMS", {}).get("UF_TELEGRAM")  # опционально
        if msg and user_id:
            # отправка в Telegram
            try:
                await bot.send_message(chat_id=user_id, text=msg)
            except Exception as e:
                logging.exception(f"Ошибка отправки в Telegram {user_id}")
    except Exception as e:
        logging.exception("Ошибка обработки webhook Bitrix")
    return {"ok": True}

# --- Старт приложения ---
@app.on_event("startup")
async def startup_event():
    logging.info("Приложение стартовало")
