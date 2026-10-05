"""Keyboards and callback data."""
from datetime import date, datetime

from aiogram.filters.callback_data import CallbackData
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from .config import Settings
from .db import Booking
from .texts import fmt_day, t


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


def main_kb(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=t(lang, "btn_book")), KeyboardButton(text=t(lang, "btn_my"))],
        [KeyboardButton(text=t(lang, "btn_lang"))],
    ], resize_keyboard=True)


def contact_kb(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=t(lang, "btn_share"), request_contact=True)],
        [KeyboardButton(text=t(lang, "btn_cancel"))],
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


def days_kb(lang: str, sid: str, days: list[date]):
    kb = InlineKeyboardBuilder()
    for d in days:
        kb.button(text=fmt_day(lang, d), callback_data=DayCb(sid=sid, d=f"{d:%Y%m%d}"))
    kb.button(text=t(lang, "back"), callback_data=BackCb(to="services"))
    kb.adjust(*([3] * ((len(days) + 2) // 3)), 1)
    return kb.as_markup()


def slots_kb(lang: str, sid: str, slots: list[datetime]):
    kb = InlineKeyboardBuilder()
    for s in slots:
        kb.button(text=f"{s:%H:%M}", callback_data=SlotCb(sid=sid, ts=f"{s:%Y%m%d%H%M}"))
    kb.button(text=t(lang, "back"), callback_data=BackCb(to="days", sid=sid))
    kb.adjust(*([4] * ((len(slots) + 3) // 4)), 1)
    return kb.as_markup()


def confirm_kb(lang: str):
    kb = InlineKeyboardBuilder()
    kb.button(text=t(lang, "btn_confirm"), callback_data=ConfirmCb(ok=True))
    kb.button(text=t(lang, "btn_cancel"), callback_data=ConfirmCb(ok=False))
    return kb.as_markup()


def admin_kb(lang: str, bid: int):
    kb = InlineKeyboardBuilder()
    kb.button(text=t(lang, "btn_adm_confirm"), callback_data=AdminCb(action="confirm", bid=bid))
    kb.button(text=t(lang, "btn_adm_cancel"), callback_data=AdminCb(action="cancel", bid=bid))
    return kb.as_markup()


def my_kb(lang: str, bookings: list[Booking]):
    kb = InlineKeyboardBuilder()
    for n, b in enumerate(bookings, 1):
        kb.button(text=t(lang, "btn_cancel_n", n=n), callback_data=MyCancelCb(bid=b.id))
    kb.adjust(3)
    return kb.as_markup()
