import os
import logging
import requests
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.session.aiohttp import AiohttpSession

# --- Настройки ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # токен Telegram-бота
BITRIX_REST_URL = os.getenv("BITRIX_REST_URL")  # https://b24-.../rest/1/.../
BITRIX_LINE_ID = int(os.getenv("BITRIX_LINE_ID", 1))  # ID открытой линии

logging.basicConfig(level=logging.INFO)

# --- Инициализация бота и диспетчера ---
storage = MemoryStorage()
bot = Bot(token=TELEGRAM_TOKEN, session=AiohttpSession())
dp = Dispatcher(storage=storage)

# --- FastAPI приложение ---
app = FastAPI()

# --- Хранилище SESSION_ID для пользователей ---
USER_SESSIONS = {}  # user_id -> session_id

# --- Функция для отправки сообщения в Bitrix Open Line ---
def send_to_bitrix(user_id: str, message: str):
    """
    1. Если сессия для пользователя есть, отправляем сообщение через bot.session.message.send
    2. Иначе создаём сессию через message.session.start, сохраняем SESSION_ID и отправляем
    """
    if not BITRIX_REST_URL:
        logging.warning("BITRIX_REST_URL не настроен")
        return

    session_id = USER_SESSIONS.get(user_id)

    if not session_id:
        # Создаём новую сессию
        data = {
            "LINE_ID": BITRIX_LINE_ID,
            "EXTERNAL_USER_ID": user_id,
            "MESSAGE": message
        }
        try:
            resp = requests.post(f"{BITRIX_REST_URL}/imopenlines.message.session.start.json", json=data)
            resp_json = resp.json()
            logging.info(f"Создание сессии: {resp.status_code} {resp.text}")
            if "result" in resp_json and "SESSION_ID" in resp_json["result"]:
                session_id = resp_json["result"]["SESSION_ID"]
                USER_SESSIONS[user_id] = session_id
            else:
                logging.warning(f"Не удалось получить SESSION_ID для {user_id}")
                return
        except Exception as e:
            logging.exception("Ошибка при создании сессии Bitrix")
            return

    # Отправка сообщения через bot.session.message.send
    try:
        send_data = {
            "SESSION_ID": session_id,
            "MESSAGE": message
        }
        resp = requests.post(f"{BITRIX_REST_URL}/imopenlines.bot.session.message.send.json", json=send_data)
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
        # проверяем сообщение от оператора
        params = data.get("data", {}).get("PARAMS", {})
        msg = params.get("MESSAGE")
        external_user_id = params.get("EXTERNAL_USER_ID")  # user_id Telegram
        if msg and external_user_id:
            try:
                await bot.send_message(chat_id=external_user_id, text=msg)
            except Exception as e:
                logging.exception(f"Ошибка отправки в Telegram {external_user_id}")
    except Exception as e:
        logging.exception("Ошибка обработки webhook Bitrix")
    return {"ok": True}

# --- Старт приложения ---
@app.on_event("startup")
async def startup_event():
    logging.info("Приложение стартовало")
