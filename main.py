import logging
from fastapi import FastAPI, Request
from aiogram import types

from telegram.bot import dp, bot
from bitrix.webhook import handle_bitrix_webhook

logging.basicConfig(level=logging.INFO)

app = FastAPI()


@app.post("/telegram")
async def telegram_webhook(request: Request):
    update = types.Update(**await request.json())
    await dp.feed_update(bot, update)
    return {"ok": True}


@app.post("/bitrix")
async def bitrix_webhook(request: Request):
    return await handle_bitrix_webhook(request)


@app.get("/")
async def health():
    return {"status": "ok"}
