import os
import logging
import requests
from config import BITRIX_REST_URL, CONNECTOR_ID, BITRIX_CLIENT_ID, BITRIX_CLIENT_SECRET

log = logging.getLogger(__name__)

def send_message(external_id: str, message: str):
    """
    Отправка сообщения в открытую линию через Connector API с OAuth авторизацией.
    """
    payload = {
        "ID": external_id,
        "CONNECTOR": CONNECTOR_ID,
        "MESSAGE": message
    }

    headers = {
        "Authorization": f"Bearer {get_access_token()}"
    }

    r = requests.post(f"{BITRIX_REST_URL}/imbot.message.add", json=payload, headers=headers)
    log.info("Bitrix Connector send: %s %s", r.status_code, r.text)
    return r.json()


def get_access_token() -> str:
    """
    Получаем токен приложения через OAuth2 Client Credentials.
    """
    url = "https://oauth.bitrix.info/oauth/token/"
    data = {
        "grant_type": "client_credentials",
        "client_id": BITRIX_CLIENT_ID,
        "client_secret": BITRIX_CLIENT_SECRET
    }
    r = requests.post(url, data=data)
    r.raise_for_status()
    return r.json()["access_token"]
