"""Portfolio cover for the booking bot: the real v2 interface over the shop photo. 1280x800, Pillow.

Drawn at 2x and scaled down, so rounded corners and text edges stay smooth.
Run: python deploy/make_cover.py
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).with_name("cover-booking-bot.png")
S = 2                                    # supersampling factor
W, H = 1280 * S, 800 * S
F = "C:/Windows/Fonts/"

INK = (13, 11, 10)
BRASS = (222, 168, 98)
TEXT = (244, 239, 233)
MUTED = (178, 166, 152)
CHAT = (14, 22, 33)
BUBBLE = (24, 37, 51)
BTN = (36, 52, 68)
BTN_TEXT = (226, 236, 245)
BUSY = (96, 112, 128)
QUOTE_BAR = (100, 170, 235)
GREEN = (49, 160, 90)
RED = (214, 72, 68)


def font(name, size):
    return ImageFont.truetype(F + name, size * S)


REG, SEMI, BOLD = "segoeui.ttf", "seguisb.ttf", "segoeuib.ttf"


def px(*v):
    return tuple(int(x * S) for x in v)


# --- background: the shop photo, darkened from the left where the text sits -------
photo = Image.open(ROOT / "assets" / "banner.jpg").convert("RGB")
scale = max(W / photo.width, H / photo.height)
photo = photo.resize((int(photo.width * scale), int(photo.height * scale)), Image.LANCZOS)
photo = photo.crop(((photo.width - W) // 2, (photo.height - H) // 2,
                    (photo.width - W) // 2 + W, (photo.height - H) // 2 + H))
photo = photo.filter(ImageFilter.GaussianBlur(3 * S))

shade = Image.new("L", (W, H))
sd = ImageDraw.Draw(shade)
for x in range(W):
    k = x / W
    sd.line([(x, 0), (x, H)], fill=int(255 * (0.94 - 0.30 * k)))   # 94% dark on the left, 64% on the right
img = Image.composite(Image.new("RGB", (W, H), INK), photo, shade)
d = ImageDraw.Draw(img)

# --- left: what it is -----------------------------------------------------------------
x = 72
d.text(px(x, 92), "TELEGRAM-БОТ  ·  PYTHON  ·  AIOGRAM 3", font=font(SEMI, 19), fill=BRASS)
d.text(px(x, 126), "Бот запису", font=font(BOLD, 62), fill=TEXT)
d.text(px(x, 200), "клієнтів", font=font(BOLD, 62), fill=TEXT)
for i, line in enumerate(["Барбершоп, салон, репетитор: клієнт", "записується за хвилину, власник",
                          "підтверджує в один дотик."]):
    d.text(px(x, 296 + i * 36), line, font=font(REG, 25), fill=MUTED)

features = ["Весь тиждень і весь день: зайняте видно одразу",
            "Нагадування за добу і за 2 години",
            "Заявки власнику з кнопками підтвердження",
            "Українська та англійська, 23 автотести"]
y = 436
for line in features:
    d.rounded_rectangle(px(x, y + 9, x + 14, y + 23), radius=3 * S, fill=BRASS)
    d.text(px(x + 30, y), line, font=font(REG, 23), fill=TEXT)
    y += 46

d.text(px(x, 668), "Демо працює 24/7", font=font(REG, 20), fill=MUTED)
d.text(px(x, 694), "t.me/SoexDemo_Bot", font=font(SEMI, 27), fill=BRASS)

# --- right: the chat, drawn like Telegram's dark theme --------------------------------------
P0X, P0Y, P1X, P1Y = 724, 44, 1218, 756
shadow = Image.new("L", (W, H), 0)
ImageDraw.Draw(shadow).rounded_rectangle(px(P0X + 8, P0Y + 18, P1X + 8, P1Y + 18), radius=40 * S, fill=170)
shadow = shadow.filter(ImageFilter.GaussianBlur(22 * S))
img.paste(Image.new("RGB", (W, H), (0, 0, 0)), mask=shadow)
d = ImageDraw.Draw(img)
d.rounded_rectangle(px(P0X, P0Y, P1X, P1Y), radius=36 * S, fill=CHAT)

# header with the real avatar
d.rounded_rectangle(px(P0X, P0Y, P1X, P0Y + 84), radius=36 * S, fill=BUBBLE)
d.rectangle(px(P0X, P0Y + 50, P1X, P0Y + 84), fill=BUBBLE)
ava = Image.open(ROOT / "assets" / "avatar.jpg").convert("RGB").resize(px(48, 48), Image.LANCZOS)
mask = Image.new("L", ava.size, 0)
ImageDraw.Draw(mask).ellipse((0, 0, *ava.size), fill=255)
img.paste(ava, px(P0X + 22, P0Y + 18), mask)
d.text(px(P0X + 84, P0Y + 18), "Barber Lab Demo", font=font(SEMI, 21), fill=TEXT)
d.text(px(P0X + 84, P0Y + 46), "бот", font=font(REG, 17), fill=MUTED)

PAD = 18
L, R = P0X + PAD, P1X - PAD


def bubble(y, lines, quote=None, width=None):
    """A bot message: plain lines, then an optional quote block with a coloured bar."""
    lh = 28
    h = 16 + lh * len(lines) + (12 + lh * len(quote) + 8 if quote else 0) + 6
    w = width or (R - L)
    d.rounded_rectangle(px(L, y, L + w, y + h), radius=16 * S, fill=BUBBLE)
    cy = y + 10
    for text, f in lines:
        d.text(px(L + 16, cy), text, font=f, fill=TEXT)
        cy += lh
    if quote:
        cy += 6
        qh = lh * len(quote) + 8
        d.rounded_rectangle(px(L + 14, cy, R - 14, cy + qh), radius=6 * S, fill=(30, 48, 66))
        d.rectangle(px(L + 14, cy, L + 18, cy + qh), fill=QUOTE_BAR)
        for i, (label, value) in enumerate(quote):
            qx = L + 30
            d.text(px(qx, cy + 4 + i * lh), label, font=font(SEMI, 18), fill=TEXT)
            lw = d.textlength(label, font=font(SEMI, 18)) / S
            d.text(px(qx + lw + 6, cy + 4 + i * lh), value, font=font(REG, 18), fill=TEXT)
    return y + h + 8


def button_row(y, labels, cols, h=40, gap=6):
    bw = (R - L - gap * (cols - 1)) / cols
    for i, (label, kind) in enumerate(labels):
        r, c = divmod(i, cols)
        bx, by = L + c * (bw + gap), y + r * (h + gap)
        fill = {"green": GREEN, "red": RED}.get(kind, BTN)
        color = BUSY if kind == "busy" else BTN_TEXT
        f = font(SEMI if kind in ("green", "red") else REG, 18)
        d.rounded_rectangle(px(bx, by, bx + bw, by + h), radius=10 * S, fill=fill)
        tw = d.textlength(label, font=f) / S
        d.text(px(bx + (bw - tw) / 2, by + 8), label, font=f, fill=color)
    rows = (len(labels) + cols - 1) // cols
    return y + rows * (h + gap) + 6


y = P0Y + 100
y = bubble(y, [("Крок 3 з 4 · Час", font(BOLD, 19)),
               ("Чоловіча стрижка, Ср 07.10", font(REG, 19)),
               ("Оберіть вільний час:", font(REG, 19))])
slots = [("10:00", ""), ("10:30", ""), ("зайнято", "busy"), ("зайнято", "busy"),
         ("12:00", ""), ("зайнято", "busy"), ("13:00", ""), ("13:30", "")]
y = button_row(y, slots, cols=4, h=38)
y = button_row(y, [("Назад", "")], cols=1, h=38) + 10

y = bubble(y, [("Новий запис #12", font(BOLD, 19))],
           quote=[("Послуга:", "Чоловіча стрижка"), ("Коли:", "Ср 07.10 о 12:00"),
                  ("Ціна:", "500 грн"), ("Контакт:", "Іван, +380 67 123 45 67")])
y = button_row(y, [("Підтвердити", "green"), ("Скасувати", "red")], cols=2, h=42) + 8

bubble(y, [("Нагадування", font(BOLD, 19)), ("Через 2 години, о 12:00, у вас стрижка.", font(REG, 18))])

img = img.resize((W // S, H // S), Image.LANCZOS)
img.save(OUT, optimize=True)
print(OUT, img.size)
