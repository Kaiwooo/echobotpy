# bitrix/api.py
import logging
import requests
from typing import Optional

from config import (
    BITRIX_REST_URL,
    CONNECTOR_ID,
    BITRIX_CLIENT_ID,
    BITRIX_CLIENT_SECRET,
)

log = logging.getLogger("bitrix.api")


class BitrixAPIError(Exception):
    pass


class BitrixConnectorAPI:
    """
    Работа с Bitrix24 OpenLines Connector API
    """

    def __init__(self):
        self._access_token: Optional[str] = None

    # ---------- OAuth ----------

    def _get_access_token(self) -> str:
        """
        Получение OAuth access_token для приложения Bitrix24
        """
        if self._access_token:
            return self._access_token

        if not BITRIX_CLIENT_ID or not BITRIX_CLIENT_SECRET:
            raise BitrixAPIError("BITRIX_CLIENT_ID / BITRIX_CLIENT_SECRET not set")

        url = "https://oauth.bitrix.info/oauth/token/"
        data = {
            "grant_type": "client_credentials",
            "client_id": BITRIX_CLIENT_ID,
            "client_secret": BITRIX_CLIENT_SECRET,
        }

        r = requests.post(url, data=data, timeout=10)
        if r.status_code != 200:
            raise BitrixAPIError(f"OAuth error {r.status_code}: {r.text}")

        payload = r.json()
        self._access_token = payload["access_token"]
        return self._access_token

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Content-Type": "application/json",
        }

    # ---------- Connector API ----------

    def send_message(
        self,
        external_user_id: str,
        text: str,
        user_name: str = "Telegram user",
    ) -> dict:
        """
        Отправка сообщения В открытую линию Bitrix24

        external_user_id — стабильный ID (например telegram user_id)
        """
        if not BITRIX_REST_URL:
            raise BitrixAPIError("BITRIX_REST_URL not set")

        if not CONNECTOR_ID:
            raise BitrixAPIError("BITRIX_CONNECTOR_ID not set")

        url = f"{BITRIX_REST_URL}imconnector.send.messages"

        payload = {
            "CONNECTOR": CONNECTOR_ID,
            "LINE": CONNECTOR_ID,
            "MESSAGES": [
                {
                    "user": {
                        "id": external_user_id,
                        "name": user_name,
                    },
                    "message": {
                        "text": text
                    }
                }
            ]
        }

        r = requests.post(
            url,
            json=payload,
            headers=self._headers(),
            timeout=10,
        )

        log.info("Bitrix Connector send: %s %s", r.status_code, r.text)

        if r.status_code == 401:
            # токен протух — пробуем обновить
            self._access_token = None
            return self.send_message(external_user_id, text, user_name)

        if r.status_code != 200:
            raise BitrixAPIError(f"Bitrix error {r.status_code}: {r.text}")

        return r.json()


# singleton
bitrix_connector = BitrixConnectorAPI()
