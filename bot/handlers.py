"""Bot handlers: the client's booking flow, the owner's buttons and commands.

The booking runs in one message that is edited step by step. Helper messages
(the phone request, the summary to check) are deleted once the booking is done,
so the chat ends with one clean card instead of a pile of prompts.
"""
import html
import re
from datetime import datetime, timedelta

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, FSInputFile, Message, User

from .config import ROOT, Service, Settings
from .db import DB, Booking
from .keyboards import (AdminCb, BackCb, ConfirmCb, DayCb, MyCancelCb, ServiceCb, SlotCb,
                        admin_kb, confirm_kb, contact_kb, days_kb, main_kb, my_kb,
                        services_kb, slots_kb)
from .slots import day_grid, overlaps, week_grid
from .texts import all_variants, fmt_day, fmt_when, status_text, step, t

router = Router()
PHONE_RE = re.compile(r"^\+?[\d\s()\-]{7,20}$")
BANNER = ROOT / "assets" / "banner.jpg"
_banner_file_id: dict[str, str] = {}   # Telegram file_id after the first upload, so the photo is sent once


class BookingForm(StatesGroup):
    contact = State()
    confirm = State()


def user_lang(db: DB, user: User) -> str:
    saved = db.get_lang(user.id)
    if saved:
        return saved
    return "uk" if (user.language_code or "").startswith(("uk", "ru")) else "en"


def busy_window(db: DB, s: Settings, now: datetime):
    return db.busy(now - timedelta(days=1), now + timedelta(days=s.schedule.days_ahead + 1))


def minutes(svc: Service) -> int:
    return int(svc.duration.total_seconds() // 60)


def card(lang: str, s: Settings, svc: Service, start: datetime, name: str, phone: str) -> str:
    return t(lang, "card", service=svc.name(lang), when=fmt_when(lang, start), dur=minutes(svc),
             price=svc.price, cur=s.currency[lang], name=html.escape(name), phone=html.escape(phone))


def booking_text(lang: str, key: str, b: Booking, s: Settings) -> str:
    svc = s.services[b.service_id]
    return t(lang, key, id=b.id, service=svc.name(lang), when=fmt_when(lang, b.start),
             name=html.escape(b.name), phone=html.escape(b.phone), status=status_text(lang, b.status),
             card=card(lang, s, svc, b.start, b.name, b.phone))


async def drop(bot: Bot, chat_id: int, *message_ids: int | None) -> None:
    """Delete helper messages; ones that are already gone or too old are skipped."""
    for mid in message_ids:
        if mid:
            try:
                await bot.delete_message(chat_id, mid)
            except TelegramBadRequest:
                pass


# --- start, language --------------------------------------------------------

@router.message(CommandStart())
async def start(message: Message, state: FSMContext, db: DB, settings: Settings):
    await state.clear()
    lang = user_lang(db, message.from_user)
    db.set_lang(message.from_user.id, lang)
    text = t(lang, "start", business=settings.business[lang])
    if settings.demo_mode:
        text += t(lang, "start_demo")
    if not BANNER.exists():
        await message.answer(text, reply_markup=main_kb(lang))
        return
    sent = await message.answer_photo(_banner_file_id.get("id") or FSInputFile(BANNER),
                                      caption=text, reply_markup=main_kb(lang))
    if getattr(sent, "photo", None):
        _banner_file_id["id"] = sent.photo[-1].file_id


@router.message(F.text.in_(all_variants("btn_lang")))
async def switch_lang(message: Message, db: DB):
    lang = "en" if user_lang(db, message.from_user) == "uk" else "uk"
    db.set_lang(message.from_user.id, lang)
    await message.answer(t(lang, "lang_set"), reply_markup=main_kb(lang))


# --- booking: service -> day -> time (one message, edited) -----------------

def services_text(lang: str) -> str:
    return step(lang, 1, "title_service") + "\n" + t(lang, "choose_service")


@router.message(F.text.in_(all_variants("btn_book")))
async def book(message: Message, state: FSMContext, db: DB, settings: Settings):
    await state.clear()
    lang = user_lang(db, message.from_user)
    await message.answer(services_text(lang), reply_markup=services_kb(lang, settings))


async def show_days(call: CallbackQuery, sid: str, db: DB, s: Settings):
    lang = user_lang(db, call.from_user)
    svc = s.services[sid]
    now = s.now()
    week = week_grid(svc.duration, busy_window(db, s, now), s.schedule, now)
    if not any(status == "free" for _, status in week):
        await call.message.edit_text(t(lang, "no_days"), reply_markup=services_kb(lang, s))
        return
    await call.message.edit_text(step(lang, 2, "title_day") + "\n" + t(lang, "choose_day", service=svc.name(lang)),
                                 reply_markup=days_kb(lang, sid, week, now.date()))


async def show_times(call: CallbackQuery, svc: Service, day, db: DB, s: Settings) -> bool:
    lang = user_lang(db, call.from_user)
    now = s.now()
    grid = day_grid(day, svc.duration, busy_window(db, s, now), s.schedule, now)
    if not any(free for _, free in grid):
        return False
    text = step(lang, 3, "title_time") + "\n" + t(lang, "choose_time", service=svc.name(lang), day=fmt_day(lang, day))
    await call.message.edit_text(text, reply_markup=slots_kb(lang, svc.id, grid))
    return True


@router.callback_query(ServiceCb.filter())
async def pick_service(call: CallbackQuery, callback_data: ServiceCb, db: DB, settings: Settings):
    if callback_data.sid in settings.services:
        await show_days(call, callback_data.sid, db, settings)
    await call.answer()


@router.callback_query(DayCb.filter())
async def pick_day(call: CallbackQuery, callback_data: DayCb, db: DB, settings: Settings):
    lang = user_lang(db, call.from_user)
    svc = settings.services[callback_data.sid]
    day = datetime.strptime(callback_data.d, "%Y%m%d").date()
    if not await show_times(call, svc, day, db, settings):
        await call.answer(t(lang, "slot_taken"), show_alert=True)
        await show_days(call, svc.id, db, settings)
        return
    await call.answer()


@router.callback_query(BackCb.filter())
async def go_back(call: CallbackQuery, callback_data: BackCb, db: DB, settings: Settings):
    lang = user_lang(db, call.from_user)
    if callback_data.to == "days" and callback_data.sid in settings.services:
        await show_days(call, callback_data.sid, db, settings)
    else:
        await call.message.edit_text(services_text(lang), reply_markup=services_kb(lang, settings))
    await call.answer()


@router.callback_query(SlotCb.filter())
async def pick_slot(call: CallbackQuery, callback_data: SlotCb, state: FSMContext,
                    db: DB, settings: Settings):
    lang = user_lang(db, call.from_user)
    svc = settings.services[callback_data.sid]
    start = datetime.strptime(callback_data.ts, "%Y%m%d%H%M")
    now = settings.now()
    if start < now + settings.schedule.min_lead or overlaps(start, svc.duration, busy_window(db, settings, now)):
        await call.answer(t(lang, "slot_taken"), show_alert=True)
        await show_times(call, svc, start.date(), db, settings)
        return
    await call.message.edit_text(t(lang, "picked", service=svc.name(lang), when=fmt_when(lang, start)))
    ask = await call.message.answer(step(lang, 4, "title_contact") + "\n" + t(lang, "ask_contact"),
                                    reply_markup=contact_kb(lang))
    await state.set_state(BookingForm.contact)
    await state.update_data(sid=svc.id, ts=callback_data.ts, flow_id=call.message.message_id,
                            ask_id=ask.message_id)
    await call.answer()


# --- contact and confirmation ---------------------------------------------

@router.message(BookingForm.contact, F.text.in_(all_variants("btn_cancel")))
@router.message(BookingForm.confirm, F.text.in_(all_variants("btn_cancel")))
async def cancel_flow(message: Message, state: FSMContext, bot: Bot, db: DB):
    data = await state.get_data()
    await state.clear()
    lang = user_lang(db, message.from_user)
    await drop(bot, message.chat.id, data.get("flow_id"), data.get("ask_id"), data.get("confirm_id"))
    await message.answer(t(lang, "flow_cancelled"), reply_markup=main_kb(lang))


@router.message(BookingForm.contact)
async def got_contact(message: Message, state: FSMContext, bot: Bot, db: DB, settings: Settings):
    lang = user_lang(db, message.from_user)
    if message.contact:
        phone = message.contact.phone_number
        name = message.contact.first_name or message.from_user.full_name
    elif message.text and PHONE_RE.match(message.text.strip()):
        phone, name = message.text.strip(), message.from_user.full_name
    else:
        await message.answer(t(lang, "bad_phone"))
        return
    data = await state.get_data()
    await drop(bot, message.chat.id, data.get("ask_id"))
    svc = settings.services[data["sid"]]
    start = datetime.strptime(data["ts"], "%Y%m%d%H%M")
    sent = await message.answer(t(lang, "confirm", card=card(lang, settings, svc, start, name, phone)),
                                reply_markup=confirm_kb(lang))
    await state.update_data(phone=phone, name=name, ask_id=None, confirm_id=sent.message_id)
    await state.set_state(BookingForm.confirm)


@router.callback_query(BookingForm.confirm, ConfirmCb.filter())
async def confirm(call: CallbackQuery, callback_data: ConfirmCb, state: FSMContext,
                  bot: Bot, db: DB, settings: Settings):
    lang = user_lang(db, call.from_user)
    data = await state.get_data()
    await state.clear()
    chat_id = call.message.chat.id
    await drop(bot, chat_id, data.get("flow_id"), data.get("confirm_id"))
    if not callback_data.ok:
        await call.message.answer(t(lang, "flow_cancelled"), reply_markup=main_kb(lang))
        await call.answer()
        return

    svc = settings.services[data["sid"]]
    start = datetime.strptime(data["ts"], "%Y%m%d%H%M")
    now = settings.now()
    # Someone else may have taken the slot while this client was typing the phone.
    if start < now + settings.schedule.min_lead or overlaps(start, svc.duration, busy_window(db, settings, now)):
        await call.message.answer(t(lang, "slot_taken"), reply_markup=main_kb(lang))
        await call.message.answer(services_text(lang), reply_markup=services_kb(lang, settings))
        await call.answer()
        return

    bid = db.add(call.from_user.id, data["name"], data["phone"], svc.id, start, svc.duration, now)
    b = db.get(bid)
    await call.message.answer(booking_text(lang, "booked", b, settings), reply_markup=main_kb(lang))
    await notify_owner(bot, db, settings, b, "admin_new", with_buttons=True)
    await call.answer()


async def notify_owner(bot: Bot, db: DB, s: Settings, b: Booking, key: str, with_buttons: bool):
    """Send a booking event to the owner. In demo mode the client gets a copy too."""
    recipients = set(s.admin_ids)
    demo_copy = s.demo_mode and b.user_id not in s.admin_ids
    if demo_copy:
        recipients.add(b.user_id)
    for uid in recipients:
        lang = db.get_lang(uid) or "uk"
        text = booking_text(lang, key, b, s)
        if demo_copy and uid == b.user_id:
            text = t(lang, "demo_note") + "\n\n" + text
        await bot.send_message(uid, text, reply_markup=admin_kb(lang, b.id) if with_buttons else None)


# --- owner's buttons --------------------------------------------------------

@router.callback_query(AdminCb.filter())
async def admin_action(call: CallbackQuery, callback_data: AdminCb, bot: Bot, db: DB, settings: Settings):
    lang = user_lang(db, call.from_user)
    b = db.get(callback_data.bid)
    allowed = call.from_user.id in settings.admin_ids or (
        settings.demo_mode and b is not None and b.user_id == call.from_user.id)
    if b is None or not allowed:
        await call.answer(t(lang, "not_admin"), show_alert=True)
        return
    if b.status != "pending":
        await call.answer(t(lang, "adm_already", id=b.id, status=status_text(lang, b.status)), show_alert=True)
        return

    new_status = "confirmed" if callback_data.action == "confirm" else "cancelled"
    db.set_status(b.id, new_status)
    result = t(lang, "adm_confirmed" if new_status == "confirmed" else "adm_cancelled", id=b.id)
    await call.message.edit_text(call.message.html_text + "\n\n" + result)

    client_lang = db.get_lang(b.user_id) or "uk"
    key = "client_confirmed" if new_status == "confirmed" else "client_cancelled"
    await bot.send_message(b.user_id, t(client_lang, key, when=fmt_when(client_lang, b.start)))
    await call.answer()


def bookings_list(lang: str, title: str, items: list[Booking], s: Settings) -> str:
    if not items:
        return t(lang, "list_empty")
    return title + "\n\n" + "\n\n".join(booking_text(lang, "list_item", b, s) for b in items)


async def owner_list(message: Message, db: DB, s: Settings, days: int, title_key: str):
    lang = user_lang(db, message.from_user)
    now = s.now()
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    items = db.between(start_of_day, start_of_day + timedelta(days=days))
    if message.from_user.id not in s.admin_ids:
        if not s.demo_mode:
            await message.answer(t(lang, "not_admin"))
            return
        # Demo testers see the owner's view, but only with their own bookings.
        items = [b for b in items if b.user_id == message.from_user.id]
    await message.answer(bookings_list(lang, t(lang, title_key), items, s))


@router.message(Command("today"))
async def today(message: Message, db: DB, settings: Settings):
    await owner_list(message, db, settings, 1, "list_today")


@router.message(Command("week"))
async def week(message: Message, db: DB, settings: Settings):
    await owner_list(message, db, settings, 7, "list_week")


# --- client's own bookings -------------------------------------------------

@router.message(F.text.in_(all_variants("btn_my")))
async def my_bookings(message: Message, db: DB, settings: Settings):
    lang = user_lang(db, message.from_user)
    items = db.upcoming_for_user(message.from_user.id, settings.now())
    if not items:
        await message.answer(t(lang, "my_empty"))
        return
    lines = [t(lang, "my_item", n=n, when=fmt_when(lang, b.start),
               service=settings.services[b.service_id].name(lang), status=status_text(lang, b.status))
             for n, b in enumerate(items, 1)]
    await message.answer(t(lang, "my_title") + "\n\n" + "\n\n".join(lines), reply_markup=my_kb(lang, items))


@router.callback_query(MyCancelCb.filter())
async def my_cancel(call: CallbackQuery, callback_data: MyCancelCb, bot: Bot, db: DB, settings: Settings):
    lang = user_lang(db, call.from_user)
    b = db.get(callback_data.bid)
    if b is None or b.user_id != call.from_user.id or b.status == "cancelled":
        await call.answer(t(lang, "my_empty"), show_alert=True)
        return
    db.set_status(b.id, "cancelled")
    await call.message.edit_text(t(lang, "cancel_done", when=fmt_when(lang, b.start)))
    await notify_owner(bot, db, settings, db.get(b.id), "admin_client_cancelled", with_buttons=False)
    await call.answer()


@router.message()
async def fallback(message: Message, db: DB):
    lang = user_lang(db, message.from_user)
    await message.answer(t(lang, "unknown"), reply_markup=main_kb(lang))
