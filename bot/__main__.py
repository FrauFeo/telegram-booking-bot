"""Entry point: python -m bot"""
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from .config import load_settings
from .db import DB
from .handlers import router
from .reminders import reminder_loop


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    settings = load_settings()
    if not settings.token:
        sys.exit("BOT_TOKEN is empty. Copy .env.example to .env and put the token from @BotFather there.")

    db = DB(settings.db_path)
    bot = Bot(settings.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    dp["db"] = db
    dp["settings"] = settings
    dp.include_router(router)

    await bot.set_my_commands([
        BotCommand(command="start", description="Menu / Меню"),
        BotCommand(command="today", description="Today's bookings / Записи на сьогодні"),
        BotCommand(command="week", description="Next 7 days / Записи на тиждень"),
    ])
    reminders = asyncio.create_task(reminder_loop(bot, db, settings))
    try:
        await dp.start_polling(bot)
    finally:
        reminders.cancel()


if __name__ == "__main__":
    asyncio.run(main())
