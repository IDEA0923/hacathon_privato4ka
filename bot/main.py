import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, html, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

from dbs_div import pg  # Импортируем твой объект базы данных
import env

# Инициализация бота
bot = Bot(token=env.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()

# Определение состояний FSM для регистрации
class Registration(StatesGroup):
    choosing_subject = State()
    entering_class = State()
    entering_region = State()

# Клавиатура для выбора предметов (3 буквы, первая заглавная)
subjects_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Mat"), KeyboardButton(text="Inf")],
        [KeyboardButton(text="Phy"), KeyboardButton(text="Che")],
        [KeyboardButton(text="Bio"), KeyboardButton(text="His")]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

@router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    # Очищаем старые состояния на всякий случай
    await state.clear()
    
    tg_id = message.from_user.id
    
    # Проверяем, есть ли уже пользователь в базе
    user_exists = await pg.aread("SELECT id FROM users WHERE tg_id = $1", tg_id)
    
    if user_exists:
        await message.answer("Ты уже зарегистрирован в системе!")
        return

    # Если пользователя нет, начинаем опрос
    await message.answer(
        f"Привет, {html.bold(message.from_user.full_name)}! Давай пройдем регистрацию.\n"
        "Выбери свой основной предмет из списка:",
        reply_markup=subjects_keyboard
    )
    await state.set_state(Registration.choosing_subject)

@router.message(Registration.choosing_subject)
async def subject_chosen(message: Message, state: FSMContext) -> None:
    # Сохраняем выбранный предмет в контекст FSM
    await state.update_data(subjects=message.text)
    
    await message.answer(
        "Отлично! Теперь введи свой класс (цифрой от 1 до 11):",
        reply_markup=ReplyKeyboardRemove()  # Убираем клавиатуру предметов
    )
    await state.set_state(Registration.entering_class)

@router.message(Registration.entering_class)
async def class_entered(message: Message, state: FSMContext) -> None:
    text = message.text
    
    # Валидация класса (должно быть число от 1 до 11)
    if not text.isdigit() or not (1 <= int(text) <= 11):
        await message.answer("Пожалуйста, введи корректный класс — число от 1 до 11!")
        return
        
    await state.update_data(user_class=int(text))
    
    await message.answer("И последнее: введи номер своего региона (цифрами, например: 77, 50, 78):")
    await state.set_state(Registration.entering_region)

@router.message(Registration.entering_region)
async def region_entered(message: Message, state: FSMContext) -> None:
    text = message.text
    
    # Валидация региона (только цифры, так как в init.sql тип INT)
    if not text.isdigit():
        await message.answer("Номер региона должен состоять только из цифр! Введи, например, 25 для Приморского края:")
        return
        
    user_data = await state.get_data()
    tg_id = message.from_user.id
    
    # ИСПРАВЛЕНО: сохраняем всю строку "Mat", "Inf" целиком, а не первую букву [0]
    subject = user_data['subjects']  
    user_class = user_data['user_class']
    region = int(text)
    
    try:
        # Сохранение данных в PostgreSQL через метод awrite
        await pg.awrite(
            "INSERT INTO users (tg_id, subjects, class, region) VALUES ($1, $2, $3, $4)",
            tg_id, subject, user_class, region
        )
        
        # Завершаем FSM и очищаем сохраненные шаги
        await state.clear()
        
        await message.answer("🎉 Регистрация успешно завершена! Твои данные сохранены.")
        
    except Exception as e:
        logging.error(f"Ошибка при записи пользователя в БД: {e}")
        await message.answer("Произошла ошибка при сохранении данных. Попробуй позже.")

@router.message(Command("profile"))
async def profile_handler(message: Message) -> None:
    """Показать настройки пользователя"""
    tg_id = message.from_user.id
    user_data = await pg.aread("SELECT subjects, class, region FROM users WHERE tg_id = $1", tg_id)
    
    if not user_data:
        await message.answer("Ты ещё не зарегистрирован. Используй /start для регистрации.")
        return
    
    subjects, user_class, region = user_data[0]
    await message.answer(
        f"📋 <b>Твой профиль:</b>\n"
        f"📚 Предметы: {subjects}\n"
        f"🎓 Класс: {user_class}\n"
        f"🌍 Регион: {region}"
    )

@router.message(Command("settings"))
async def settings_handler(message: Message, state: FSMContext) -> None:
    """Изменить настройки пользователя"""
    tg_id = message.from_user.id
    user_exists = await pg.aread("SELECT id FROM users WHERE tg_id = $1", tg_id)
    
    if not user_exists:
        await message.answer("Ты ещё не зарегистрирован. Используй /start для регистрации.")
        return
    
    await state.clear()
    await message.answer(
        "⚙️ <b>Настройки:</b>\n"
        "Чтобы изменить данные, пройди регистрацию заново командой /start\n"
        "Текущие данные будут заменены новыми."
    )
    await state.set_state(Registration.choosing_subject)
    await message.answer(
        "Выбери свой основной предмет из списка:",
        reply_markup=subjects_keyboard
    )

@router.message(Command("help"))
async def help_handler(message: Message) -> None:
    """Справка по командам бота"""
    await message.answer(
        f"ℹ️ <b>Справка по командам:</b>\n\n"
        f"/start — Начать регистрацию или пройти её заново\n"
        f"/profile — Показать твои текущие настройки\n"
        f"/settings — Изменить настройки (предметы, класс, регион)\n"
        f"/help — Показать эту справку\n\n"
        f"Бот помогает подобрать подходящие олимпиады на основе твоих данных."
    )
        
async def main() -> None:
    # Важно: подключаемся к БД перед запуском бота
    await pg.connect()
    
    # Создаем таблицу, если её нет (используя синтаксис asyncpg с плейсхолдерами, 
    # но для DDL запросов без параметров можно писать чистый SQL)
    
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")
