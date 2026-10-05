"""Background task that sends reminders a day and 2 hours before a visit."""
import asyncio
import logging
from datetime import timedelta

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

from .config import Settings
from .db import DB
from .slots import ReminderState, due_reminders
from .texts import t

log = logging.getLogger(__name__)
CHECK_EVERY = 60  # seconds


async def send_due(bot: Bot, db: DB, s: Settings) -> None:
    now = s.now()
    for b in db.between(now, now + timedelta(hours=25)):
        state = ReminderState(start=b.start, created=b.created, sent_24h=b.sent_24h, sent_2h=b.sent_2h)
        for kind in due_reminders(state, now):
            lang = db.get_lang(b.user_id) or "uk"
            text = t(lang, f"remind_{kind}", time=f"{b.start:%H:%M}",
                     service=s.services[b.service_id].name(lang), business=s.business[lang])
            try:
                await bot.send_message(b.user_id, text)
            except TelegramAPIError as e:
                # The client blocked the bot or deleted the chat: retrying every minute won't help.
                log.warning("Reminder %s for booking %s not delivered: %s", kind, b.id, e)
            db.mark_reminded(b.id, kind)
            if kind == "2h":
                db.mark_reminded(b.id, "24h")


async def reminder_loop(bot: Bot, db: DB, s: Settings) -> None:
    while True:
        try:
            await send_due(bot, db, s)
        except Exception:
            log.exception("Reminder check failed")
        await asyncio.sleep(CHECK_EVERY)
