from aiogram import Router, types
from aiogram.filters import CommandStart

from bitrix.api import BitrixAPI

router = Router()
bitrix = BitrixAPI()

# ⚠️ один раз положи реальные токены
# (обычно читаются из БД или env после первичной OAuth-авторизации)
bitrix.set_tokens(
    access_token="ACCESS_TOKEN",
    refresh_token="REFRESH_TOKEN",
    expires_in=3600,
)


@router.message(CommandStart())
async def start(message: types.Message):
    await message.answer("Привет! Напишите сообщение — оператор ответит 👋")


@router.message()
async def handle_message(message: types.Message):
    if not message.text:
        return

    dialog_id = f"telegram_{message.from_user.id}"

    bitrix.send_message(
        dialog_id=dialog_id,
        text=message.text,
    )

    await message.answer("Сообщение отправлено оператору ✅")
