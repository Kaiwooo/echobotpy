import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart

from config import TELEGRAM_TOKEN
from bitrix.api import bitrix_connector

log = logging.getLogger(__name__)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer("Привет! Напиши сообщение — я передам его оператору 👋")


@dp.message()
async def handle_message(message: types.Message):
    """
    1. Отвечаем эхо в Telegram
    2. Отправляем сообщение в Bitrix Open Lines через Connector API
    """
    text = message.text or ""

    # Эхо пользователю
    await message.answer(text)

    # Отправка в Bitrix
    ok = bitrix_connector.send_message(
        external_user_id=str(message.from_user.id),
        text=text,
        user_name=message.from_user.full_name,
    )

    if not ok:
        log.warning("Не удалось отправить сообщение в Bitrix")
