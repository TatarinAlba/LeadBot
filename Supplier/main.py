from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from respositories import AccountRepository, CategoryRepository, AccountWithCategoryRepository
from model import Account, Account_by_category, Category
from config import TOKEN
import markups as nav
import re
import logging

bot = Bot(token=TOKEN) # getting information about the token from the text file
storage = MemoryStorage()
logging.basicConfig(level=logging.INFO, filename="logs.log",filemode="w")
dp = Dispatcher(bot, storage=storage)
account_repo = AccountRepository()
category_repo = CategoryRepository()
account_and_category_repo = AccountWithCategoryRepository()

base_is_empty = len(account_repo.getAllAcounts()) == 0

class WorkingStates(StatesGroup):
    work = State()
    wait = State()

globalState: FSMContext = WorkingStates.wait

@dp.message_handler(commands="start", state="*")
async def starting_process(message: types.Message):
    global base_is_empty 
    if message.chat.type == "private":
        admin = account_repo.getAccountById(message.from_user.id)
        if (base_is_empty):
            admin = Account(message.from_user.id) 
            base_is_empty = False
            account_repo.addAccount(admin)
            await bot.send_message(chat_id=message.from_id, text="Привет! 🤖👋😊\n\nЯ рад видеть вас здесь! Я бот в Telegram, который отслеживает лиды для вас. Моя задача - помочь вам получать больше клиентов и увеличивать продажи. Если у вас есть какие-либо вопросы или пожелания, не стесняйтесь обращаться ко мне. Я всегда готов помочь! 😊👍", reply_markup=nav.account_menu)


# @dp.callback_query_handler(text="register")
# async def registration_process(query_call: types.CallbackQuery):
#     account = account_repo.getAccountById(query_call.from_user.id)
#     if account is not None:
#         await bot.delete_message(chat_id=query_call.from_user.id, message_id = query_call.message.message_id)
#         await bot.send_message(chat_id=query_call.from_user.id, text="🚫 Извините, но ваш аккаунт уже существует, попробуйте войти в существующий профиль.")
#     else:
#         await bot.delete_message(chat_id=query_call.from_user.id, message_id = query_call.message.message_id)
#         account = Account(query_call.from_user.id)
#         account_repo.addAccount(account)
#         await bot.send_message(chat_id=query_call.from_user.id, text="✅ Аккаунт успешно создан!\n\nДля начала работы введите команду /start и нажмите кнопку \"Войти\".")


# @dp.callback_query_handler(text="login")
# async def wait_for_name(query_call: types.CallbackQuery, state: FSMContext):
#         await bot.delete_message(chat_id=query_call.from_user.id, message_id = query_call.message.message_id)
#         account = account_repo.getAccountById(query_call.from_user.id)
#         if account is None:
#             await bot.send_message(chat_id=query_call.from_user.id, text="🚫 Извините, но ваш аккаунт не найден, попробуйте зарегистрироваться.")
#         else:
#             await bot.send_message(chat_id=query_call.from_user.id, text="✅ Добро пожаловать в личный кабинет.\n\nВесь следующий функционал, доступный вам, вы можете посмотреть ниже.", reply_markup=nav.account_menu)


@dp.callback_query_handler(text="category_menu", state="*")
async def category_menu_output(query_call: types.CallbackQuery):
    await bot.delete_message(chat_id=query_call.from_user.id, message_id = query_call.message.message_id)
    await bot.send_message(chat_id=query_call.from_user.id, text="🤖 Выберите категорию работы, информацию о которой хотели бы получать", reply_markup=nav.categories_menu)

@dp.callback_query_handler(text="fulfilment", state="*")
async def category_menu_output(query_call: types.CallbackQuery, state: FSMContext):
    global globalState
    category = category_repo.getCategoryByName("Fulfilment")
    if (category == None):
        category = Category("Fulfilment")
        category_repo.addCategory(category)
    account_telegram = query_call.from_user.id
    account_with_category = Account_by_category(category.id, account_telegram)
    if account_and_category_repo.getAccountForCategory(account_with_category) != None:
        await bot.delete_message(chat_id=query_call.from_user.id, message_id = query_call.message.message_id)
        await bot.send_message(chat_id=query_call.from_user.id, text="🚫 Вы уже подписаны на это\n\n🤖 Выберите дополнительную категорию работы, информацию о которой хотели бы получать\n\nЕсли вы хотите запустить или приостановить бота, используйте команду /status", reply_markup=nav.categories_menu)
        return 
    account_and_category_repo.addAccountForCategory(account_with_category)
    await bot.delete_message(chat_id=query_call.from_user.id, message_id = query_call.message.message_id)
    await bot.send_message(chat_id=query_call.from_user.id, text="✅ Успешно\n\n🤖 Выберите дополнительную категорию работы, информацию о которой хотели бы получать.\n\nЕсли вы хотите запустить или приостановить бота, используйте команду /status", reply_markup=nav.categories_menu)
    await state.set_state(WorkingStates.work)
    globalState = WorkingStates.work

@dp.callback_query_handler(text="close", state="*")
async def close_window(query_call:types.CallbackQuery):
    await bot.delete_message(chat_id=query_call.from_user.id, message_id = query_call.message.message_id)

@dp.message_handler(commands="status", state="*")
async def bot_status(message: types.Message, state: FSMContext):
    global globalState
    if not base_is_empty and message.chat.type == "private":
        current_state = await state.get_state()
        if current_state == "WorkingStates:work":
            await bot.send_message(chat_id=message.from_user.id, text="🤖 Статус бота - работает!", reply_markup=nav.control_menu)
        elif current_state != None:
            globalState = WorkingStates.wait
            await state.set_state(WorkingStates.wait)
            await bot.send_message(chat_id=message.from_user.id, text="🤖 Статус бота - не работает!", reply_markup=nav.control_menu)
        else:
            await bot.send_message(chat_id=message.from_user.id, text="🤖 Статус бота - не работает!", reply_markup=nav.control_menu)

@dp.callback_query_handler(text="stop_button", state="*")
async def close_window(query_call:types.CallbackQuery, state: FSMContext):
    global globalState
    await bot.delete_message(chat_id=query_call.from_user.id, message_id = query_call.message.message_id)
    current_state = await state.get_state()
    if current_state != "WorkingStates:work":
        await bot.send_message(chat_id=query_call.from_user.id, text="🚫 Бот уже на пазуе. Нельзя его остановить ещё раз!", reply_markup=nav.control_menu)
    else:
        globalState = WorkingStates.wait
        await state.set_state(WorkingStates.wait)
        await bot.send_message(chat_id=query_call.from_user.id, text="✅ Бот успешно приостановлен", reply_markup=nav.control_menu)

@dp.callback_query_handler(text="start_button", state="*")
async def close_window(query_call:types.CallbackQuery, state: FSMContext):
    global globalState
    await bot.delete_message(chat_id=query_call.from_user.id, message_id = query_call.message.message_id)
    current_state = await state.get_state()
    if current_state == "WorkingStates:work":
        await bot.send_message(chat_id=query_call.from_user.id, text="🚫 Бот уже запущен. Нельзя его запустить ещё раз!", reply_markup=nav.control_menu)
    else:
        globalState = WorkingStates.work
        await state.set_state(WorkingStates.work)
        await bot.send_message(chat_id=query_call.from_user.id, text="✅ Бот успешно запущен", reply_markup=nav.control_menu)


@dp.message_handler()
async def check_message(message: types.Message):
    global globalState
    if message.chat.type != "private" and not base_is_empty and globalState is WorkingStates.work:
        participants = account_and_category_repo.getAccountsForCategoryByName("Fulfilment")
        with open('keywords.txt', 'r') as f:
            regex_list = f.readlines()
        for regex in regex_list:
            if re.search(regex.strip().lower(), message.text.lower()):
                for person in participants:
                    keyboard_for_lead = InlineKeyboardMarkup(row_width=1).insert(InlineKeyboardButton(text='👨‍🏭 Связаться с заказчиком', url="https://t.me/" + message.from_user.username)).insert(InlineKeyboardButton(text='⚠️ Пожаловаться на заказчика', callback_data='warn_author'))
                    await bot.send_message(person.account_telegram_id, message.text, reply_markup=keyboard_for_lead)
                return


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
