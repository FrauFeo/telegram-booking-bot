"""End-to-end check of the handlers without Telegram.

Updates are fed straight into the dispatcher, and a fake session records every
API call the bot makes instead of sending it.
"""
from datetime import datetime, time, timedelta

import pytest
from aiogram import Bot, Dispatcher
from aiogram.client.session.base import BaseSession
from aiogram.methods import DeleteMessage, EditMessageReplyMarkup, EditMessageText, SendMessage, SendPhoto
from aiogram.types import CallbackQuery, Chat, Contact, Message, Update, User
from zoneinfo import ZoneInfo

from bot.config import Service, Settings
from bot.db import DB
from bot.handlers import router
from bot.reminders import send_due
from bot.slots import Schedule

CLIENT, OWNER = 111, 999
NOW = datetime(2026, 10, 5, 9, 0)   # Monday morning


class FakeSession(BaseSession):
    def __init__(self):
        super().__init__()
        self.calls = []

    async def make_request(self, bot, method, timeout=None):
        self.calls.append(method)
        if isinstance(method, (SendMessage, SendPhoto, EditMessageText, EditMessageReplyMarkup)):
            chat_id = getattr(method, "chat_id", None) or CLIENT
            return Message(message_id=len(self.calls), date=datetime.now(),
                           chat=Chat(id=chat_id, type="private"), text=getattr(method, "text", "") or "")
        return True

    async def stream_content(self, *a, **kw):  # not used by these tests
        raise NotImplementedError

    async def close(self):
        pass

    def sent(self, kind=SendMessage, chat_id=None):
        return [c for c in self.calls if isinstance(c, kind) and (chat_id is None or c.chat_id == chat_id)]


@pytest.fixture(scope="module")
def dp():
    d = Dispatcher()
    d.include_router(router)
    return d


@pytest.fixture
def env(tmp_path, monkeypatch, dp):
    settings = Settings(
        token="1:test", admin_ids=frozenset({OWNER}), demo_mode=True, db_path=tmp_path / "t.db",
        business={"uk": "Barber Lab", "en": "Barber Lab"}, currency={"uk": "грн", "en": "UAH"},
        tz=ZoneInfo("Europe/Kyiv"),
        schedule=Schedule((0, 1, 2, 3, 4, 5), time(10), time(19), timedelta(minutes=30),
                          timedelta(hours=1), 7),
        services={"haircut": Service("haircut", {"uk": "Стрижка", "en": "Haircut"}, timedelta(hours=1), 500)},
    )
    monkeypatch.setattr(Settings, "now", lambda self: NOW)
    db = DB(settings.db_path)
    dp["db"], dp["settings"] = db, settings
    session = FakeSession()
    bot = Bot("1:test", session=session)
    return dp, bot, session, db, settings


_uid = 0


def _next():
    global _uid
    _uid += 1
    return _uid


def user(uid):
    return User(id=uid, is_bot=False, first_name=f"U{uid}", language_code="uk")


def msg(uid, text=None, contact=None):
    return Message(message_id=_next(), date=datetime.now(), chat=Chat(id=uid, type="private"),
                   from_user=user(uid), text=text, contact=contact)


async def send_text(dp, bot, uid, text=None, contact=None):
    await dp.feed_update(bot, Update(update_id=_next(), message=msg(uid, text, contact)))


async def press(dp, bot, uid, data):
    cq = CallbackQuery(id=str(_next()), from_user=user(uid), chat_instance="x", data=data,
                       message=msg(uid, "previous"))
    await dp.feed_update(bot, Update(update_id=_next(), callback_query=cq))


def buttons(method):
    return [b for row in method.reply_markup.inline_keyboard for b in row]


def clickable(method):
    return [b for b in buttons(method) if b.callback_data]


async def book_first_slot(dp, bot, session):
    await send_text(dp, bot, CLIENT, "/start")
    await send_text(dp, bot, CLIENT, "📅 Записатися")
    await press(dp, bot, CLIENT, buttons(session.sent()[-1])[0].callback_data)        # service
    await press(dp, bot, CLIENT, clickable(session.sent(EditMessageText)[-1])[0].callback_data)  # first day
    slot = clickable(session.sent(EditMessageText)[-1])[0]
    await press(dp, bot, CLIENT, slot.callback_data)                                   # first time
    await send_text(dp, bot, CLIENT, "+380 67 123 45 67")
    await press(dp, bot, CLIENT, buttons(session.sent()[-1])[0].callback_data)        # confirm
    return slot


async def test_full_booking_flow(env):
    dp, bot, session, db, s = env
    slot = await book_first_slot(dp, bot, session)

    assert slot.text == "10:00"          # Monday 09:00 + 1h lead -> first slot is 10:00 today
    b = db.get(1)
    assert b.start == datetime(2026, 10, 5, 10, 0) and b.phone == "+380 67 123 45 67"
    assert any("Ви записані" in m.text for m in session.sent(chat_id=CLIENT))
    owner_msgs = session.sent(chat_id=OWNER)
    assert owner_msgs and "Новий запис #1" in owner_msgs[-1].text
    # demo mode: the client also gets the owner's view
    assert any(m.text.startswith("<i>Демо") for m in session.sent(chat_id=CLIENT))
    # helper messages (the step-by-step message and the summary) are cleaned up
    assert len([c for c in session.calls if isinstance(c, DeleteMessage)]) >= 3


async def test_booked_slot_disappears(env):
    dp, bot, session, db, s = env
    await book_first_slot(dp, bot, session)
    await send_text(dp, bot, CLIENT, "📅 Записатися")
    await press(dp, bot, CLIENT, buttons(session.sent()[-1])[0].callback_data)
    await press(dp, bot, CLIENT, buttons(session.sent(EditMessageText)[-1])[0].callback_data)
    grid = {b.text.replace("̶", ""): b for b in buttons(session.sent(EditMessageText)[-1])}
    assert "̶" in [b for b in buttons(session.sent(EditMessageText)[-1]) if b.disabled][0].text   # crossed out
    assert grid["10:00"].disabled is not None and grid["10:30"].disabled is not None   # shown, but greyed out
    assert grid["11:00"].callback_data and grid["11:00"].disabled is None
    # Telegram accepts exactly one action per button: a disabled one must not carry callback data
    assert all(not (b.disabled and b.callback_data) for b in grid.values())


async def test_owner_confirms_and_client_is_told(env):
    dp, bot, session, db, s = env
    await book_first_slot(dp, bot, session)
    confirm_btn = buttons(session.sent(chat_id=OWNER)[-1])[0]
    await press(dp, bot, OWNER, confirm_btn.callback_data)
    assert db.get(1).status == "confirmed"
    assert "підтверджено" in session.sent(chat_id=CLIENT)[-1].text


async def test_stranger_cannot_use_owner_buttons(env):
    dp, bot, session, db, s = env
    await book_first_slot(dp, bot, session)
    confirm_btn = buttons(session.sent(chat_id=OWNER)[-1])[0]
    await press(dp, bot, 555, confirm_btn.callback_data)
    assert db.get(1).status == "pending"


async def test_bad_phone_is_rejected(env):
    dp, bot, session, db, s = env
    await send_text(dp, bot, CLIENT, "📅 Записатися")
    await press(dp, bot, CLIENT, buttons(session.sent()[-1])[0].callback_data)
    await press(dp, bot, CLIENT, buttons(session.sent(EditMessageText)[-1])[0].callback_data)
    await press(dp, bot, CLIENT, clickable(session.sent(EditMessageText)[-1])[0].callback_data)
    await send_text(dp, bot, CLIENT, "hello")
    assert "Не схоже" in session.sent(chat_id=CLIENT)[-1].text
    await send_text(dp, bot, CLIENT, contact=Contact(phone_number="380671234567", first_name="Ivan"))
    assert "Перевірте запис" in session.sent(chat_id=CLIENT)[-1].text


async def test_client_cancels_own_booking(env):
    dp, bot, session, db, s = env
    await book_first_slot(dp, bot, session)
    await send_text(dp, bot, CLIENT, "🗂 Мої записи")
    await press(dp, bot, CLIENT, buttons(session.sent(chat_id=CLIENT)[-1])[0].callback_data)
    assert db.get(1).status == "cancelled"
    assert "скасував" in session.sent(chat_id=OWNER)[-1].text


async def test_reminder_sent_once(env, monkeypatch):
    dp, bot, session, db, s = env
    db.add(CLIENT, "Ivan", "+380", "haircut", datetime(2026, 10, 6, 12, 0), timedelta(hours=1),
           datetime(2026, 10, 1, 9, 0))
    monkeypatch.setattr(Settings, "now", lambda self: datetime(2026, 10, 5, 12, 5))
    await send_due(bot, db, s)
    await send_due(bot, db, s)
    reminders = [m for m in session.sent(chat_id=CLIENT) if "Нагадування" in m.text]
    assert len(reminders) == 1 and "Завтра о 12:00" in reminders[0].text


async def test_profile_setup_fits_limits_and_uploads_avatar_once(env, monkeypatch, tmp_path):
    from aiogram.methods import SetMyDescription, SetMyProfilePhoto, SetMyShortDescription
    import bot.__main__ as main
    dp, bot, session, db, s = env
    avatar = tmp_path / "avatar.jpg"
    avatar.write_bytes(b"jpg")
    monkeypatch.setattr(main, "AVATAR", avatar)

    await main.setup_profile(bot, s)
    await main.setup_profile(bot, s)   # a restart must not re-upload the same avatar

    descs = [c for c in session.calls if isinstance(c, SetMyDescription)]
    shorts = [c for c in session.calls if isinstance(c, SetMyShortDescription)]
    assert descs and all(len(c.description) <= 512 for c in descs)
    assert shorts and all(len(c.short_description) <= 120 for c in shorts)
    assert len([c for c in session.calls if isinstance(c, SetMyProfilePhoto)]) == 1


async def test_week_shows_days_off_greyed(env):
    dp, bot, session, db, s = env
    await send_text(dp, bot, CLIENT, "📅 Записатися")
    await press(dp, bot, CLIENT, buttons(session.sent()[-1])[0].callback_data)
    days = [b for b in buttons(session.sent(EditMessageText)[-1]) if b.text != "Назад"]
    assert len(days) == 8                                   # today + 7 days, nothing hidden
    sunday = next(b for b in days if b.text.replace("̶", "").startswith("Нд"))
    assert sunday.disabled is not None and not sunday.callback_data
    assert days[0].text == "Сьогодні" and days[0].callback_data
