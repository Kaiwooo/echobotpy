import logging
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from bitrix.api import send_message, register_user
from config import TELEGRAM_TOKEN

logging.basicConfig(level=logging.INFO)
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

@dp.message()
async def echo_and_send_to_bitrix(message: types.Message):
    # эхо в Telegram
    await message.answer(message.text)

    # формируем external_id для Connector API
    external_id = register_user(message.from_user.id, message.from_user.username or "unknown")

    # отправляем в Bitrix
    send_message(external_id, message.text)
