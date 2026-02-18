import logging
from fastapi import Request
from telegram.bot import bot
from storage import get_telegram_chat

log = logging.getLogger(__name__)

async def handle_bitrix_webhook(request: Request):
    payload = await request.json()
    log.info("Bitrix webhook: %s", payload)

    data = payload.get("data", {}).get("PARAMS", {})
    external_id = data.get("USER_ID") or data.get("ID")
    message = data.get("MESSAGE")

    if not external_id or not message:
        return {"ok": True}

    telegram_chat_id = get_telegram_chat(external_id)
    if telegram_chat_id:
        await bot.send_message(telegram_chat_id, message)
    else:
        log.warning("Нет связанного Telegram чата для %s", external_id)

    return {"ok": True}