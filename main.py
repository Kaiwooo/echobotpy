import logging
from fastapi import FastAPI, Request
from telegram.bot import dp, bot
from bitrix.api import bitrix_connector
import asyncio

logging.basicConfig(level=logging.INFO)

app = FastAPI()

@app.post("/bitrix/webhook")
async def bitrix_webhook(request: Request):
    """
    Вебхук, который получает ONAPPINSTALL от Bitrix
    """
    data = await request.json()
    logger = logging.getLogger("bitrix.webhook")
    logger.info(f"Bitrix webhook received: {data}")

    if "auth" in data:
        bitrix_connector.set_auth(data["auth"])
    return {"status": "ok"}


@app.post("/telegram")
async def telegram_webhook(request: Request):
    """
    Вебхук для Telegram
    """
    update = await request.json()
    await dp.feed_update(bot, update)
    return {"status": "ok"}


@app.on_event("startup")
async def startup_event():
    # В FastAPI можно запускать бота через polling, если нет вебхука
    # asyncio.create_task(dp.start_polling(bot))  # если нужен polling
    logging.info("Server started")
