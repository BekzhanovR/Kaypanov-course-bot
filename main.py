import logging
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

API_TOKEN = '7196404290:AAEfMsF19JDtW_jYKu93Wth4gAoXfEO5G_U'
CHANNEL_ID = '-1001947869008'
ADMIN_USER_ID = 1418543797  

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

class SurveyStates(StatesGroup):
    name = State()
    phone = State()

# Boshlang'ich tugmalar
start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
start_button = KeyboardButton('/start')
start_keyboard.add(start_button)

# Ma'lumotlar bazasini yaratish va ulash
conn = sqlite3.connect('survey_data.db')
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS survey (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    phone TEXT NOT NULL
)
""")
conn.commit()

async def check_membership(user_id):
    member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
    return member.is_chat_member()

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    inline_kb = InlineKeyboardMarkup(row_width=1)
    inline_btn1 = InlineKeyboardButton('Kanalǵa aǵza bolıń', url=f'https://t.me/azamatkaypanov')
    inline_btn2 = InlineKeyboardButton('Aǵza boldım', callback_data='check_sub')
    inline_kb.add(inline_btn1, inline_btn2)
    
    if message.from_user.id == ADMIN_USER_ID:
        await message.reply("Sálem admin! Siz admin funksiyalarınan paydalanıwıńız múmkin.", reply_markup=admin_keyboard())
    else:
        await message.reply("Sálem! botımızǵa xosh kelipsiz. Botdan paydalanıw ushın aldın kanalımızǵa aǵza bolıń.", reply_markup=inline_kb)

def admin_keyboard():
    admin_kb = InlineKeyboardMarkup(row_width=1)
    admin_btn1 = InlineKeyboardButton('Paydalanıwshılar dizimin kóriw', callback_data='view_users')
    admin_kb.add(admin_btn1)
    return admin_kb

@dp.callback_query_handler(lambda c: c.data == 'check_sub')
async def process_callback_button1(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if await check_membership(user_id):
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, "Kanalǵa aǵza bolǵanıńız ushın raxmet! Sorawnamanı baslaw ushın /basla buyrıǵın jiberiń.")
    else:
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, "Siz ele kanalǵa aǵza bolmadıńız. Iltimas, aldın kanalǵa aǵza bolıń.")

@dp.callback_query_handler(lambda c: c.data == 'view_users')
async def process_view_users(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id == ADMIN_USER_ID:
        cursor.execute("SELECT * FROM survey")
        rows = cursor.fetchall()
        response = "Paydalanıwshılar dizimi:\n"
        for row in rows:
            response += f"ID: {row[0]} \n, Familya atı: {row[2]} \n, Telefon nomer: {row[3]}\n"
        await bot.send_message(callback_query.from_user.id, response)
    else:
        await bot.send_message(callback_query.from_user.id, "Siz admin emessiz!")


@dp.message_handler(commands=['basla'])
async def start_survey(message: types.Message):
    if await check_membership(message.from_user.id):
        await message.reply("Familiya, atıńızdi kiritiń:")
        await SurveyStates.name.set()
    else:
        inline_kb = InlineKeyboardMarkup(row_width=1)
        inline_btn1 = InlineKeyboardButton('Kanalǵa aǵza bolıń', url=f'https://t.me/{CHANNEL_ID}')
        inline_btn2 = InlineKeyboardButton('Aǵza boldım', callback_data='check_sub')
        inline_kb.add(inline_btn1, inline_btn2)
        
        await message.reply("Iltimas, aldın kanalımızǵa aǵza bolıń.", reply_markup=inline_kb)

@dp.message_handler(state=SurveyStates.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.reply("Familiya, atıńızdi kiritiń:")
    await SurveyStates.next()

@dp.message_handler(state=SurveyStates.phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    user_data = await state.get_data()
    
    cursor.execute("INSERT INTO survey (user_id, name, phone) VALUES (?, ?, ?)",
                   (message.from_user.id, user_data['name'], user_data['phone']))
    conn.commit()
    
    inline_kb_video = InlineKeyboardMarkup(row_width=1)
    inline_btn_video = InlineKeyboardButton('Video kóriw', url="https://t.me/+pqFnC79JPQxmNzAy")
    inline_kb_video.add(inline_btn_video)

    await state.finish()
    await message.reply(f"Raxmet!  Maǵlıwmatlar qabıl qılındı:\n\n", reply_markup=inline_kb_video)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)