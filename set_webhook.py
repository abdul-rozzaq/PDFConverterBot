import sys
import asyncio

from aiogram import Bot

from src.core import settings


async def main():
    domain = sys.argv[1]
    bot_id = settings.BOT_TOKEN.split(":", maxsplit=1)[0]

    url = f"{domain}/telegram/webhook/{bot_id}"

    try:
        bot = Bot(token=settings.BOT_TOKEN)
        await bot.set_webhook(url)
        data = await bot.get_me()

        print("Set webhook successful", f"http://t.me/{data.username}")

    except Exception as e:
        print("Set webhook error", str(e))


if __name__ == "__main__":
    asyncio.run(main())
