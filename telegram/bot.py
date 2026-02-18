# telegram/bot.py
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from config import TELEGRAM_TOKEN
from bitrix.api import start_session, send_message
from storage import get_bitrix_chat

log = logging.getLogger(__name__)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


@dp.message()
async def on_message(message: types.Message):
    # 1. Эхо
    await message.answer(message.text)

    telegram_chat_id = message.chat.id
    user_name = message.from_user.username or message.from_user.full_name

    # 2. Проверяем, есть ли уже чат в bitrix
    chat_id = get_bitrix_chat(telegram_chat_id)

    if not chat_id:
        chat_id = start_session(telegram_chat_id, user_name)
        if not chat_id:
            log.warning("Не удалось создать сессию bitrix")
            return

    # 3. Отправляем сообщение оператору
    send_message(chat_id, message.text)
