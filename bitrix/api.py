import logging
import requests
from config import BITRIX_REST_URL, CONNECTOR_ID
from storage import bind_chat

log = logging.getLogger(__name__)

def send_message(external_id: str, message: str):
    """
    Отправка сообщения в открытую линию через Connector API.
    Если пользователь еще не существует — Bitrix создаст его автоматически.
    """
    payload = {
        "ID": external_id,
        "CONNECTOR": CONNECTOR_ID,
        "MESSAGE": message
    }
    r = requests.post(f"{BITRIX_REST_URL}/imbot.message.add", json=payload)
    log.info("Bitrix Connector send: %s %s", r.status_code, r.text)
    return r.json()

def register_user(telegram_chat_id: int, username: str) -> str:
    """
    Возвращает external_id для Connector.
    Здесь мы формируем уникальный external_id для Telegram пользователя.
    """
    external_id = f"telegram_{telegram_chat_id}"
    bind_chat(external_id, telegram_chat_id)
    return external_id