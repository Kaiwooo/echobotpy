import logging
import requests
from config import BITRIX_REST_URL, BITRIX_LINE_ID
from storage import bind_chats

log = logging.getLogger(__name__)


def start_session(telegram_chat_id: int, user_name: str) -> str | None:
    """
    Создаем диалог в открытой линии
    """
    payload = {
        "LINE_ID": BITRIX_LINE_ID,
        "USER": {
            "NAME": user_name,
            "EXTERNAL_ID": f"telegram_{telegram_chat_id}",
        }
    }

    r = requests.post(f"{BITRIX_REST_URL}/imopenlines.session.start", json=payload)
    log.info("Создание сессии: %s %s", r.status_code, r.text)

    if r.status_code != 200 or "result" not in r.json():
        return None

    session_id = r.json()["result"]["SESSION_ID"]
    chat_id = r.json()["result"]["CHAT_ID"]

    bind_chats(telegram_chat_id, chat_id)
    return chat_id


def send_message(chat_id: str, text: str):
    payload = {
        "CHAT_ID": chat_id,
        "MESSAGE": text,
    }

    r = requests.post(f"{BITRIX_REST_URL}/imopenlines.message.send", json=payload)
    log.info("Сообщение в bitrix: %s %s", r.status_code, r.text)
