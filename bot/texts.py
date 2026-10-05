"""Interface texts in Ukrainian and English."""
from datetime import date, datetime

LANGS = ("uk", "en")

TEXTS = {
    "uk": {
        "start": "Вітаю! Це бот запису в <b>{business}</b>.\nОберіть дію на кнопках нижче.",
        "btn_book": "📅 Записатися",
        "btn_my": "🗂 Мої записи",
        "btn_lang": "🌐 English",
        "lang_set": "Мову змінено на українську.",
        "choose_service": "Оберіть послугу:",
        "service_line": "{name} · {dur} хв · {price} {cur}",
        "choose_day": "<b>{service}</b>\nОберіть день:",
        "no_days": "На найближчі дні вільних місць немає. Спробуйте пізніше.",
        "choose_time": "<b>{service}</b>, {day}\nОберіть час:",
        "back": "⬅ Назад",
        "ask_contact": "Залиште номер телефону, щоб з вами могли зв'язатися.\n"
                       "Натисніть кнопку нижче або напишіть номер.",
        "btn_share": "📱 Поділитися номером",
        "btn_cancel": "✖ Скасувати",
        "bad_phone": "Не схоже на номер телефону. Спробуйте ще раз, наприклад +380 67 123 45 67.",
        "confirm": "Перевірте запис:\n\n<b>{service}</b>\n{when}\n{price} {cur}\n{name}, {phone}",
        "btn_confirm": "✅ Записатися",
        "slot_taken": "Цей час щойно зайняли. Оберіть інший, будь ласка.",
        "booked": "Готово! Ви записані:\n<b>{service}</b>, {when}.\n\n"
                  "Власник підтвердить запис, а ми нагадаємо за добу і за 2 години до візиту.",
        "flow_cancelled": "Запис скасовано.",
        "my_empty": "У вас немає майбутніх записів.",
        "my_title": "Ваші записи:",
        "my_item": "{n}. {when} · {service} · {status}",
        "status_pending": "очікує підтвердження",
        "status_confirmed": "підтверджено",
        "btn_cancel_n": "✖ Скасувати {n}",
        "cancel_done": "Запис на {when} скасовано.",
        "remind_24h": "⏰ Нагадуємо: завтра о {time} у вас <b>{service}</b> в {business}.",
        "remind_2h": "⏰ Через 2 години, о {time}, у вас <b>{service}</b> в {business}. Чекаємо!",
        "admin_new": "🆕 Новий запис #{id}\n<b>{service}</b>\n{when}\n{name}, {phone}",
        "btn_adm_confirm": "✅ Підтвердити",
        "btn_adm_cancel": "❌ Скасувати",
        "adm_confirmed": "✅ Запис #{id} підтверджено.",
        "adm_cancelled": "❌ Запис #{id} скасовано.",
        "adm_already": "Запис #{id} вже має статус: {status}.",
        "client_confirmed": "✅ Ваш запис на {when} підтверджено. До зустрічі!",
        "client_cancelled": "На жаль, запис на {when} скасовано. "
                            "Оберіть інший час через «📅 Записатися».",
        "admin_client_cancelled": "Клієнт скасував запис #{id}: {service}, {when}.",
        "demo_note": "👀 Демо: так це повідомлення побачить власник бізнесу. Кнопки працюють.",
        "list_today": "Записи на сьогодні:",
        "list_week": "Записи на 7 днів:",
        "list_empty": "Записів немає.",
        "list_item": "#{id} {when} · {service} · {name}, {phone} · {status}",
        "not_admin": "Ця команда для власника бізнесу.",
        "unknown": "Скористайтеся кнопками внизу 👇",
        "minutes": "хв",
        "at": "о",
        "weekdays": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"],
    },
    "en": {
        "start": "Hi! This is the booking bot of <b>{business}</b>.\nChoose an action below.",
        "btn_book": "📅 Book",
        "btn_my": "🗂 My bookings",
        "btn_lang": "🌐 Українська",
        "lang_set": "Language switched to English.",
        "choose_service": "Choose a service:",
        "service_line": "{name} · {dur} min · {price} {cur}",
        "choose_day": "<b>{service}</b>\nChoose a day:",
        "no_days": "No free slots in the next days. Please try again later.",
        "choose_time": "<b>{service}</b>, {day}\nChoose a time:",
        "back": "⬅ Back",
        "ask_contact": "Leave your phone number so we can reach you.\n"
                       "Tap the button below or type the number.",
        "btn_share": "📱 Share my number",
        "btn_cancel": "✖ Cancel",
        "bad_phone": "That does not look like a phone number. Try again, for example +380 67 123 45 67.",
        "confirm": "Check your booking:\n\n<b>{service}</b>\n{when}\n{price} {cur}\n{name}, {phone}",
        "btn_confirm": "✅ Book it",
        "slot_taken": "Someone has just taken this time. Please choose another one.",
        "booked": "Done! You are booked:\n<b>{service}</b>, {when}.\n\n"
                  "The owner will confirm it, and we will remind you a day and 2 hours before.",
        "flow_cancelled": "Booking cancelled.",
        "my_empty": "You have no upcoming bookings.",
        "my_title": "Your bookings:",
        "my_item": "{n}. {when} · {service} · {status}",
        "status_pending": "waiting for confirmation",
        "status_confirmed": "confirmed",
        "btn_cancel_n": "✖ Cancel {n}",
        "cancel_done": "Your booking for {when} is cancelled.",
        "remind_24h": "⏰ Reminder: tomorrow at {time} you have <b>{service}</b> at {business}.",
        "remind_2h": "⏰ In 2 hours, at {time}, you have <b>{service}</b> at {business}. See you!",
        "admin_new": "🆕 New booking #{id}\n<b>{service}</b>\n{when}\n{name}, {phone}",
        "btn_adm_confirm": "✅ Confirm",
        "btn_adm_cancel": "❌ Cancel",
        "adm_confirmed": "✅ Booking #{id} confirmed.",
        "adm_cancelled": "❌ Booking #{id} cancelled.",
        "adm_already": "Booking #{id} is already {status}.",
        "client_confirmed": "✅ Your booking for {when} is confirmed. See you!",
        "client_cancelled": "Sorry, your booking for {when} was cancelled. "
                            "Please pick another time with «📅 Book».",
        "admin_client_cancelled": "The client cancelled booking #{id}: {service}, {when}.",
        "demo_note": "👀 Demo: this is what the business owner sees. The buttons work.",
        "list_today": "Today's bookings:",
        "list_week": "Bookings for the next 7 days:",
        "list_empty": "No bookings.",
        "list_item": "#{id} {when} · {service} · {name}, {phone} · {status}",
        "not_admin": "This command is for the business owner.",
        "unknown": "Please use the buttons below 👇",
        "minutes": "min",
        "at": "at",
        "weekdays": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    },
}


def t(lang: str, key: str, **kw) -> str:
    text = TEXTS.get(lang, TEXTS["uk"])[key]
    return text.format(**kw) if kw else text


def fmt_day(lang: str, d: date) -> str:
    return f"{TEXTS[lang]['weekdays'][d.weekday()]} {d:%d.%m}"


def fmt_when(lang: str, dt: datetime) -> str:
    return f"{fmt_day(lang, dt.date())} {TEXTS[lang]['at']} {dt:%H:%M}"


def status_text(lang: str, status: str) -> str:
    return t(lang, f"status_{status}") if status in ("pending", "confirmed") else status


def all_variants(key: str) -> set[str]:
    """A button label in every language, to match it whatever language the user has."""
    return {TEXTS[lang][key] for lang in LANGS}
