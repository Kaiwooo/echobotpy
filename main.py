import os
import logging
import requests
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.client.bot import DefaultBotProperties
from aiogram.dispatcher.fsm.storage.memory import MemoryStorage

# ---------------- CONFIG ----------------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BITRIX_REST_URL = os.getenv("BITRIX_REST_URL")  # пример: https://b24-xxx.bitrix24.ru/rest/1/a10zktt7n91vljxn/
BITRIX_BOT_ID = os.getenv("BITRIX_BOT_ID")      # id бота в Bitrix Open Line
BITRIX_LINE_ID = os.getenv("BITRIX_LINE_ID")    # id вашей открытой линии

logging.basicConfig(level=logging.INFO)

# ---------------- INIT ----------------
bot = Bot(
    token=TELEGRAM_TOKEN,
    default=DefaultBotProperties(parse_mode="HTML")
)
dp = Dispatcher(storage=MemoryStorage())
app = FastAPI()

# ---------------- TELEGRAM WEBHOOK ----------------
@app.post("/telegram")
async def telegram_webhook(request: Request):
    """
    Входящие сообщения от Telegram
    """
    try:
        update = types.Update(**await request.json())
        if update.message:
            user_id = update.message.from_user.id
            text = update.message.text or ""
            
            # Эхо
            await bot.send_message(chat_id=user_id, text=text)

            # Отправка в Bitrix Open Line
            bitrix_payload = {
                "BOT_ID": BITRIX_BOT_ID,
                "LINE_ID": BITRIX_LINE_ID,
                "MESSAGE": text,
                "USER_ID": user_id,  # чтобы оператор мог видеть, кому писать
            }
            bitrix_resp = requests.post(
                f"{BITRIX_REST_URL}imopenlines.crm.message.add.json",
                json=bitrix_payload
            )
            logging.info(f"Bitrix response: {bitrix_resp.text}")

        return {"ok": True}
    except Exception as e:
        logging.error(f"Telegram webhook error: {e}")
        return {"ok": False, "error": str(e)}

# ---------------- BITRIX WEBHOOK ----------------
@app.post("/bitrix")
async def bitrix_webhook(request: Request):
    """
    Входящие сообщения от Bitrix Open Lines (оператор → Telegram)
    """
    try:
        data = await request.json()
        logging.info(f"Incoming Bitrix message: {data}")

        telegram_user_id = int(data.get("USER_ID") or data.get("CHAT_ID"))
        text = data.get("MESSAGE")

        if telegram_user_id and text:
            await bot.send_message(chat_id=telegram_user_id, text=text)
            return {"ok": True}
        else:
            return {"ok": False, "error": "Missing USER_ID or MESSAGE"}
    except Exception as e:
        logging.error(f"Bitrix webhook error: {e}")
        return {"ok": False, "error": str(e)}

# ---------------- STARTUP/SHUTDOWN ----------------
@app.on_event("startup")
async def on_startup():
    logging.info("Bot started")

@app.on_event("shutdown")
async def on_shutdown():
    await bot.session.close()
    logging.info("Bot stopped")
