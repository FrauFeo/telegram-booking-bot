"""Portfolio cover for the booking bot: a mock Telegram chat. 1280x800, Pillow."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 800
OUT = Path(__file__).with_name("cover-booking-bot.png")
F = "C:/Windows/Fonts/"

BG = (14, 22, 33)
CHAT = (24, 34, 45)
BOT = (33, 47, 61)
ME = (43, 82, 120)
BTN = (40, 58, 76)
ACCENT = (82, 170, 230)
TEXT = (236, 241, 245)
MUTED = (130, 148, 165)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)
f = lambda name, size: ImageFont.truetype(F + name, size)
EMOJI = ImageFont.truetype(F + "seguiemj.ttf", 22)
title, sub, body, small = f("segoeuib.ttf", 58), f("segoeui.ttf", 28), f("segoeui.ttf", 23), f("segoeui.ttf", 19)

# left: what it is
x = 70
d.text((x, 90), "TELEGRAM · PYTHON · AIOGRAM 3", font=f("segoeuib.ttf", 22), fill=ACCENT)
d.text((x, 130), "Бот запису", font=title, fill=TEXT)
d.text((x, 200), "клієнтів", font=title, fill=TEXT)
d.text((x, 290), "Послуга → день → вільний час →", font=sub, fill=MUTED)
d.text((x, 328), "телефон → підтвердження власника", font=sub, fill=MUTED)
y = 410
for line in ["Нагадування за добу і за 2 години", "Кнопки для власника бізнесу", "Українська та англійська", "19 автотестів, працює на сервері"]:
    d.ellipse((x, y + 10, x + 12, y + 22), fill=ACCENT)
    d.text((x + 28, y), line, font=f("segoeui.ttf", 26), fill=TEXT)
    y += 50
d.text((x, 650), "t.me/SoexDemo_Bot", font=f("segoeuib.ttf", 26), fill=ACCENT)

# right: phone-like chat
px0, py0, px1, py1 = 700, 60, 1210, 740
d.rounded_rectangle((px0, py0, px1, py1), radius=36, fill=CHAT)
d.rectangle((px0, py0 + 30, px1, py0 + 92), fill=BOT)
d.rounded_rectangle((px0, py0, px1, py0 + 92), radius=36, fill=BOT)
d.ellipse((px0 + 24, py0 + 26, px0 + 70, py0 + 72), fill=ACCENT)
d.text((px0 + 38, py0 + 32), "B", font=f("segoeuib.ttf", 26), fill=BG)
d.text((px0 + 86, py0 + 26), "Barber Lab Demo", font=f("segoeuib.ttf", 22), fill=TEXT)
d.text((px0 + 86, py0 + 54), "бот", font=small, fill=MUTED)


def draw_line(x, y, t):
    """Draw text; a leading emoji goes through the color emoji font."""
    if t and ord(t[0]) > 0x2000 and not t[0].isalpha():
        emoji, rest = t.split(" ", 1)
        d.text((x, y + 3), emoji, font=EMOJI, embedded_color=True)
        d.text((x + d.textlength(emoji, font=EMOJI) + 6, y), rest, font=body, fill=TEXT)
    else:
        d.text((x, y), t, font=body, fill=TEXT)


def line_width(t):
    if t and ord(t[0]) > 0x2000 and not t[0].isalpha():
        emoji, rest = t.split(" ", 1)
        return d.textlength(emoji, font=EMOJI) + 6 + d.textlength(rest, font=body)
    return d.textlength(t, font=body)


def bubble(y, text_lines, mine=False):
    w = max(line_width(t) for t in text_lines) + 36
    h = 18 + 32 * len(text_lines)
    x1 = px1 - 24 if mine else px0 + 24 + w
    x0 = x1 - w
    d.rounded_rectangle((x0, y, x1, y + h), radius=16, fill=ME if mine else BOT)
    for i, t in enumerate(text_lines):
        draw_line(x0 + 18, y + 9 + 32 * i, t)
    return y + h + 14


def buttons(y, rows):
    bw_total = px1 - px0 - 48
    for row in rows:
        bw = (bw_total - 8 * (len(row) - 1)) / len(row)
        for i, label in enumerate(row):
            bx = px0 + 24 + i * (bw + 8)
            d.rounded_rectangle((bx, y, bx + bw, y + 44), radius=10, fill=BTN)
            tw = line_width(label)
            draw_line(bx + (bw - tw) / 2, y + 8, label)
        y += 52
    return y + 10


y = py0 + 116
y = bubble(y, ["📅 Записатися"], mine=True)
y = bubble(y, ["Чоловіча стрижка, Вт 06.10", "Оберіть час:"])
y = buttons(y, [["10:00", "11:00", "12:30", "14:00"], ["15:30", "16:00", "17:00", "18:00"]])
y = bubble(y, ["🆕 Новий запис #12", "Стрижка, Вт 06.10 о 14:00", "Іван, +380 67 123 45 67"])
y = buttons(y, [["✅ Підтвердити", "❌ Скасувати"]])
bubble(y, ["⏰ Через 2 години, о 14:00…"])

img.save(OUT, optimize=True)
print(OUT, img.size)
