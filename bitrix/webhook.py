import logging
from fastapi import Request
from telegram.bot import bot

log = logging.getLogger(__name__)


async def handle_bitrix_webhook(request: Request):
    """
    Webhook от Bitrix для нового сообщения в открытой линии
    """
    data = await request.json()
    log.info("Bitrix connector webhook: %s", data)

    event = data.get("event")
    params = data.get("data", {}).get("PARAMS", {})

    if event == "ONIMCONNECTORRECEIVE" and params.get("MESSAGE"):
        user_id = params.get("USER_ID")  # Bitrix user ID
        message = params.get("MESSAGE")
        telegram_chat_id = params.get("UF_TELEGRAM")  # связанный Telegram chat_id

        if telegram_chat_id:
            try:
                await bot.send_message(chat_id=telegram_chat_id, text=message)
            except Exception:
                log.exception("Ошибка отправки в Telegram")

    return {"ok": True}