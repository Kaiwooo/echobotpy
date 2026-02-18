from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Text
from bitrix.api import bitrix_connector
import logging

logging.basicConfig(level=logging.INFO)

# Ваш Telegram токен
TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

@dp.message()
async def handle_message(message: Message):
    """
    Пересылаем сообщение в Bitrix Open Line
    """
    text = message.text
    dialog_id = f"telegram_{message.from_user.id}"  # Привязка к пользователю Telegram

    try:
        response = bitrix_connector.send_message(dialog_id, text)
        await message.answer(f"Сообщение отправлено в Bitrix: {response}")
    except Exception as e:
        await message.answer(f"Ошибка при отправке: {e}")