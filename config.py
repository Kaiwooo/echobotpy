import os

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BITRIX_WEBHOOK_SECRET = os.getenv("BITRIX_WEBHOOK_SECRET")  # секрет для проверки
BITRIX_REST_URL = os.getenv("BITRIX_REST_URL")  # https://b24-.../rest/1/.../