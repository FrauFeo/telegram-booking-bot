"""Interface texts in Ukrainian and English.

Emoji only on the three main menu buttons: everything else relies on bold
headings, quote blocks and coloured buttons, so messages stay clean.
"""
from datetime import date, datetime

LANGS = ("uk", "en")

TEXTS = {
    "uk": {
        "bot_short": "Онлайн-запис у {business}: послуга, день і вільний час за хвилину. Демо-бот.",
        "bot_description": "Бот запису клієнтів для барбершопу, салону чи репетитора.\n\n"
                           "Оберіть послугу, день і вільний час, залиште телефон. Власник отримає заявку "
                           "з кнопками, а вам прийде нагадування за добу і за 2 години до візиту.\n\n"
                           "Це демо: ви побачите і бік клієнта, і бік власника. Номер можна вводити вигаданий.",
        "start": "<b>{business}</b>\nЗапис онлайн за хвилину: оберіть послугу, день і вільний час.",
        "start_demo": "\n\n<i>Це демо-бот. Можна записатися з вигаданим номером: ви побачите і бік клієнта, "
                      "і бік власника.</i>",
        "btn_book": "📅 Записатися",
        "btn_my": "🗂 Мої записи",
        "btn_lang": "🌐 English",
        "lang_set": "Мову змінено на українську.",
        "step": "<b>Крок {n} з 4 · {title}</b>",
        "title_service": "Послуга",
        "title_day": "День",
        "title_time": "Час",
        "title_contact": "Контакт",
        "choose_service": "Оберіть, що вам потрібно:",
        "service_line": "{name} · {dur} хв · {price} {cur}",
        "choose_day": "{service}\nОберіть день:",
        "no_days": "На найближчі дні вільних місць немає. Спробуйте пізніше.",
        "choose_time": "{service}, {day}\nОберіть вільний час:",
        "back": "Назад",
        "picked": "<b>{service}</b>\n{when}",
        "ask_contact": "Залиште номер телефону, щоб з вами могли зв'язатися. "
                       "Натисніть кнопку нижче або напишіть номер.",
        "btn_share": "Поділитися номером",
        "btn_cancel": "Скасувати",
        "bad_phone": "Не схоже на номер телефону. Спробуйте ще раз, наприклад +380 67 123 45 67.",
        "card": "<b>Послуга:</b> {service}\n<b>Коли:</b> {when}\n<b>Тривалість:</b> {dur} хв\n"
                "<b>Ціна:</b> {price} {cur}\n<b>Контакт:</b> {name}, {phone}",
        "confirm": "<b>Перевірте запис</b>\n<blockquote>{card}</blockquote>",
        "btn_confirm": "Записатися",
        "slot_taken": "Цей час щойно зайняли. Оберіть інший, будь ласка.",
        "booked": "<b>Ви записані</b>\n<blockquote>{card}</blockquote>\n"
                  "Власник підтвердить запис, а ми нагадаємо за добу і за 2 години до візиту.",
        "flow_cancelled": "Запис скасовано.",
        "my_empty": "У вас немає майбутніх записів.",
        "my_title": "<b>Ваші записи</b>",
        "my_item": "<b>{n}.</b> {when}\n{service} · <i>{status}</i>",
        "status_pending": "очікує підтвердження",
        "status_confirmed": "підтверджено",
        "btn_cancel_n": "Скасувати {n}",
        "cancel_done": "Запис на {when} скасовано.",
        "remind_24h": "<b>Нагадування</b>\nЗавтра о {time} у вас {service} в {business}.",
        "remind_2h": "<b>Нагадування</b>\nЧерез 2 години, о {time}, у вас {service} в {business}. Чекаємо!",
        "admin_new": "<b>Новий запис #{id}</b>\n<blockquote>{card}</blockquote>",
        "btn_adm_confirm": "Підтвердити",
        "btn_adm_cancel": "Скасувати",
        "adm_confirmed": "<b>Запис #{id} підтверджено.</b>",
        "adm_cancelled": "<b>Запис #{id} скасовано.</b>",
        "adm_already": "Запис #{id} вже має статус: {status}.",
        "client_confirmed": "Ваш запис на {when} <b>підтверджено</b>. До зустрічі!",
        "client_cancelled": "На жаль, запис на {when} скасовано. Оберіть інший час через «Записатися».",
        "admin_client_cancelled": "<b>Клієнт скасував запис #{id}</b>\n<blockquote>{card}</blockquote>",
        "demo_note": "<i>Демо: так це повідомлення побачить власник бізнесу. Кнопки працюють.</i>",
        "list_today": "<b>Записи на сьогодні</b>",
        "list_week": "<b>Записи на 7 днів</b>",
        "list_empty": "Записів немає.",
        "list_item": "<b>#{id}</b> {when} · {service}\n{name}, {phone} · <i>{status}</i>",
        "not_admin": "Ця команда для власника бізнесу.",
        "unknown": "Скористайтеся кнопками внизу.",
        "today": "Сьогодні",
        "slot_busy": "зайнято",
        "day_off": "вихідний",
        "day_full": "зайнято",
        "tomorrow": "Завтра",
        "at": "о",
        "weekdays": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"],
    },
    "en": {
        "bot_short": "Book at {business} online: service, day and a free time in a minute. Demo bot.",
        "bot_description": "Booking bot for a barbershop, salon or tutor.\n\n"
                           "Pick a service, a day and a free time, leave your phone. The owner gets the request "
                           "with buttons, and you get reminders a day and 2 hours before the visit.\n\n"
                           "This is a demo: you see both the client side and the owner side. "
                           "A made-up phone number is fine.",
        "start": "<b>{business}</b>\nBook online in a minute: pick a service, a day and a free time.",
        "start_demo": "\n\n<i>This is a demo bot. Book with a made-up number: you will see both the client "
                      "side and the owner side.</i>",
        "btn_book": "📅 Book",
        "btn_my": "🗂 My bookings",
        "btn_lang": "🌐 Українська",
        "lang_set": "Language switched to English.",
        "step": "<b>Step {n} of 4 · {title}</b>",
        "title_service": "Service",
        "title_day": "Day",
        "title_time": "Time",
        "title_contact": "Contact",
        "choose_service": "Choose what you need:",
        "service_line": "{name} · {dur} min · {price} {cur}",
        "choose_day": "{service}\nChoose a day:",
        "no_days": "No free slots in the next days. Please try again later.",
        "choose_time": "{service}, {day}\nChoose a free time:",
        "back": "Back",
        "picked": "<b>{service}</b>\n{when}",
        "ask_contact": "Leave your phone number so we can reach you. Tap the button below or type the number.",
        "btn_share": "Share my number",
        "btn_cancel": "Cancel",
        "bad_phone": "That does not look like a phone number. Try again, for example +380 67 123 45 67.",
        "card": "<b>Service:</b> {service}\n<b>When:</b> {when}\n<b>Duration:</b> {dur} min\n"
                "<b>Price:</b> {price} {cur}\n<b>Contact:</b> {name}, {phone}",
        "confirm": "<b>Check your booking</b>\n<blockquote>{card}</blockquote>",
        "btn_confirm": "Book it",
        "slot_taken": "Someone has just taken this time. Please choose another one.",
        "booked": "<b>You are booked</b>\n<blockquote>{card}</blockquote>\n"
                  "The owner will confirm it, and we will remind you a day and 2 hours before.",
        "flow_cancelled": "Booking cancelled.",
        "my_empty": "You have no upcoming bookings.",
        "my_title": "<b>Your bookings</b>",
        "my_item": "<b>{n}.</b> {when}\n{service} · <i>{status}</i>",
        "status_pending": "waiting for confirmation",
        "status_confirmed": "confirmed",
        "btn_cancel_n": "Cancel {n}",
        "cancel_done": "Your booking for {when} is cancelled.",
        "remind_24h": "<b>Reminder</b>\nTomorrow at {time} you have {service} at {business}.",
        "remind_2h": "<b>Reminder</b>\nIn 2 hours, at {time}, you have {service} at {business}. See you!",
        "admin_new": "<b>New booking #{id}</b>\n<blockquote>{card}</blockquote>",
        "btn_adm_confirm": "Confirm",
        "btn_adm_cancel": "Cancel",
        "adm_confirmed": "<b>Booking #{id} confirmed.</b>",
        "adm_cancelled": "<b>Booking #{id} cancelled.</b>",
        "adm_already": "Booking #{id} is already {status}.",
        "client_confirmed": "Your booking for {when} is <b>confirmed</b>. See you!",
        "client_cancelled": "Sorry, your booking for {when} was cancelled. Please pick another time with «Book».",
        "admin_client_cancelled": "<b>The client cancelled booking #{id}</b>\n<blockquote>{card}</blockquote>",
        "demo_note": "<i>Demo: this is what the business owner sees. The buttons work.</i>",
        "list_today": "<b>Today's bookings</b>",
        "list_week": "<b>Bookings for the next 7 days</b>",
        "list_empty": "No bookings.",
        "list_item": "<b>#{id}</b> {when} · {service}\n{name}, {phone} · <i>{status}</i>",
        "not_admin": "This command is for the business owner.",
        "unknown": "Please use the buttons below.",
        "today": "Today",
        "slot_busy": "taken",
        "day_off": "day off",
        "day_full": "full",
        "tomorrow": "Tomorrow",
        "at": "at",
        "weekdays": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    },
}


def t(lang: str, key: str, **kw) -> str:
    text = TEXTS.get(lang, TEXTS["uk"])[key]
    return text.format(**kw) if kw else text


def step(lang: str, n: int, title_key: str) -> str:
    return t(lang, "step", n=n, title=t(lang, title_key))


def fmt_day(lang: str, d: date) -> str:
    return f"{TEXTS[lang]['weekdays'][d.weekday()]} {d:%d.%m}"


def day_label(lang: str, d: date, today: date) -> str:
    """Button label: "Today" and "Tomorrow" read faster than a date."""
    if d == today:
        return t(lang, "today")
    if (d - today).days == 1:
        return t(lang, "tomorrow")
    return fmt_day(lang, d)


def short_day(lang: str, d: date, today: date) -> str:
    """Short day name for a disabled button: "Today", "Tomorrow" or a weekday."""
    if d == today:
        return t(lang, "today")
    if (d - today).days == 1:
        return t(lang, "tomorrow")
    return TEXTS[lang]["weekdays"][d.weekday()]


def fmt_when(lang: str, dt: datetime) -> str:
    return f"{fmt_day(lang, dt.date())} {TEXTS[lang]['at']} {dt:%H:%M}"


def status_text(lang: str, status: str) -> str:
    return t(lang, f"status_{status}") if status in ("pending", "confirmed") else status


def all_variants(key: str) -> set[str]:
    """A button label in every language, to match it whatever language the user has."""
    return {TEXTS[lang][key] for lang in LANGS}
