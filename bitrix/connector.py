import requests
import logging
from config import BITRIX_REST_URL

log = logging.getLogger(__name__)

def send_message(connector_id: str, user_id: str, text: str):
    """
    Отправка сообщения через Connector API
    """
    payload = {
        "ID": user_id,          # ID пользователя Bitrix24 в открытой линии
        "CONNECTOR": connector_id,
        "MESSAGE": text
    }

    url = f"{BITRIX_REST_URL}/imconnector.message.send"
    try:
        r = requests.post(url, json=payload)
        log.info("Bitrix connector send: %s %s", r.status_code, r.text)
        return r.json()
    except Exception as e:
        log.exception("Ошибка отправки в Bitrix Connector")
        return None
