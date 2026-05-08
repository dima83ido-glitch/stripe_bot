import os
import logging
import asyncio
import sqlite3
import random
import string
from keep_alive import keep_alive
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import BotCommand, BotCommandScopeDefault

async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command='/start', description='Старт'),
        BotCommand(command='/buy', description='Купить аккаунты'),
        BotCommand(command='/support', description='Поддержка'),
        BotCommand(command='/ref', description='Реферальная система'),
        BotCommand(command='/deals', description='Профиль')
    ]
    await bot.set_my_commands(main_menu_commands, scope=BotCommandScopeDefault())

# 1. ЗАПУСК И КОНФИГ
load_dotenv()
keep_alive()

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID")) if os.getenv("ADMIN_ID") else 0

bot = Bot(token=TOKEN)
dp = Dispatcher()
logging.basicConfig(level=logging.INFO)

# 2. БАЗА ДАННЫХ (ЕДИНАЯ)
db = sqlite3.connect("orion_main.db", check_same_thread=False)
cursor = db.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0,
    deals INTEGER DEFAULT 0,
    bought_items INTEGER DEFAULT 0,
    spent INTEGER DEFAULT 0
)
""")
db.commit()

# 3. СОСТОЯНИЯ (FSM)
class ShopStates(StatesGroup):
    waiting_for_screenshot = State()
    waiting_for_product_data = State() # Для админа

# 4. ТЕКСТЫ И ССЫЛКИ
IMG_MAIN = "https://i.postimg.cc/TYVPYxDW/photo-2026-05-03-14-34-19.jpg"
IMG_BUY = "https://i.postimg.cc/wT8ygtJR/photo-2026-05-03-14-34-29.jpg"
IMG_PAY = "https://i.postimg.cc/ZYDHcxGz/photo-2026-05-05-18-20-59.jpg"
IMG_CRYPTO = "https://i.postimg.cc/dVggxKpg/photo-2026-05-05-18-18-51.jpg"
IMG_SUPPORT = "https://i.postimg.cc/bNsRK6D4/photo-2026-05-03-07-32-45-(8).jpg"
IMG_REF = "https://i.postimg.cc/KcfLqV7c/photo-2026-05-03-07-32-45-(7).jpg"
IMG_PROFILE = "https://i.postimg.cc/L6YYMtnX/photo.jpg"

CRYPTO_REQUISITES = (
    "<b>💳 Реквизиты для оплаты:</b>\n\n"
    
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

# 5. КЛАВИАТУРЫ
def kb_main():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛒 Купить аккаунты", callback_data="buy")],
        [InlineKeyboardButton(text="👤 Профиль", callback_data="profile"), InlineKeyboardButton(text="💰 Рефералка", callback_data="ref")],
        [InlineKeyboardButton(text="🆘 Поддержка", callback_data="support")]
    ])

def kb_back():
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]])

# 6. ХЕНДЛЕРЫ МЕНЮ
@dp.message(Command("start"))
async def start(message: types.Message):
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (message.from_user.id,))
    db.commit()
    await message.answer_photo(IMG_MAIN, caption="""🎉 Добро пожаловать в Orion Seller Bot! ✨
🌟 Давно хотел приобрести качественные Stripe аккаунты с балансом?
💫 Тебе определенно к нам! ⭐️
🎲 Ниже располагается меню, ознакамливайся!
───────────────────""", reply_markup=kb_main(), parse_mode="HTML")

@dp.callback_query(F.data == "back_to_main")
async def back_main(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_media(InputMediaPhoto(media=IMG_MAIN, caption="""🎉 Добро пожаловать в Orion Seller Bot! ✨
🌟 Давно хотел приобрести качественные Stripe аккаунты с балансом?
💫 Тебе определенно к нам! ⭐️
🎲 Ниже располагается меню, ознакамливайся!
───────────────────"""), reply_markup=kb_main())

# 7. РАЗДЕЛ ПОКУПКИ
@dp.callback_query(F.data == "buy")
async def buy_packs(call: types.CallbackQuery):
    packs = [1, 5, 10, 20, 30, 50]
    buttons = [[InlineKeyboardButton(text=f"💎 Пак: {p} шт.", callback_data=f"order_{p}")] for p in packs]
    buttons.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")])
    await call.message.edit_media(InputMediaPhoto(media=IMG_BUY, caption="""🛒 Шаг 1 из 3... Выбор количества для покупки

🌟 Решил купить аккаунты? Ты на верном пути! ✈️

🎯 Наши преимущества:
✅ Гарантия возврата в случаи невалидности 🔮
✅ Платежные системы высшего уровня 💾
✅ Удобные способы оплаты 📥
✅ Быстрая тех поддержка 📞

💎 Прайс лист на аккаунты:
💎 1-20 шт → 10$ за аккаунт
🚀 21-50 шт → 9$ за аккаунт

🎯 Выбери уже готовый пак!"""), reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons))

@dp.callback_query(F.data.startswith("order_"))
async def choose_pay(call: types.CallbackQuery, state: FSMContext):
    qty = int(call.data.split("_")[1])
    price = qty * 10 if qty <= 20 else qty * 9
    await state.update_data(qty=qty, price=price)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплата картой", url="https://t.me/orion_seller")],
        [InlineKeyboardButton(text="₿ Криптовалютой", callback_data="pay_crypto")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="buy")]
    ])
    await call.message.edit_media(InputMediaPhoto(media=IMG_PAY, caption=f"📦 Заказ: {qty} шт.\n💰 Итого: {price}$"), reply_markup=kb)

@dp.callback_query(F.data == "pay_crypto")
async def pay_crypto(call: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Я оплатил", callback_data="confirm_pay")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="buy")]
    ])
    await call.message.edit_media(InputMediaPhoto(media=IMG_CRYPTO, caption=CRYPTO_REQUISITES), reply_markup=kb)

@dp.callback_query(F.data == "confirm_pay")
async def wait_scr(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(ShopStates.waiting_for_screenshot)
    await call.message.edit_caption(caption="📸 Пришлите скриншот чека оплаты в этот чат:", reply_markup=kb_back())

# 8. ОБРАБОТКА СКРИНШОТА И АДМИНКА
@dp.message(ShopStates.waiting_for_screenshot, F.photo)
async def get_screenshot(message: types.Message, state: FSMContext):
    data = await state.get_data()
    qty, price = data.get('qty'), data.get('price')
    
    await message.answer("<b>✅ Чек принят!</b> Ожидайте проверки админом.", parse_mode="HTML")
    
    kb_adm = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Одобрить", callback_data=f"adm_ok_{message.from_user.id}_{qty}_{price}")],
        [InlineKeyboardButton(text="❌ Отклонить", callback_data=f"adm_no_{message.from_user.id}")]
    ])
    await bot.send_photo(ADMIN_ID, message.photo[-1].file_id, 
                         caption=f"💰 <b>НОВЫЙ ЧЕК</b>\nЮзер: @{message.from_user.username}\nID: {message.from_user.id}\nЗаказ: {qty} шт ({price}$)", 
                         reply_markup=kb_adm, parse_mode="HTML")
    await state.clear()

@dp.callback_query(F.data.startswith("adm_"))
async def admin_action(call: types.CallbackQuery, state: FSMContext):
    params = call.data.split("_")
    action, user_id = params[1], int(params[2])
    
    if action == "ok":
        qty, price = int(params[3]), int(params[4])
        await state.update_data(target=user_id, q=qty, p=price)
        await state.set_state(ShopStates.waiting_for_product_data)
        await call.message.answer(f"⌨️ <b>Введи товар (данные аккаунтов) для {user_id}:</b>", parse_mode="HTML")
    else:
        await bot.send_message(user_id, "❌ <b>Ваша оплата отклонена.</b> Свяжитесь с поддержкой.", parse_mode="HTML")
        await call.message.edit_caption(caption=call.message.caption + "\n\n❌ ОТКЛОНЕНО")
    await call.answer()

@dp.message(ShopStates.waiting_for_product_data, F.from_user.id == ADMIN_ID)
async def send_product(message: types.Message, state: FSMContext):
    data = await state.get_data()
    uid, q, p = data['target'], data['q'], data['p']
    
    # Обновляем БД
    cursor.execute("UPDATE users SET deals = deals + 1, bought_items = bought_items + ?, spent = spent + ? WHERE user_id = ?", (q, p, uid))
    db.commit()
    
    await bot.send_message(uid, f"💎 <b>ВАШ ТОВАР:</b>\n\n<code>{message.text}</code>\n\nСтатистика в профиле обновлена!", parse_mode="HTML")
    await message.answer(f"✅ Товар отправлен юзеру {uid}, статистика обновлена.")
    await state.clear()

# 9. ПРОФИЛЬ, РЕФКА, САППОРТ
@dp.callback_query(F.data == "profile")
async def view_profile(call: types.CallbackQuery):
    cursor.execute("SELECT deals, bought_items, spent FROM users WHERE user_id = ?", (call.from_user.id,))
    res = cursor.fetchone()
    text = f"👤 <b>Профиль:</b>\n🆔 ID: <code>{call.from_user.id}</code>\n🤝 Сделок: {res[0]}\n🛒 Куплено: {res[1]} шт.\n💳 Потрачено: {res[2]}$", parse_mode="HTML"
    await call.message.edit_media(InputMediaPhoto(media=IMG_PROFILE, caption=text), reply_markup=kb_back())

@dp.callback_query(F.data == "support")
async def view_support(call: types.CallbackQuery):
    await call.message.edit_media(InputMediaPhoto(media=IMG_SUPPORT, caption="""🛎️ Нужна помощь? Обращайся правильно!

🔹 Напиши твою проблему нам !
🔹 Менеджер поддержки: @orion_seller

📌 Правила обращения:
✅ Будь вежлив и точен
✅ Не спамь"""), 
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="✉️ Написать", url="https://t.me/orion_seller")],[InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]]))

@dp.callback_query(F.data == "ref")
async def view_ref(call: types.CallbackQuery):
    await call.message.edit_media(InputMediaPhoto(media=IMG_REF, caption="💰 <b>Реферальная система</b>\n\nПолучай 10% с покупок друзей!\nЧтобы получить личную ссылку, напиши менеджеру."), 
                                  reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔗 Получить ссылку", url="https://t.me/orion_seller")],[InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_main")]]))

# 10. ЗАПУСК
async def main():
    print("🚀 ORION TEAM BOT ЗАПУСКАЕТСЯ...")

    # Настраиваем кнопку «Меню» перед запуском опроса
    try:
        await set_main_menu(bot)
        print("✅ Кнопка меню успешно установлена")
    except Exception as e:
        print(f"❌ Ошибка при установке меню: {e}")

    # Удаляем старые сообщения, которые накопились, пока бот был выключен
    await bot.delete_webhook(drop_pending_updates=True)

    # Запускаем бесконечный цикл работы бота
    try:
        await dp.start_polling(bot)
    except Exception as e:
        print(f"⚠️ Критическая ошибка при работе: {e}")
    finally:
        await bot.session.close()
        
if __name__ == "__main__":
    asyncio.run(main())