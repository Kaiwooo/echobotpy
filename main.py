from fastapi import FastAPI, Request
from telegram.bot import dp, bot
from bitrix.webhook import handle_bitrix_webhook
from aiogram.types import Update
import logging

logging.basicConfig(level=logging.INFO)
app = FastAPI()

# Telegram webhook
@app.post("/telegram")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update(**data)
    await dp.feed_update(bot, update)
    return {"ok": True}

# Bitrix webhook
@app.post("/bitrix")
async def bitrix_webhook(request: Request):
    return await handle_bitrix_webhook(request)

@app.on_event("startup")
async def startup_event():
    logging.info("Приложение стартовало")
