from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from telegram.bot import router
from config import TELEGRAM_TOKEN

app = FastAPI()
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()
dp.include_router(router)

@app.post("/telegram")
async def telegram_webhook(request: Request):
    data = await request.json()
    update = Update.model_validate(data)
    await dp.feed_update(bot, update)
    return {"ok": True}