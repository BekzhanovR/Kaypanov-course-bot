import logging
import sqlite3
import pandas as pd
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.utils import executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage

API_TOKEN = '7196404290:AAEfMsF19JDtW_jYKu93Wth4gAoXfEO5G_U'
CHANNEL_ID = '-1001947869008'
ADMIN_USER_ID = 1418543797  # Admin foydalanuvchi ID'sini bu yerga yozing

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
dp.middleware.setup(LoggingMiddleware())

class SurveyStates(StatesGroup):
    name = State()
    phone = State()
    age = State()
    city = State()
    business = State()
    source = State()
    course = State()
    reason = State()

# Boshlang'ich tugmalar
start_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
start_button = KeyboardButton('/start')
start_keyboard.add(start_button)

# Sorovnoma tugmalari
age_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
age_buttons = ["18-24", "25-34", "35-44", "44-54", "55-60"]
age_keyboard.add(*age_buttons)

city_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
city_buttons = ["Nukus shahri", "Xojeli", "Taxiyatash", "Shimbay", "Qon'irat", "Shomanay", "Qanliko'l", "Kegeyli", "To'rtko'l", "Taxtako'pir", "Moynaq", "Bozataw", "Beruniy", "Amudarya", "No'kis rayon"]
city_keyboard.add(*city_buttons)

business_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
business_buttons = ["Sovda-sotiq", "Xizmmat ko'rsatish", "Ishlab shiqish", "Ta'lim", "boshqa"]
business_keyboard.add(*business_buttons)

source_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
source_buttons = ["Telegram", "Instagram", "Facebook", "Websayt", "Boshqa"]
source_keyboard.add(*source_buttons)

course_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
course_buttons = ["Ha", "Yoq"]
course_keyboard.add(*course_buttons)

reason_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
reason_buttons = ["Kópten beri kúzeter edim. Sabaqlıqtı kútip júr edim.", "Oqıǵım kelip júr baslanǵısh maǵlıwmatlardı aldım.", "Maǵan biznes boyınsha real keysler unaydı."]
reason_keyboard.add(*reason_buttons)

# Ma'lumotlar bazasini yaratish va ulash
conn = sqlite3.connect('survey_data.db')
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS survey (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    age TEXT NOT NULL,
    city TEXT NOT NULL,
    business TEXT NOT NULL,
    source TEXT NOT NULL,
    course TEXT NOT NULL,
    reason TEXT NOT NULL
)
""")
conn.commit()

async def check_membership(user_id):
    member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
    return member.is_chat_member()

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    inline_kb = InlineKeyboardMarkup(row_width=1)
    inline_btn1 = InlineKeyboardButton('Kanalga obuna bo\'ling', url=f'https://t.me/azamatkaypanov')
    inline_btn2 = InlineKeyboardButton('Obuna bo\'ldim', callback_data='check_sub')
    inline_kb.add(inline_btn1, inline_btn2)
    
    if message.from_user.id == ADMIN_USER_ID:
        await message.reply("Salom admin! Siz admin funksiyalaridan foydalanishingiz mumkin.", reply_markup=admin_keyboard())
    else:
        await message.reply("Salom! Botimizga xush kelibsiz. Botdan foydalanish uchun avval kanalimizga obuna bo'ling.", reply_markup=inline_kb)

def admin_keyboard():
    admin_kb = InlineKeyboardMarkup(row_width=1)
    admin_btn1 = InlineKeyboardButton('Foydalanuvchilar ro\'yxatini ko\'rish', callback_data='view_users')
    admin_kb.add(admin_btn1)
    return admin_kb

@dp.callback_query_handler(lambda c: c.data == 'check_sub')
async def process_callback_button1(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if await check_membership(user_id):
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, "Kanalga obuna bo'lganingiz uchun rahmat! Sorovnomani boshlash uchun /boshla buyrug'ini yuboring.")
    else:
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, "Siz hali kanalga obuna bo'lmadingiz. Iltimos, avval kanalga obuna bo'ling.")

@dp.callback_query_handler(lambda c: c.data == 'view_users')
async def process_view_users(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    if user_id == ADMIN_USER_ID:
        cursor.execute("SELECT * FROM survey")
        rows = cursor.fetchall()
        response = "Foydalanuvchilar ro'yxati:\n"
        for row in rows:
            response += f"ID: {row[0]} \n, Familya ismi: {row[2]} \n, Telefon raqami: {row[3]} \n, Yoshi: {row[4]} \n, Yashash manzilli: {row[5]} \n, Qanday yo'nalishka qiziqadi: {row[6]} \n, Biz haqimizda qayerdan eshitkan: {row[7]} \n, Oldin kursta oqiganmi: {row[8]} \n, Nima uchun bizni tanlagan: {row[9]}\n"
        await bot.send_message(callback_query.from_user.id, response)
    else:
        await bot.send_message(callback_query.from_user.id, "Siz admin emassiz!")

@dp.message_handler(commands=['survey'])
async def start_survey(message: types.Message):
    if await check_membership(message.from_user.id):
        await message.reply("Familiya, ismingizni kiriting:")
        await SurveyStates.name.set()
    else:
        inline_kb = InlineKeyboardMarkup(row_width=1)
        inline_btn1 = InlineKeyboardButton('Kanalga obuna bo\'ling', url=f'https://t.me/{CHANNEL_ID}')
        inline_btn2 = InlineKeyboardButton('Obuna bo\'ldim', callback_data='check_sub')
        inline_kb.add(inline_btn1, inline_btn2)
        
        await message.reply("Iltimos, avval kanalimizga obuna bo'ling.", reply_markup=inline_kb)

@dp.message_handler(state=SurveyStates.name)
async def process_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.reply("Telefon raqamingizni kiriting:")
    await SurveyStates.next()

@dp.message_handler(state=SurveyStates.phone)
async def process_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await message.reply("Yoshingizni tanlang:", reply_markup=age_keyboard)
    await SurveyStates.next()

@dp.message_handler(state=SurveyStates.age)
async def process_age(message: types.Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.reply("Yashash manzilingizni tanlang:", reply_markup=city_keyboard)
    await SurveyStates.next()

@dp.message_handler(state=SurveyStates.city)
async def process_city(message: types.Message, state: FSMContext):
    await state.update_data(city=message.text)
    await message.reply("Qanday biznes turiga qiziqasiz?", reply_markup=business_keyboard)
    await SurveyStates.next()

@dp.message_handler(state=SurveyStates.business)
async def process_business(message: types.Message, state: FSMContext):
    await state.update_data(business=message.text)
    await message.reply("Biz haqimizda qayerdan eshitdingiz?", reply_markup=source_keyboard)
    await SurveyStates.next()

@dp.message_handler(state=SurveyStates.source)
async def process_source(message: types.Message, state: FSMContext):
    await state.update_data(source=message.text)
    await message.reply("Oldin kurslarimizda o'qidingizmi?", reply_markup=course_keyboard)
    await SurveyStates.next()

@dp.message_handler(state=SurveyStates.course)
async def process_course(message: types.Message, state: FSMContext):
    await state.update_data(course=message.text)
    await message.reply("Nima uchun bizni tanladingiz?", reply_markup=reason_keyboard)
    await SurveyStates.next()

@dp.message_handler(state=SurveyStates.reason)
async def process_reason(message: types.Message, state: FSMContext):
    await state.update_data(reason=message.text)
    user_data = await state.get_data()
    
    cursor.execute("INSERT INTO survey (user_id, name, phone, age, city, business, source, course, reason) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   (message.from_user.id, user_data['name'], user_data['phone'], user_data['age'], user_data['city'], user_data['business'], user_data['source'], user_data['course'], user_data['reason']))
    conn.commit()
    
    video_btn = InlineKeyboardButton("Video darslarni ko'rish", url='https://t.me/+pqFnC79JPQxmNzAy')

    await message.reply(f"Rahmat! Ma'lumotlaringiz qabul qilindi:\n\n", reply_markup=video_btn)
    await state.finish()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)