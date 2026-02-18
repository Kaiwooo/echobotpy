from aiogram import Router, types
from aiogram.filters import CommandStart
from bitrix.api import BitrixAPI, BitrixAPIError

router = Router()
bitrix = BitrixAPI()

@router.message(CommandStart())
async def start(message: types.Message):
    await message.answer("Привет! Напишите сообщение — оператор ответит 👋")

@router.message()
async def handle_message(message: types.Message):
    if not message.text:
        return

    # dialog_id в Bitrix = telegram_<chat_id>
    dialog_id = f"telegram_{message.from_user.id}"
    try:
        bitrix.send_message(dialog_id=dialog_id, text=message.text)
        await message.answer("Сообщение отправлено оператору ✅")
    except BitrixAPIError as e:
        await message.answer(f"Ошибка при отправке: {e}")
