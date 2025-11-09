import asyncio
from aiogram import Bot, Dispatcher
from cards_bot.config import settings
from cards_bot.database import init_db
from cards_bot.handlers import router
import sys

import logging
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode


dp = Dispatcher()

async def main():
    await init_db()
    bot = Bot(token=settings.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp.include_router(router)
    print("✅ CardsBot запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout)
    asyncio.run(main())
