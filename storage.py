# простой пример хранения в памяти (можно заменить на Redis/DB)
chats = {}  # external_id -> telegram_chat_id

def bind_chat(external_id: str, telegram_chat_id: int):
    chats[external_id] = telegram_chat_id

def get_telegram_chat(external_id: str) -> int | None:
    return chats.get(external_id)