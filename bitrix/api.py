import logging
import requests

logger = logging.getLogger("bitrix.api")
logger.setLevel(logging.INFO)

class BitrixAPI:
    def __init__(self):
        # Параметры после установки приложения будут сюда сохраняться
        self.client_endpoint = None
        self.access_token = None
        self.refresh_token = None

    def set_auth(self, auth: dict):
        """
        Сохраняем auth из ONAPPINSTALL
        """
        self.access_token = auth.get("access_token")
        self.refresh_token = auth.get("refresh_token")
        self.client_endpoint = auth.get("client_endpoint")

        logger.info(f"Bitrix auth received: {auth}")

    def send_message(self, dialog_id: str, text: str):
        """
        Отправляем сообщение в Open Lines
        """
        if not self.client_endpoint or not self.access_token:
            raise Exception("Bitrix auth not set")

        url = f"{self.client_endpoint}rest/imopenlines.message.add.json"
        payload = {
            "auth": self.access_token,
            "DIALOG_ID": dialog_id,
            "MESSAGE": text
        }
        r = requests.post(url, json=payload)
        if r.status_code != 200:
            logger.error(f"Bitrix API error {r.status_code}: {r.text}")
            raise Exception(f"Bitrix API error {r.status_code}: {r.text}")
        return r.json()

bitrix_connector = BitrixAPI()