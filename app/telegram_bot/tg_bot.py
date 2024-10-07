import logging
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.filters import Command
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
import requests
from worker.tasks import handle_request as celery_handle_request
from worker.tasks import handle_interpret as celery_interpret
from worker.celery_config import app
from celery.result import AsyncResult
from config import TOKEN, API_URL


bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)
user_tokens = {}


class Registration(StatesGroup):
    email = State()
    password = State()


class Login(StatesGroup):
    email = State()
    password = State()


class Balance(StatesGroup):
    amount = State()


class Form(StatesGroup):
    waiting_for_file = State()
    pdf_path = State()


@dp.message_handler(Command('start'))
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
    await message.answer(f"Привет, {message.from_user.first_name}! Я помогу тебе узнать, какую зарплату ты можешь "
                         f"получить по твоему резюме с сфере Data Science \n Ты можешь сделать 2 бесплатных запроса в "
                         f"день. Если захочешь больше — каждый дополнительный запрос стоит всего 100 рублей. "
                         f"Воспользуйся шансом улучшить своё будущее уже сегодня!"
                         , reply_markup=keyboard)


@dp.message_handler(Command('help'))
async def help(message: types.Message):
    await message.answer('Доступные команды:\n'
                         '\start: Начать взаимодействие\n'
                         '\help: Показать справочную информацию')


@dp.message_handler(lambda message: message.text.lower() == 'войти в аккаунт', state="*")
async def login(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Введите email для входа:")
    await state.set_state(Login.email)


@dp.message_handler(lambda message: message.text.lower() == 'регистрация', state="*")
async def register(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Введите email для входа:")
    await state.set_state(Registration.email)


@dp.message_handler(lambda message: message.text.lower() == 'сделать запрос', state="*")
async def register(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Пожалуйста, загрузите файл в формате PDF.")
    await state.set_state(Form.waiting_for_file)


@dp.message_handler(lambda message: message.text.lower() == 'сделать запрос', state="*")
async def register(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("Пожалуйста, загрузите файл в формате PDF.")
    await state.set_state(Form.waiting_for_file)


@dp.message_handler(lambda message: message.text.lower() == "регистрация", state='None')
async def capture_name(message: types.Message, state: FSMContext):
    await message.answer('Введите email')
    await state.set_state(Registration.email)


@dp.message_handler(state=Registration.email)
async def capture_password(message: types.Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.reply('Введите пароль')
    await state.set_state(Registration.password)


@dp.message_handler(state=Registration.password)
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
        await message.answer(f"Ошибка регистрации: неверный ответ сервера. Status code: {request.status_code}")

    await state.finish()


@dp.message_handler(lambda message: message.text.lower() == "войти в аккаунт", state=None)
async def capture_name(message: types.Message, state: FSMContext):
    await message.answer('Введите email')
    await state.set_state(Login.email)


@dp.message_handler(state=Login.email)
async def capture_password(message: types.Message, state: FSMContext):
    await state.update_data(email=message.text)
    await message.reply('Введите пароль')
    await state.set_state(Login.password)


@dp.message_handler(state=Login.password)
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
    await state.finish()


@dp.message_handler(lambda message: message.text.lower() == 'пополнить баланс', state=None)
async def add_money(message: types.Message, state: FSMContext):
    await message.answer('Введите сумму')
    await state.set_state(Balance.amount)


@dp.message_handler(state=Balance.amount)
async def process_add_money(message: types.Message, state: FSMContext):
    try:
        amount = float(message.text)
    except ValueError:
        await message.answer("Пожалуйста, введите корректную сумму.")
        return

    token = user_tokens.get(message.chat.id)
    if not token:
        await message.answer("Вы не авторизованы. Пожалуйста, войдите в аккаунт.")
        await state.finish()
        return

    headers = {"Authorization": f"Bearer {token}"}
    request = requests.post(
        f"{API_URL}/balances/add_balance",
        headers=headers,
        data={"amount": amount}
    )
    if request.status_code == 200:
        await message.answer("Ваш баланс успешно пополнен!")
    elif request.status_code == 500:
        await message.answer("Вы не авторизованы. Пожалуйста, войдите в аккаунт.")
    else:
        await message.answer(f"Ошибка пополнения: {request.json().get('detail', 'Ошибка пополнения')}")

    await state.finish()


@dp.message_handler(lambda message: message.text.lower() == 'посмотреть баланс')
async def get_balance(message: types.Message):
    request = requests.get(f"{API_URL}/balances/balance")
    if request.status_code == 200:
        balance = request.json().get('amount')
        await message.answer(f'Ваш баланс: {balance}')
    elif request.status_code == 500:
        await message.answer("Вы не авторизованы. Пожалуйста, войдите в аккаунт.")
    else:
        await message.answer(f"Ошибка: {request.json().get('detail', 'Ошибка')}")


@dp.message_handler(lambda message: message.text.strip().lower() == 'сделать запрос')
async def start_file_upload(message: types.Message, state: FSMContext):
    await message.answer("Пожалуйста, загрузите файл в формате PDF.")
    await state.set_state(Form.waiting_for_file)


@dp.message_handler(state=Form.waiting_for_file, content_types=['document'])
async def handle_request(message: types.Message, state: FSMContext):
    if message.document.mime_type != 'application/pdf':
        await message.reply("Некорректный формат. Пожалуйста, загрузите PDF файл")
        return

    file_info = await bot.get_file(message.document.file_id)
    downloaded_file = await bot.download_file(file_info.file_path)
    pdf_path = f'/app/shared_data/{message.document.file_name}'

    await state.update_data(pdf_path=pdf_path)

    await state.set_state(Form.pdf_path)

    file_content = downloaded_file.read()

    with open(pdf_path, 'wb') as new_file:
        new_file.write(file_content)

    await message.reply("Файл принят в обработку")

    response = requests.get(f"{API_URL}/users/current_user")
    if response.status_code == 200:
        user_data = response.json()
        current_user = user_data.get("email")
    else:
        kb = [
            [
                types.KeyboardButton(text="Регистрация"),
                types.KeyboardButton(text="Войти в аккаунт")
            ],
        ]
        keyboard_1 = types.ReplyKeyboardMarkup(
            keyboard=kb,
            resize_keyboard=True,
            input_field_placeholder="Выберите действие"
        )
        await message.answer("Вы не авторизованы. Пожалуйста, войдите в аккаунт.", reply_markup=keyboard_1)
        return None

    await message.answer('Итак, барабанная дробь...')

    task_id = celery_handle_request.apply_async(args=[pdf_path, current_user])
    result = AsyncResult(task_id, app=app)
    kb = [
        [
            types.KeyboardButton(text="Хотите улучшить зарплату? Нажмите здесь"),
            types.KeyboardButton(text="В меню")
        ],
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )

    await message.answer(f'Предполагаю, что твоя будущая зарплата будет такой: '
                         f'{round(result.get()["salary"], 3)} 💼💸', reply_markup=keyboard)


@dp.message_handler(lambda message: message.text.strip().lower() == 'хотите улучшить зарплату? нажмите здесь',
                    state=Form.pdf_path)
async def handle_interpret(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    pdf_path = user_data.get('pdf_path')

    if pdf_path is None:
        await message.answer("Ошибка: путь к PDF-файлу не найден.")
        return

    await message.answer("Анализ прогноза... Пожалуйста, подождите")

    response = requests.get(f"{API_URL}/users/current_user")
    if response.status_code == 200:
        user_data = response.json()
        current_user = user_data.get("email")
    else:
        await message.answer("Не удалось получить данные пользователя.")
        return

    task = celery_interpret.apply_async(args=[pdf_path, current_user])
    result = AsyncResult(task, app=app)
    skills_improve, skills_advice = result.get()

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

    await message.answer(f'Вы можете улучшать эти навыки, они повышают ваши зарплату:\n{skills_improve}')
    await message.answer(f'Можете рассмотреть эти навыки, они повысят зарплату:\n {skills_advice}',
                         reply_markup=keyboard)


@dp.message_handler(lambda message: message.text.strip().lower() == 'в меню')
async def menu(message: types.Message):
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
    await message.answer('Выберите действие!', reply_markup=keyboard)


@dp.message_handler(lambda message: message.text.lower() == 'история запросов')
async def transaction_history(message: types.Message):
    response = requests.get(url=f"{API_URL}/users/transaction_history")

    if response.status_code == 200:
        await message.answer('История последних 5 запросов:')

        transactions = response.json()

        if transactions and isinstance(transactions, list):
            for transaction in transactions[-5:]:
                current_time = transaction.get('current_time')
                salary = transaction.get('salary')
                spent_money = transaction.get('spent_money')

                if current_time and salary and spent_money is not None:
                    await message.answer(
                        f"Дата: {current_time}\nПрогноз: {salary}\nПотрачено: {spent_money}"
                    )
                else:
                    await message.answer("Ошибка: недостаточно данных для отображения транзакции.")
        else:
            await message.answer("История запросов пуста.")

    elif response.status_code == 500:
        await message.answer("Вы не авторизованы. Пожалуйста, войдите в аккаунт.")
    else:
        await message.answer(
            f"Ошибка получения истории: {response.json().get('detail', 'Ошибка получения истории')}"
        )


@dp.message_handler(lambda message: message.text.lower() == 'выйти из профиля')
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