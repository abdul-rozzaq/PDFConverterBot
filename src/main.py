from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.bot import feed_update


from .core import settings

app = FastAPI(title="PDF Convertor bot")


@app.post("/telegram/webhook/{bot_id}")
async def webhook(request: Request, bot_id: str):

    if bot_id != settings.BOT_TOKEN.split(":", maxsplit=1)[0]:
        return JSONResponse({"detail": "Bot ID is invalid"}, status=status.HTTP_400_BAD_REQUEST)

    update = await request.json()

    try:
        await feed_update(update)
    except Exception as e:
        print(str(e))

    return {"status": "ok"}
