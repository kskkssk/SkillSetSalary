import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram import F
from aiogram.dispatcher import FSMContext
from aiogram.types import FSInputFile
from aiogram.dispatcher.filters.state import State, StatesGroup
import requests
from worker.tasks import handle_request as celery_handle_request
from worker.celery_config import app
import os
from celery.result import AsyncResult
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)

load_dotenv()

TOKEN = os.getenv('TOKEN')
API_URL = os.getenv('API_URL_TG')

bot = Bot(token=TOKEN)
dp = Dispatcher()
user_tokens = {}


class Registration(StatesGroup):
    email = State()
    password = State()


class Login(StatesGroup):
    email = State()
    password = State()


class Balance(StatesGroup):
    amount = State()


@dp.message(Command('start'))
async def start(message: types.Message):
    kb = [
        [
            types.KeyboardButton(text="Регистрация"),
            types.KeyboardButton(text="Войти в аккаунт")
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )
    await message.answer(f'Привет, {message.from_user.first_name}!, я предскажу зарплату по твоему резюме'
                         , reply_markup=keyboard)


@dp.message(Command('help'))
async def help(message: types.Message):
    await message.answer('Доступные команды:\n'
                         '\start: Начать взаимодействие\n'
                         '\help: Показать справочную информацию')


@dp.message(F.text.lower() == "регистрация", state='None')
async def capture_name(message: types.Message, state: FSMContext):
    await message.answer('Введите email')
    await state.set_state(Registration.email)


@dp.message(F.text, Registration.email)
async def capture_password(message: types.Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.reply('Введите пароль')
    await state.set_state(Registration.password)


async def get_complete_register(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    email = user_data['email']
    password = message.text
    json_raw = {
        "email": email,
        "password": password,
    }
    request = requests.post(url=f"{API_URL}/users/signup/", json=json_raw)
    if request.status_code == 200:
        await message.answer("Вы успешно зарегистрировались!")
    else:
        await message.answer(
                         f"Ошибка регистрации: неверный ответ сервера. Status code: {request.status_code}")
    await state.clear()


@dp.message(F.text.lower() == "войти в аккаунт", state=None)
async def capture_name(message: types.Message, state: FSMContext):
    await message.answer('Введите email')
    await state.set_state(Registration.email)


@dp.message(F.text, Registration.email)
async def capture_password(message: types.Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.reply('Введите пароль')
    await state.set_state(Registration.password)


async def get_complete_login(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    email = user_data['email']
    password = message.text
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    data = {
        'grant_type': 'password',
        'username': email,
        'password': password,
    }

    response = requests.post(f'{API_URL}/users/signin', headers=headers, data=data)
    if response.status_code == 200:
        access_token = response.json().get("access_token")
        user_tokens[message.chat.id] = access_token

        kb = [
            [
                types.KeyboardButton(text="Пополнить баланс"),
                types.KeyboardButton(text="Посмотреть баланс"),
                types.KeyboardButton(text="Сделать запрос"),
                types.KeyboardButton(text="История запросов"),
                types.KeyboardButton(text="Выйти из профиля")
            ],
        ]
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=kb,
            resize_keyboard=True,
            input_field_placeholder="Выберите действие"
        )

        await message.answer("Вы успешно вошли в систему!", reply_markup=keyboard)

    elif response.status_code == 500:
        await message.answer("Неправильный пользователь или пароль. Попробуйте еще раз.")
    else:
        await message.answer(f"Ошибка входа: {response.json().get('detail', 'Ошибка входа')}")
    await state.clear()


@dp.message(F.text.lower() == 'пополнить баланс')
async def add_money(message: types.Message):
    await message.answer('Введите сумму')


@dp.message(F.text.lower() == 'посмотреть баланс')
async def get_balance(message: types.Message):
    request = requests.get(f"{API_URL}/balances/balance")
    if request.status_code == 200:
        balance = request.json().get('amount')
        await message.answer(f'Ваш баланс: {balance}')
    elif request.status_code == 500:
        await message.answer("Вы не авторизованы. Пожалуйста, войдите в аккаунт.")
    else:
        await message.answer(f"Ошибка: {request.json().get('detail', 'Ошибка')}")


@dp.message(F.text.lower() == 'сделать запрос', content_types=['document'])
async def handle_docs(message: types.Message):
    try:
        if message.document.mime_type != 'application/pdf':
            await message.reply("Пожалуйста, загрузите файл в формате PDF.")
            return

        file_info = await bot.get_file(message.document.file_id)
        downloaded_file = await bot.download_file(file_info.file_path)
        src = f'./telegram_bot/files/{message.document.file_name}'
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        await message.reply("Файл принят в обработку")
        return new_file

    except requests.exceptions.RequestException as e:
        await message.reply(f"Ошибка при загрузке файла: {e}")
    except Exception as e:
        await message.reply(f"Произошла ошибка: {e}")


def format_prediction():
    pass


async def handle_request(message: types.Message):
    data = handle_docs
    response = requests.get(f"{API_URL}/users/current_user")
    if response.status_code == 200:
        user_data = response.json()
        current_user = user_data.get("username")
    else:
        await message.answer("Вы не авторизованы. Пожалуйста, войдите в аккаунт.")
        return None

    task_id = celery_handle_request.apply_async(args=[data, current_user])
    result = AsyncResult(task_id, app=app)
    await message.answer(result)


@dp.message(F.text.lower() == 'история запросов')
async def transaction_history(message: types.Message):
    response = requests.get(url=f"{API_URL}/users/transaction_history")
    if response.status_code == 200:
        transactions = response.json()
        for transaction in transactions:
            await message.answer(
                             f"Дата: {transaction['data']}\nПрогноз: {transaction['prediction']}\nПотрачено: {transaction['spent_money']}")
    elif response.status_code == 500:
        await message.answer("Вы не авторизованы. Пожалуйста, войдите в аккаунт.")
    else:
        await message.answer(
                         f"Ошибка получения истории: {response.json().get('detail', 'Ошибка получения истории')}")


@dp.message(F.text.lower() == 'выйти из профиля')
async def logout(message: types.Message):
    request = requests.post(url=f"{API_URL}/users/logout")
    if request.status_code == 200:
        await message.answer("Вы успешно вышли из профиля")

        kb = [
            [
                types.KeyboardButton(text='Регистрация'),
                types.KeyboardButton(text='Войти в аккаунт'),
            ],
        ]
        keyboard = types.ReplyKeyboardMarkup(
            keyboard=kb,
            resize_keyboard=True,
            input_field_placeholder="Выберите действие"
        )

        await message.answer('Выберите действие', reply_markup=keyboard)
    else:
        await message.answer('Ошибка')


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())