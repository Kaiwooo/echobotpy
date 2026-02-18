# MVP: in-memory storage
# telegram_chat_id -> bitrix_chat_id

telegram_to_bitrix = {}
bitrix_to_telegram = {}


def bind_chats(telegram_chat_id: int, bitrix_chat_id: str):
    telegram_to_bitrix[telegram_chat_id] = bitrix_chat_id
    bitrix_to_telegram[bitrix_chat_id] = telegram_chat_id

def get_bitrix_chat(telegram_chat_id: int):
    return telegram_to_bitrix.get(telegram_chat_id)

def get_telegram_chat(bitrix_chat_id: str):
    return bitrix_to_telegram.get(bitrix_chat_id)
