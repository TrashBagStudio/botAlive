

import asyncio
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import (
    Message,
    CallbackQuery,
    FSInputFile,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InputMediaPhoto,
)
from aiogram.filters import CommandStart

TOKEN = "8870600936:AAFm31YV9_aC-jvciKJ-1YgIeVwAf7QZIew"

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

# =========================
# MOCK DATA
# =========================

user_data = {}

locations = {
    "ru": "🇷🇺 Россия",
    "de": "🇩🇪 Германия",
    "us": "🇺🇸 США",
    "nl": "🇳🇱 Нидерланды",
}

periods = {
    "1m": "1 месяц",
    "3m": "3 месяца",
    "12m": "12 месяцев",
}

period_multipliers = {
    "1m": 1,
    "3m": 2.7,
    "12m": 9.6,
}

PHOTO_PATH = "rathub.png"


# =========================
# HELPERS
# =========================

def get_user_config(user_id):
    if user_id not in user_data:
        user_data[user_id] = {
            "location": "ru",
            "period": "1m",
            "traffic": 10,
            "registered": datetime.now().strftime("%d.%m.%Y"),
            "accepted_rules": False
        }

    return user_data[user_id]


def calc_price(traffic, period):
    base_price = 0.175 * traffic
    multiplier = period_multipliers.get(period, 1)

    return round(base_price * multiplier, 2)


async def edit_photo_menu(message, caption, keyboard):
    media = InputMediaPhoto(
        media=FSInputFile(PHOTO_PATH),
        caption=caption,
        parse_mode="HTML"
    )

    await message.edit_media(
        media=media,
        reply_markup=keyboard
    )


# =========================
# MAIN MENU
# =========================

def main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🛒 Купить",
                    callback_data="buy",
                    style='success'
                ),
            ],

            [
                InlineKeyboardButton(
                    text="👤 Профиль",
                    callback_data="profile",
                    style='primary'

                ),
                InlineKeyboardButton(
                    text="💬 Поддержка",
                    callback_data="support",
                    style='danger'
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📰 Новости",
                    callback_data="news"
                ),
                InlineKeyboardButton(
                    text="ℹ️ Инфо",
                    callback_data="info"

                ),
            ]

        ]
    )


def main_menu_text():
    return """
<b>⚡ RatVad HUB</b>

Добро пожаловать в магазин VPN конфигураций VLESS.

🔥 Быстро
🔒 Безопасно
🌍 Анонимно

Выберите нужный раздел ниже.
"""


# =========================
# AGREEMENT
# =========================

def agreement_accept_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Да, принимаю",
                    callback_data="accept_rules"
                )
            ]
        ]
    )


# =========================
# BUY MENU
# =========================

def buy_menu(user_id):
    data = get_user_config(user_id)

    price = calc_price(
        data["traffic"],
        data["period"]
    )

    text = f"""
<b>⚡ RatVad HUB VPN</b>

<b>Локация:</b> {locations[data["location"]]}
<b>Период:</b> {periods[data["period"]]}
<b>Трафик:</b> {data["traffic"]} GB
<b>Цена:</b> {price}$

━━━━━━━━━━━━━━━

🚀 VLESS конфигурация
🔒 Высокая скорость
🌍 Стабильное подключение
📡 Поддержка всех устройств
"""

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"Локация: {locations[data['location']].split()[0]}",
                    callback_data="locations"
                ),
                InlineKeyboardButton(
                    text=periods[data["period"]],
                    callback_data="periods"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="-",
                    callback_data="minus"
                ),
                InlineKeyboardButton(
                    text=f"{data['traffic']} GB",
                    callback_data="none"
                ),
                InlineKeyboardButton(
                    text="+",
                    callback_data="plus"
                ),
            ],
            [
                InlineKeyboardButton(
                    text=f"{price}$",
                    callback_data="price"
                ),
                InlineKeyboardButton(
                    text="🛒 Заказать",
                    callback_data="order"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="main"
                ),
            ]
        ]
    )

    return text, kb


# =========================
# PROFILE
# =========================

def profile_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="💳 История пополнений",
                    callback_data="history"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💰 Пополнить",
                    callback_data="deposit"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💬 Поддержка",
                    callback_data="profile_support"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📄 Пользовательское соглашение",
                    callback_data="agreement"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔒 Политика конфиденциальности",
                    callback_data="privacy"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="main"
                )
            ]
        ]
    )


# =========================
# START
# =========================

@dp.message(CommandStart())
async def start(message: Message):
    data = get_user_config(message.from_user.id)

    photo = FSInputFile(PHOTO_PATH)

    if not data["accepted_rules"]:
        await message.answer_photo(
            photo=photo,
            caption=(
                "<b>Добро пожаловать</b>\n\n"
                "Продолжая использование бота, "
                "вы соглашаетесь с политикой "
                "конфиденциальности и "
                "пользовательским соглашением."
            ),
            reply_markup=agreement_accept_menu()
        )
        return

    await message.answer_photo(
        photo=photo,
        caption=main_menu_text(),
        reply_markup=main_menu()
    )


# =========================
# ACCEPT RULES
# =========================

@dp.callback_query(F.data == "accept_rules")
async def accept_rules(callback: CallbackQuery):
    data = get_user_config(callback.from_user.id)

    data["accepted_rules"] = True

    await edit_photo_menu(
        callback.message,
        main_menu_text(),
        main_menu()
    )

    await callback.answer("Соглашение принято")


# =========================
# MAIN MENU
# =========================

@dp.callback_query(F.data == "main")
async def back_main(callback: CallbackQuery):
    await edit_photo_menu(
        callback.message,
        main_menu_text(),
        main_menu()
    )

    await callback.answer()


# =========================
# BUY
# =========================

@dp.callback_query(F.data == "buy")
async def buy(callback: CallbackQuery):
    text, kb = buy_menu(callback.from_user.id)

    await edit_photo_menu(
        callback.message,
        text,
        kb
    )

    await callback.answer()


@dp.callback_query(F.data == "plus")
async def plus(callback: CallbackQuery):
    data = get_user_config(callback.from_user.id)

    if data["traffic"] < 100:
        data["traffic"] += 10

    text, kb = buy_menu(callback.from_user.id)

    await callback.message.edit_caption(
        caption=text,
        reply_markup=kb
    )

    await callback.answer()


@dp.callback_query(F.data == "minus")
async def minus(callback: CallbackQuery):
    data = get_user_config(callback.from_user.id)

    if data["traffic"] > 10:
        data["traffic"] -= 10

    text, kb = buy_menu(callback.from_user.id)

    await callback.message.edit_caption(
        caption=text,
        reply_markup=kb
    )

    await callback.answer()


# =========================
# LOCATIONS
# =========================

@dp.callback_query(F.data == "locations")
async def locations_menu(callback: CallbackQuery):

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🇷🇺 Россия",
                    callback_data="loc_ru"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🇩🇪 Германия",
                    callback_data="loc_de"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🇺🇸 США",
                    callback_data="loc_us"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🇳🇱 Нидерланды",
                    callback_data="loc_nl"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="buy"
                )
            ]
        ]
    )

    await callback.message.edit_caption(
        caption="<b>🌍 Выберите локацию</b>",
        reply_markup=kb
    )

    await callback.answer()


@dp.callback_query(F.data.startswith("loc_"))
async def set_location(callback: CallbackQuery):
    data = get_user_config(callback.from_user.id)

    loc = callback.data.split("_")[1]

    data["location"] = loc

    text, kb = buy_menu(callback.from_user.id)

    await callback.message.edit_caption(
        caption=text,
        reply_markup=kb
    )

    await callback.answer("Локация изменена")


# =========================
# PERIODS
# =========================

@dp.callback_query(F.data == "periods")
async def periods_menu(callback: CallbackQuery):

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="1 месяц",
                    callback_data="per_1m"
                )
            ],
            [
                InlineKeyboardButton(
                    text="3 месяца",
                    callback_data="per_3m"
                )
            ],
            [
                InlineKeyboardButton(
                    text="12 месяцев",
                    callback_data="per_12m"
                )
            ],
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data="buy"
                )
            ]
        ]
    )

    await callback.message.edit_caption(
        caption="<b>⏳ Выберите период</b>",
        reply_markup=kb
    )

    await callback.answer()


@dp.callback_query(F.data.startswith("per_"))
async def set_period(callback: CallbackQuery):
    data = get_user_config(callback.from_user.id)

    period = callback.data.split("_")[1]

    data["period"] = period

    text, kb = buy_menu(callback.from_user.id)

    await callback.message.edit_caption(
        caption=text,
        reply_markup=kb
    )

    await callback.answer("Период изменён")


# =========================
# ORDER
# =========================

@dp.callback_query(F.data == "order")
async def order(callback: CallbackQuery):
    await callback.answer(
        "❌ Недостаточно денег на балансе",
        show_alert=True
    )


# =========================
# PROFILE
# =========================

@dp.callback_query(F.data == "profile")
async def profile(callback: CallbackQuery):

    user = callback.from_user
    data = get_user_config(user.id)

    username = user.username if user.username else "Нет"

    text = f"""
<b>👤 Профиль</b>

<b>Username:</b> @{username}
<b>ID:</b> <code>{user.id}</code>
<b>Дата регистрации:</b> {data["registered"]}

<b>Баланс:</b> 0$
"""

    await edit_photo_menu(
        callback.message,
        text,
        profile_menu()
    )

    await callback.answer()


# =========================
# SIMPLE PAGE
# =========================

async def simple_page(callback, title, text, back_callback="main"):

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⬅️ Назад",
                    callback_data=back_callback
                )
            ]
        ]
    )

    await edit_photo_menu(
        callback.message,
        f"<b>{title}</b>\n\n{text}",
        kb
    )

    await callback.answer()


# =========================
# SIMPLE PAGES
# =========================

@dp.callback_query(F.data == "info")
async def info(callback: CallbackQuery):
    await simple_page(
        callback,
        "ℹ️ Информация",
        "RatVad HUB — сервис продажи VPN конфигураций VLESS.\n"
        "Политика конфиденциальности:\nhttps://telegra.ph/Politika-konfidencialnosti-04-01-26\n\n"
        "Пользовательское соглашение:\nhttps://telegra.ph/Polzovatelskoe-soglashenie-04-01-19"
    )


@dp.callback_query(F.data == "news")
async def news(callback: CallbackQuery):
    await simple_page(
        callback,
        "📰 Новости",
        "Новостей пока нет."
    )


@dp.callback_query(F.data == "support")
async def support(callback: CallbackQuery):
    await simple_page(
        callback,
        "💬 Поддержка",
        "@RatVadSupport"
    )


@dp.callback_query(F.data == "profile_support")
async def profile_support(callback: CallbackQuery):
    await simple_page(
        callback,
        "💬 Поддержка",
        "@RatVadSupport",
        back_callback="profile"
    )


@dp.callback_query(F.data == "history")
async def history(callback: CallbackQuery):
    await simple_page(
        callback,
        "💳 История пополнений",
        "История пополнений пуста.",
        back_callback="profile"
    )


@dp.callback_query(F.data == "deposit")
async def deposit(callback: CallbackQuery):
    await callback.answer(
        "Пополнение пока недоступно",
        show_alert=True
    )


@dp.callback_query(F.data == "agreement")
async def agreement(callback: CallbackQuery):
    await simple_page(
        callback,
        "📄 Пользовательское соглашение",
        "https://telegra.ph/Polzovatelskoe-soglashenie-04-01-19",
        back_callback="profile"
    )


@dp.callback_query(F.data == "privacy")
async def privacy(callback: CallbackQuery):
    await simple_page(
        callback,
        "🔒 Политика конфиденциальности",
        "https://telegra.ph/Politika-konfidencialnosti-04-01-26",
        back_callback="profile"
    )


# =========================
# EMPTY BUTTONS
# =========================

@dp.callback_query(F.data.in_(["none", "price"]))
async def empty_callbacks(callback: CallbackQuery):
    await callback.answer()


# =========================
# RUN
# =========================

async def main():
    print("RatVad HUB started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

