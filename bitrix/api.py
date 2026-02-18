import httpx
from config import BITRIX_REST_URL, BITRIX_CONNECTOR_ID

class BitrixAPIError(Exception):
    pass

class BitrixAPI:
    def __init__(self):
        self.rest_url = BITRIX_REST_URL
        self.connector_id = BITRIX_CONNECTOR_ID

    def send_message(self, dialog_id: str, text: str):
        if not self.connector_id:
            raise BitrixAPIError("BITRIX_CONNECTOR_ID not set")

        url = f"{self.rest_url}imconnector.message.add.json"
        payload = {
            "DIALOG_ID": dialog_id,
            "CONNECTOR_ID": self.connector_id,
            "MESSAGE": text
        }

        r = httpx.post(url, data=payload)
        if r.status_code != 200:
            raise BitrixAPIError(f"Bitrix API error {r.status_code}: {r.text}")

        return r.json()