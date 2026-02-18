from fastapi import FastAPI
from bitrix.webhook import handle_bitrix_webhook

app = FastAPI()

@app.post("/bitrix")
async def bitrix_webhook(request):
    return await handle_bitrix_webhook(request)

@app.on_event("startup")
async def startup_event():
    print("Bot app started")