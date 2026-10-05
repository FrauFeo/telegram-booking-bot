"""Entry point: python -m bot"""
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramAPIError
from aiogram.types import BotCommand, FSInputFile, InputProfilePhotoStatic

from .config import ROOT, Settings, load_settings
from .db import DB
from .handlers import router
from .reminders import reminder_loop
from .texts import LANGS, t

AVATAR = ROOT / "assets" / "avatar.jpg"
log = logging.getLogger(__name__)


async def setup_profile(bot: Bot, s: Settings) -> None:
    """What people see before pressing Start: description, short description, avatar.

    Descriptions are set on every start (cheap, keeps them in sync with texts.py).
    The avatar is uploaded once: Telegram keeps it, and a marker file remembers
    which picture was sent, so a new avatar.jpg is picked up automatically.
    """
    try:
        for lang in LANGS:
            await bot.set_my_description(description=t(lang, "bot_description"), language_code=lang)
            await bot.set_my_short_description(short_description=t(lang, "bot_short", business=s.business[lang]),
                                               language_code=lang)
        await bot.set_my_description(description=t("en", "bot_description"))
        await bot.set_my_short_description(short_description=t("en", "bot_short", business=s.business["en"]))

        marker = s.db_path.with_name(".avatar_uploaded")
        stamp = str(AVATAR.stat().st_mtime_ns) if AVATAR.exists() else ""
        if stamp and (not marker.exists() or marker.read_text() != stamp):
            await bot.set_my_profile_photo(photo=InputProfilePhotoStatic(photo=FSInputFile(AVATAR)))
            marker.write_text(stamp)
    except TelegramAPIError as e:
        log.warning("Could not update the bot profile: %s", e)


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
    await setup_profile(bot, settings)
    reminders = asyncio.create_task(reminder_loop(bot, db, settings))
    try:
        await dp.start_polling(bot)
    finally:
        reminders.cancel()


if __name__ == "__main__":
    asyncio.run(main())
