from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from bitrix.connector import send_message
from config import TELEGRAM_TOKEN

storage = MemoryStorage()
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(storage=storage)

CONNECTOR_ID = "your_connector_id"  # ID твоего Connector API в Bitrix

@dp.message()
async def echo_and_forward(message: types.Message):
    # 1. Эхо в Telegram
    await message.answer(message.text)
    # 2. Отправка в Bitrix через Connector API
    user_id = f"telegram_{message.from_user.id}"
    send_message(CONNECTOR_ID, user_id, message.text)