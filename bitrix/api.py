import time
import requests
from typing import Optional

from config import (
    BITRIX_REST_URL,
    BITRIX_CLIENT_ID,
    BITRIX_CLIENT_SECRET,
)

class BitrixAPIError(Exception):
    pass


class BitrixAPI:
    def __init__(self):
        self._access_token: Optional[str] = None
        self._refresh_token: Optional[str] = None
        self._expires_at: float = 0.0

    # ================= OAuth =================

    def set_tokens(self, access_token: str, refresh_token: str, expires_in: int):
        self._access_token = access_token
        self._refresh_token = refresh_token
        self._expires_at = time.time() + expires_in - 30

    def _token_expired(self) -> bool:
        return not self._access_token or time.time() >= self._expires_at

    def _refresh_access_token(self):
        if not self._refresh_token:
            raise BitrixAPIError("Refresh token is missing")

        r = requests.post(
            "https://oauth.bitrix.info/oauth/token/",
            data={
                "grant_type": "refresh_token",
                "client_id": BITRIX_CLIENT_ID,
                "client_secret": BITRIX_CLIENT_SECRET,
                "refresh_token": self._refresh_token,
            },
            timeout=10,
        )

        if r.status_code != 200:
            raise BitrixAPIError(f"OAuth refresh error {r.status_code}: {r.text}")

        data = r.json()
        self.set_tokens(
            access_token=data["access_token"],
            refresh_token=data["refresh_token"],
            expires_in=int(data["expires_in"]),
        )

    def _get_access_token(self) -> str:
        if self._token_expired():
            self._refresh_access_token()
        return self._access_token

    # ================= REST =================

    def _headers(self):
        return {
            "Authorization": f"Bearer {self._get_access_token()}",
            "Content-Type": "application/json",
        }

    def call(self, method: str, payload: dict):
        url = f"{BITRIX_REST_URL.rstrip('/')}/{method}"
        r = requests.post(url, json=payload, headers=self._headers(), timeout=10)

        if r.status_code != 200:
            raise BitrixAPIError(f"REST error {r.status_code}: {r.text}")

        data = r.json()
        if "error" in data:
            raise BitrixAPIError(str(data))

        return data.get("result")

    # ================= IM BOT =================

    def send_message(self, dialog_id: str, text: str):
        """
        dialog_id = telegram_<telegram_user_id>
        Bitrix сам:
        - создаёт чат
        - кладёт его в открытую линию
        - назначает оператора
        """
        return self.call(
            "imbot.message.add",
            {
                "DIALOG_ID": dialog_id,
                "MESSAGE": text,
            },
        )