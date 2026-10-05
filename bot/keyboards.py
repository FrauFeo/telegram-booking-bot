"""Keyboards and callback data."""
from datetime import date, datetime

from aiogram.filters.callback_data import CallbackData
from aiogram.types import DisabledButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .config import Settings
from .db import Booking
from .texts import day_label, short_day, t


class ServiceCb(CallbackData, prefix="svc"):
    sid: str


class DayCb(CallbackData, prefix="day"):
    sid: str
    d: str        # YYYYMMDD


class SlotCb(CallbackData, prefix="slot"):
    sid: str
    ts: str       # YYYYMMDDHHMM


class BackCb(CallbackData, prefix="back"):
    to: str       # "services" or "days"
    sid: str = ""


class ConfirmCb(CallbackData, prefix="cf"):
    ok: bool


class AdminCb(CallbackData, prefix="adm"):
    action: str   # "confirm" or "cancel"
    bid: int


class MyCancelCb(CallbackData, prefix="myc"):
    bid: int


# Button colours (Bot API 9.4+): "primary" blue, "success" green, "danger" red.
# They carry the meaning that emoji used to, without cluttering the text.

def main_kb(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=t(lang, "btn_book"), style="primary")],
        [KeyboardButton(text=t(lang, "btn_my")), KeyboardButton(text=t(lang, "btn_lang"))],
    ], resize_keyboard=True)


def contact_kb(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=t(lang, "btn_share"), request_contact=True, style="primary")],
        [KeyboardButton(text=t(lang, "btn_cancel"), style="danger")],
    ], resize_keyboard=True, one_time_keyboard=True)


def services_kb(lang: str, s: Settings):
    kb = InlineKeyboardBuilder()
    for svc in s.services.values():
        kb.button(text=t(lang, "service_line", name=svc.name(lang),
                         dur=int(svc.duration.total_seconds() // 60),
                         price=svc.price, cur=s.currency[lang]),
                  callback_data=ServiceCb(sid=svc.id))
    kb.adjust(1)
    return kb.as_markup()


# Taken days and times are disabled buttons AND say so in words: older Telegram apps
# do not grey out disabled buttons, and combining strikethrough renders as an underline
# in some fonts (Telegram Desktop), so plain words are the only reliable signal.

def days_kb(lang: str, sid: str, week: list[tuple[date, str]], today: date):
    """The whole booking window: days off and fully booked days are shown but disabled."""
    kb = InlineKeyboardBuilder()
    for d, status in week:
        if status == "free":
            kb.button(text=day_label(lang, d, today), callback_data=DayCb(sid=sid, d=f"{d:%Y%m%d}"))
        else:
            word = t(lang, "day_off" if status == "off" else "day_full")
            kb.button(text=f"{short_day(lang, d, today)} · {word}", disabled=DisabledButton())
    kb.button(text=t(lang, "back"), callback_data=BackCb(to="services"))
    kb.adjust(*([3] * ((len(week) + 2) // 3)), 1)
    return kb.as_markup()


def slots_kb(lang: str, sid: str, grid: list[tuple[datetime, bool]]):
    """The whole working day: free times are buttons, taken ones say "taken" and do nothing."""
    kb = InlineKeyboardBuilder()
    for start, free in grid:
        if free:
            kb.button(text=f"{start:%H:%M}", callback_data=SlotCb(sid=sid, ts=f"{start:%Y%m%d%H%M}"))
        else:
            kb.button(text=t(lang, "slot_busy"), disabled=DisabledButton())
    kb.button(text=t(lang, "back"), callback_data=BackCb(to="days", sid=sid))
    kb.adjust(*([4] * ((len(grid) + 3) // 4)), 1)
    return kb.as_markup()


def confirm_kb(lang: str):
    kb = InlineKeyboardBuilder()
    kb.button(text=t(lang, "btn_confirm"), callback_data=ConfirmCb(ok=True), style="success")
    kb.button(text=t(lang, "btn_cancel"), callback_data=ConfirmCb(ok=False), style="danger")
    return kb.as_markup()


def admin_kb(lang: str, bid: int):
    kb = InlineKeyboardBuilder()
    kb.button(text=t(lang, "btn_adm_confirm"), callback_data=AdminCb(action="confirm", bid=bid), style="success")
    kb.button(text=t(lang, "btn_adm_cancel"), callback_data=AdminCb(action="cancel", bid=bid), style="danger")
    return kb.as_markup()


def my_kb(lang: str, bookings: list[Booking]):
    kb = InlineKeyboardBuilder()
    for n, b in enumerate(bookings, 1):
        kb.button(text=t(lang, "btn_cancel_n", n=n), callback_data=MyCancelCb(bid=b.id), style="danger")
    kb.adjust(3)
    return kb.as_markup()
