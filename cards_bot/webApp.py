import asyncio
import logging
import sys
from os import getenv
from dotenv import load_dotenv
import os 


from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

load_dotenv()

# Bot token can be obtained via https://t.me/BotFather
TOKEN = "6071831153:AAF6Vqo-sFQ48KTeGKogOcnNfRgVGzUh9Jc"

# All handlers should be attached to the Router (or Dispatcher)

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer('Hello!')

@dp.message(Command('google'))
async def command_google_handler(message: Message) -> None:
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton( 
                    text='Open',
                    web_app=WebAppInfo(url='https://adam-01010.github.io/webApp.github.io/'),
                )
            ]
        ]
    )
    await message.answer('Start', reply_markup=markup)


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        stream=sys.stdout)
    asyncio.run(main())
        