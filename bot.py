from aiogram.types import InputMediaPhoto
import logging
import asyncio
import sqlite3
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto, ReplyKeyboardRemove
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

# 1. Коннектимся к базе
db = sqlite3.connect("database.db", check_same_thread=False)
cursor = db.cursor()

import sqlite3

db = sqlite3.connect("database.db", check_same_thread=False)
cursor = db.cursor()

# создаём таблицу один раз и нормально
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0
)
""")

db.commit()

db.commit()
# Создаем состояние ожидания товара
class AdminStates(StatesGroup):
    waiting_for_product = State()
import os
from aiogram import Bot # или используемая вами библиотека

# Бот будет автоматически брать токен из настроек Render
TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

# ====== БАЗА ======
conn = sqlite3.connect("db.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    qty INTEGER,
    price INTEGER,
    code TEXT
)
""")

conn.commit()


def generate_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


# ====== КРИПТА ТЕКСТ ======
crypto_text = (
    "💳 Оплата криптовалютой:\n\n"

    "USDT (TRC20):\n"
    "TGTSyUEGaK7GAkpACNDi46x47zvr5y1VuX\n\n"

    "USDT (BEP20):\n"
    "0xd06e78f1abf5c33b309cd5b86bca8167ca8d3d6c\n\n"

    "ETH (ERC20):\n"
    "0xd06e78f1abf5c33b309cd5b86bca8167ca8d3d6c\n\n"

    "BTC:\n"
    "15oU1drW3g89P33WZfEau4ow6jWxD4i397\n\n"

    "LTC:\n"
    "LeTmNWe2h9wJm4w7yUCFyeA3xz4BvrtB4W\n\n"

    "TON:\n"
    "UQCvwsHXlQ089m4Ei5RL-GYP19mPIQS5dq24_3FLKWTJE0Ov\n\n"

    "USDT (TON):\n"
    "UQCvwsHXlQ089m4Ei5RL-GYP19mPIQS5dq24_3FLKWTJE0Ov\n\n"
)


# ====== МЕНЮ ======
def main_menu():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Купить аккаунты", callback_data="buy")],
        [InlineKeyboardButton(text="🆘 Поддержка", callback_data="support")],
        [InlineKeyboardButton(text="🛒 Реферальная система", callback_data="ref")],
        [InlineKeyboardButton(text="👤 Профиль", callback_data="profile")]
    ])
    return kb

# ====== СТАРТ ======
@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer_photo(
        "https://i.postimg.cc/TYVPYxDW/photo-2026-05-03-14-34-19.jpg",
        caption="""🎉 Добро пожаловать в Orion Seller Bot! ✨
🌟 Давно хотел приобрести качественные Stripe аккаунты с балансом?
💫 Тебе определенно к нам! ⭐️
🎲 Ниже располагается меню, ознакамливайся!
───────────────────""",
        reply_markup=main_menu()
    )
@dp.message(Command("done"))
async def done_cmd(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        args = message.text.split()
        if len(args) < 3:
            await message.answer("Пиши: /done ID кол-во")
            return

        target_id = int(args[1])
        amount = int(args[2])

        # создаём юзера если нет
        cursor.execute(
            "INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, 0)",
            (target_id,)
        )

        # начисляем баланс
        cursor.execute(
            "UPDATE users SET balance = balance + ? WHERE user_id = ?",
            (amount, target_id)
        )

        db.commit()

        await message.answer(f"✅ Зачислено {amount}$ юзеру {target_id}")

    except Exception as e:
        await message.answer(f"Ошибка: {e}")
# ====== ПРОФИЛЬ ======
@dp.callback_query(F.data == "profile")
async def profile_handler(call: types.CallbackQuery):
    await call.answer()
    user_id = call.from_user.id

    try:
        # создаём пользователя если его нет
        cursor.execute(
            "INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, 0)",
            (user_id,)
        )
        db.commit()

        # баланс
        cursor.execute(
            "SELECT balance FROM users WHERE user_id = ?",
            (user_id,)
        )
        res = cursor.fetchone()
        current_balance = res[0] if res else 0

        # сделки
        try:
            cursor.execute(
                "SELECT COUNT(*), SUM(qty), SUM(price) FROM orders WHERE user_id=?",
                (user_id,)
            )
            data = cursor.fetchone()
            deals = data[0] or 0
            total_qty = data[1] or 0
            total_spent = data[2] or 0
        except:
            deals = total_qty = total_spent = 0

        text = (
            f"👤 Ваш профиль:\n\n"
            f"🆔 ID: {user_id}\n"
            f"💰 Баланс: {current_balance}$\n"
            f"🤝 Сделок: {deals}\n"
            f"🛒 Куплено: {total_qty}\n"
            f"💳 Потрачено: {total_spent}$"
        )

        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu")]
        ])

        media = InputMediaPhoto(
            media="https://i.postimg.cc/L6YYMtnX/photo.jpg",
            caption=text
        )

        await call.message.edit_media(
            media=media,
            reply_markup=kb
        )

    except Exception as e:
        await call.message.answer(f"⚠️ Ошибка профиля: {e}")

# ====== ЦЕНА ======
def get_price(qty):
    if 1 <= qty <= 20:
        return qty * 10
    elif 21 <= qty <= 30:
        return qty * 9
    elif 31 <= qty <= 50:
        return qty * 8


# ====== ПОКУПКА ======
# ====== КУПИТЬ (ОБРАБОТКА СО СМЕНОЙ ФОТО) ======
from aiogram.fsm.context import FSMContext # Убедись, что этот импорт есть вверху

# ====== ПОКУПКА ======
@dp.callback_query(F.data == "buy")
async def buy_handler(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    
    # Очищаем старые данные перед новой покупкой
    await state.clear() 
    
    packs = [1, 3, 5, 10, 20, 30]
    buttons = []
    for p in packs:
        buttons.append([InlineKeyboardButton(text=f"💎 Пак: {p} шт.", callback_data=f"pack_{p}")])
    
    buttons.append([InlineKeyboardButton(text="⬅️ ⱠɆ₣₮ (Назад)", callback_data="back")])
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    new_media = InputMediaPhoto(
        media="https://i.postimg.cc/wT8ygtJR/photo-2026-05-03-14-34-29.jpg", 
        caption=(
            "💳 <b>₴₮ɌƗ₱Ɇ ₴ⱧØ₱ | ВЫБОР ПАКЕТА</b>\n\n"
            "Выбери количество аккаунтов для покупки.\n"
            "<i>Чем больше пак, тем выгоднее цена!</i>"
        ),
        parse_mode="HTML"
    )
    
    await call.message.edit_media(media=new_media, reply_markup=kb)

# ====== ВЫБОР ПАКА ======
@dp.callback_query(F.data.startswith("pack_"))
async def pack_handler(call: types.CallbackQuery, state: FSMContext):
    await call.answer()
    
    qty = int(call.data.split("_")[1])
    price = get_price(qty)
    user = call.from_user

    # Запоминаем данные в память бота
    await state.update_data(ordered_quantity=qty, final_price=price)

    # ОТПРАВЛЯЕМ УВЕДОМЛЕНИЕ ТЕБЕ (АДМИНУ)
    await bot.send_message(
        ADMIN_ID, 
        f"🔔 <b>НОВЫЙ ЗАКАЗ</b>\n\n"
        f"👤 Клиент: @{user.username} (ID: {user.id})\n"
        f"📦 Пак: <b>{qty} шт.</b>\n"
        f"💰 Цена: <b>{price}$</b>",
        parse_mode="HTML"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Получить реквизиты", url="https://t.me/dmitryN1")],
        [InlineKeyboardButton(text="₿ Оплата криптой", callback_data=f"crypto_{qty}")],
        [InlineKeyboardButton(text="⬅️ Назад к пакам", callback_data="buy")]
    ])

    new_media = InputMediaPhoto(
        media="https://i.postimg.cc/ZYDHcxGz/photo-2026-05-05-18-20-59.jpg", 
        caption=(
            f"📦 <b>ДЕТАЛИ ЗАКАЗА</b>\n\n"
            f"🛒 Товар: <code>Stripe Accounts</code>\n"
            f"🔢 Количество: <b>{qty} шт.</b>\n"
            f"💰 К оплате: <b>{price}$</b>\n\n"
            f"<i>Напиши админу для получения реквизитов. После выдачи товара ваш профиль обновится автоматически.</i>"
        ),
        parse_mode="HTML"
    )

    await call.message.edit_media(media=new_media, reply_markup=kb)
# ====== ОБНОВЛЕНИЕ ПРОФИЛЯ (ПОСЛЕ ПОДТВЕРЖДЕНИЯ) ======
@dp.callback_query(F.data == "check_payment")
async def check_payment_handler(call: types.CallbackQuery, state: FSMContext):
    # Достаем данные из памяти
    user_data = await state.get_data()
    qty = user_data.get("ordered_quantity", 0)
    price = user_data.get("final_price", 0)
    
    if qty == 0:
        await call.answer("Ошибка: данные заказа потеряны. Начни сначала.", show_alert=True)
        return

    # ТУТ ДОЛЖНА БЫТЬ ТВОЯ ПРОВЕРКА ОПЛАТЫ (Stripe API или ручная)
    # Если оплата подтверждена (имитация):
    payment_confirmed = True 

    if payment_confirmed:
        # ОБНОВЛЯЕМ БАЗУ ДАННЫХ (замени на свои функции)
        # db.update_user_profile(user_id=call.from_user.id, add_deals=1, add_qty=qty)
        
        await call.message.answer(
            f"🥳 <b>Успешная покупка!</b>\n"
            f"В профиль добавлено сделок: 1\n"
            f"Куплено аккаунтов: {qty} шт.\n"
            f"Списано: {price}$"
        )
        await state.clear() # Очищаем память после успеха
    else:
        await call.answer("Оплата еще не поступила!", show_alert=True)

# ====== КРИПТА ======
# ====== ОПЛАТА КРИПТОЙ (ИТОГОВЫЙ БЛОК) ======
@dp.callback_query(F.data.startswith("crypto_"))
async def crypto(call: types.CallbackQuery):
    await call.answer()
    
    # Вытаскиваем количество из даты (например, crypto_5)
    qty = call.data.split("_")[1] if "_" in call.data else "1"

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Я оплатил", callback_data=f"paid_{qty}")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="buy")]
    ])

    # Смена контента на реквизиты
    await call.message.edit_media(
        media=InputMediaPhoto(
            media="https://i.postimg.cc/dVggxKpg/photo-2026-05-05-18-18-51.jpg", 
            caption=crypto_text, 
            parse_mode="HTML"
        ),
        reply_markup=kb
    )

# ====== НАЖАТИЕ "Я ОПЛАТИЛ" (МЕНЯЕМ ТОЛЬКО ТЕКСТ) ======
@dp.callback_query(F.data.startswith("paid_"))
async def process_paid(call: types.CallbackQuery):
    await call.answer()
    
    # Кнопка возврата, если юзер передумал
    cancel_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Отмена", callback_data="buy")]
    ])

    # МЕНЯЕМ ТОЛЬКО CAPTION (КАРТИНКА НЕ ТРОГАЕТСЯ)
    await call.message.edit_caption(
        caption="📸 <b>ОТПРАВЬТЕ СКРИНШОТ ОПЛАТЫ</b>\n\nПришлите фото чека прямо в этот чат. Я передам его администратору на проверку.",
        parse_mode="HTML",
        reply_markup=cancel_kb
    )
@dp.message(F.photo)
async def handle_screenshot(message: types.Message):
    if message.from_user.id == ADMIN_ID: return
    await message.answer("✅ Чек отправлен админу!")
    admin_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Одобрить", callback_data=f"adm_ok_{message.from_user.id}")],
        [InlineKeyboardButton(text="❌ Отклонить", callback_data=f"adm_no_{message.from_user.id}")]
    ])
    await message.bot.send_photo(chat_id=ADMIN_ID, photo=message.photo[-1].file_id, 
                                 caption=f"Чек от @{message.from_user.username}", reply_markup=admin_kb)
# ====== ПОДДЕРЖКА ======
@dp.callback_query(F.data == "support")
async def support(call: types.CallbackQuery):
    await call.answer()
    
    # 1. СОЗДАЕМ ОБЪЕКТ ДЛЯ СМЕНЫ ФОТО И ТЕКСТА
    new_media = InputMediaPhoto(
        media="https://i.postimg.cc/bNsRK6D4/photo-2026-05-03-07-32-45-(8).jpg", # Вставь сюда ссылку на картинку
        caption=(
            "🛎 <b>НУЖНА ПОМОЩЬ? МЫ НА СВЯЗИ!</b>\n\n"
            "🔹 Менеджер поддержки: @orion_seller\n\n"
            "📌 <b>Правила обращения:</b>\n"
            "✅ Описывай проблему сразу в одном сообщении\n"
            "✅ Прикрепляй скриншот чека, если вопрос по оплате\n"
            "✅ Будь вежлив, и мы решим всё максимально быстро!\n\n"
            "<i>Просто нажми кнопку ниже, чтобы перейти в диалог.</i>"
        ),
        parse_mode="HTML"
    )

    # 2. КНОПКИ
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✉️ Написать в поддержку", url="https://t.me/orion_seller")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
    ])

    # 3. МЕНЯЕМ ВСЁ СООБЩЕНИЕ
    await call.message.edit_media(
        media=new_media,
        reply_markup=kb
    )

# ====== РЕФЕРАЛКА ======
@dp.callback_query(F.data == "ref")
async def ref_handler(call: types.CallbackQuery):
    await call.answer()
    
    # 1. ПОДГОТОВКА НОВОГО КОНТЕНТА (ФОТО + ТЕКСТ)
    # Замени ССЫЛКА_НА_ФОТО_РЕФЕРАЛКИ на свою прямую ссылку (jpg/png)
    new_media = InputMediaPhoto(
        media="https://i.postimg.cc/KcfLqV7c/photo-2026-05-03-07-32-45-(7).jpg", 
        caption=(
            "💰 <b>РЕФЕРАЛЬНАЯ СИСТЕМА | ORION TEAM</b>\n\n"
            "Приглашай друзей и получай <b>10%</b> от каждой их покупки прямо на свой баланс!\n\n"
            "📍 <b>Как это работает?</b>\n"
            "1. Напиши нам в поддержку по кнопке ниже.\n"
            "2. Получи свою уникальную ссылку.\n"
            "3. Скидывай её друзьям или пости в каналах.\n\n"
            "<i>Деньги зачисляются автоматически после каждой успешной сделки твоего реферала!</i>"
        ),
        parse_mode="HTML"
    )

    # 2. КНОПКИ РАЗДЕЛА
    kb = InlineKeyboardMarkup(inline_keyboard=[
        # Ссылка на твой профиль @dmitryN1
        [InlineKeyboardButton(text="🔗 Получить ссылку (ЛС)", url="https://t.me/orion_seller")],
        [InlineKeyboardButton(text="⬅️ Назад в меню", callback_data="back")]
    ])
    
    # 3. МАГИЯ СМЕНЫ: меняем старое фото/текст на новое
    await call.message.edit_media(
        media=new_media,
        reply_markup=kb
    )
# ====== НАЗАД ======
@dp.callback_query(lambda c: c.data == "back")
async def back(call: types.CallbackQuery):
    await call.answer()
    # Убедись, что функция main_menu() тоже возвращает объект InlineKeyboardMarkup новой версии
    await call.message.edit_caption(caption="""🎉 Добро пожаловать в Orion Seller Bot! ✨
🌟 Давно хотел приобрести качественные Stripe аккаунты с балансом?
💫 Тебе определенно к нам! ⭐️
🎲 Ниже располагается меню, ознакамливайся!
───────────────────""", reply_markup=main_menu())
@dp.callback_query_handler(lambda c: c.data == "main_menu")
async def back_to_menu(call: types.CallbackQuery):
    await call.answer()

    await call.message.edit_caption(
        "🏠 Главное меню",
        reply_markup=main_menu()
    )
# Тут все твои функции (профиль, рефка, поддержка и т.д.)

# Вставляем логику кнопок админа
# ====== ОБНОВЛЕННАЯ АДМИНКА (РУЧНАЯ ВЫДАЧА) ======
@dp.callback_query(F.data.startswith("adm_"))
async def admin_control(call: types.CallbackQuery, state: FSMContext):
    data = call.data.split("_")
    action, user_id = data[1], int(data[2])

    if action == "ok":
        # Запоминаем ID счастливчика
        await state.update_data(target_user_id=user_id)
        # Включаем режим ожидания текста от тебя
        await state.set_state(AdminStates.waiting_for_product)
        
        await call.message.answer(f"⌨️ <b>Король писбеов, введи товар для юзера</b> <code>{user_id}</code>:\n(Просто отправь текст с данными аккаунта)")
        await call.answer()

    elif action == "no":
        try:
            await call.bot.send_message(user_id, "❌ <b>Оплата отклонена.</b>\nСвяжитесь с @dmitryN1", parse_mode="HTML")
            await call.message.edit_caption(caption=call.message.caption + "\n\n❌ <b>ОТКЛОНЕНО</b>")
        except:
            await call.answer("Юзер недоступен")
        await call.answer()

# ЭТОТ ХЕНДЛЕР ПЕРЕХВАТИТ ТВОЙ ТЕКСТ И ОТПРАВИТ ЮЗЕРУ
@dp.message(AdminStates.waiting_for_product, F.from_user.id == ADMIN_ID)
async def send_product_manually(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    user_id = user_data.get("target_user_id")
    
    try:
        # Пересылаем твой текст юзеру в красивой обертке
        await message.bot.send_message(
            user_id, 
            f"💎 <b>ВАШ ТОВАР ГОТОВ!</b>\n\n<code>{message.text}</code>\n\nСпасибо за покупку в ORION TEAM!", 
            parse_mode="HTML"
        )
        await message.answer(f"✅ Товар успешно улетел юзеру <code>{user_id}</code>")
    except Exception as e:
        await message.answer(f"❌ Не вышло отправить: {e}")
    
    await state.clear() # Выходим из режима админки

# Команда для тебя: /done ID_КЛИЕНТА КОЛ-ВО
# Пример: /done 123456789 10
@dp.message(Command("done"))
async def complete_order(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        args = message.text.split()
        customer_id = int(args[1])
        quantity = int(args[2])

        # ОБНОВЛЯЕМ БАЗУ (ORION TEAM DB)
        # Здесь мы стучимся в твою БД и добавляем +1 сделку и +кол-во
        await db.update_user_stats(
            user_id=customer_id, 
            add_deals=1, 
            add_items=quantity
        )

        await message.answer(f"✅ Сделка для {customer_id} записана в профиль!")
        await bot.send_message(customer_id, f"🎉 Покупка завершена! В ваш профиль добавлена сделка и {quantity} шт. товара.")
        
    except Exception as e:
        await message.answer(f"Ошибка: пиши /done ID кол-во\n{e}")
# ====== ИТОГОВЫЙ ЗАПУСК ======
async def main():
    print("🚀 ORION TEAM BOT ЗАПУСКАЕТСЯ...")
    try:
        # Очищаем очередь обновлений, чтобы бот не тупил после включения
        await bot.delete_webhook(drop_pending_updates=True)
        # Запускаем прослушивание серверов Telegram
        await dp.start_polling(bot)
    except Exception as e:
        print(f"⚠️ Ошибка при работе: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("❌ Бот выключен.")