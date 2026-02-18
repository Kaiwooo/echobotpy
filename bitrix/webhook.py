import logging
from fastapi import Request
from telegram.bot import bot
from storage import get_telegram_chat

log = logging.getLogger(__name__)


async def handle_bitrix_webhook(request: Request):
    payload = await request.json()
    log.info("Bitrix webhook: %s", payload)

    data = payload.get("data", {}).get("PARAMS", {})
    chat_id = data.get("CHAT_ID")
    message = data.get("MESSAGE")

    if not chat_id or not message:
        return {"ok": True}

    telegram_chat_id = get_telegram_chat(chat_id)
    if not telegram_chat_id:
        log.warning("Нет связанного Telegram чата для %s", chat_id)
        return {"ok": True}

    await bot.send_message(telegram_chat_id, message)
    return {"ok": True}
