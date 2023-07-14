"""
MIT License

Copyright (c) Albert Avkhadeev

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE."

"""

import markups as nav
import aio_pika
import json
import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from respositories import (
    AccountRepository,
    CategoryRepository,
    AccountWithCategoryRepository,
)
from model import Account, Account_by_category, Category
from config import TOKEN

# Check if logs folder exists and if not create
if not os.path.exists("logs"):
    os.makedirs("logs")

# Instance of the bot
bot = Bot(token=TOKEN)

# Storage for using FSM
storage = MemoryStorage()

# Logging information
logging.basicConfig(level=logging.ERROR, filename="logs/logs.log", filemode="w")
dp = Dispatcher(bot, storage=storage)
# Repositories for using database
account_repo = AccountRepository()
category_repo = CategoryRepository()
account_and_category_repo = AccountWithCategoryRepository()

"""
Class representing working states of the bot
"""


class WorkingStates(StatesGroup):
    entered = State()  # When user entered into bot by registration or logining in
    settings = State()
    run = State()
    stop = State()


@dp.message_handler(commands="start")
async def starting_process(message: types.Message, state: FSMContext):
    # Checkcing current state of the user. We will not accept users for this command if they already have an account
    current_state = await state.get_state()
    # Checking for only private messages
    if message.chat.type == "private" and current_state is None:
        # Temporary solution, because we are in the process of development ability to add more users. Now only one user can use bot
        admin = account_repo.getAccountById(message.from_user.id)
        if admin != None and admin.account_telegram_id == message.from_user.id:
            # If current accout were not registred before, we will add it to database
            admin = Account(message.from_user.id)
            account_repo.addAccount(admin)
            await bot.send_message(
                chat_id=message.from_id,
                text="Привет! 🤖👋😊\n\nЯ рад видеть вас здесь! Я бот в Telegram, который отслеживает лиды для вас. Моя задача - помочь вам получать больше клиентов и увеличивать продажи. Если у вас есть какие-либо вопросы или пожелания, не стесняйтесь обращаться ко мне. Я всегда готов помочь! 😊👍",
                reply_markup=nav.account_menu,
            )
            # Changing state to entered for the current user
            await state.set_state(WorkingStates.entered)


@dp.callback_query_handler(text="category_menu", state=WorkingStates.entered)
async def category_menu_output(query_call: types.CallbackQuery):
    await bot.delete_message(
        chat_id=query_call.from_user.id, message_id=query_call.message.message_id
    )
    await bot.send_message(
        chat_id=query_call.from_user.id,
        text="🤖 Выберите категорию работы, информацию о которой хотели бы получать",
        reply_markup=nav.categories_menu,
    )


@dp.callback_query_handler(text="fulfilment", state=WorkingStates.entered)
async def category_menu_output(query_call: types.CallbackQuery, state: FSMContext):
    category = category_repo.getCategoryByName("Fulfilment")
    if category == None:
        category = Category("Fulfilment")
        category_repo.addCategory(category)
    account_telegram = query_call.from_user.id
    account_with_category = Account_by_category(category.id, account_telegram)
    if account_and_category_repo.getAccountForCategory(account_with_category) != None:
        await bot.delete_message(
            chat_id=query_call.from_user.id, message_id=query_call.message.message_id
        )
        await bot.send_message(
            chat_id=query_call.from_user.id,
            text="🚫 Вы уже подписаны на это\n\nЕсли вы хотите запустить или приостановить бота, используйте команду /bot_settings",
            reply_markup=nav.close_menu,
        )
        await state.set_state(WorkingStates.battle)
        return
    account_and_category_repo.addAccountForCategory(account_with_category)
    await bot.delete_message(
        chat_id=query_call.from_user.id, message_id=query_call.message.message_id
    )
    await bot.send_message(
        chat_id=query_call.from_user.id,
        text="✅ Успешно\n\nЕсли вы хотите запустить или приостановить бота, используйте команду /bot_settings",
        reply_markup=nav.close_menu,
    )
    await state.set_state(WorkingStates.battle)


@dp.callback_query_handler(text="close", state="*")
async def close_window(query_call: types.CallbackQuery):
    await bot.delete_message(
        chat_id=query_call.from_user.id, message_id=query_call.message.message_id
    )


@dp.message_handler(
    commands="bot_settings",
    state=[WorkingStates.settings, WorkingStates.run, WorkingStates.stop],
)
async def bot_status(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == "WorkingStates:run":
        await bot.send_message(
            chat_id=message.from_user.id,
            text="🤖 Статус бота - работает!",
            reply_markup=nav.control_menu,
        )
    elif (
        current_state == "WorkingStates:stop"
        or current_state == "WorkingStates:settings"
    ):
        await bot.send_message(
            chat_id=message.from_user.id,
            text="🤖 Статус бота - не работает!",
            reply_markup=nav.control_menu,
        )


@dp.callback_query_handler(
    text="stop_button",
    state=[WorkingStates.settings, WorkingStates.run, WorkingStates.stop],
)
async def close_window(query_call: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(
        chat_id=query_call.from_user.id, message_id=query_call.message.message_id
    )
    current_state = await state.get_state()
    if current_state != "WorkingStates:run":
        await bot.send_message(
            chat_id=query_call.from_user.id,
            text="🚫 Бот уже на пазуе. Нельзя его остановить ещё раз!",
            reply_markup=nav.control_menu,
        )
    else:
        account_and_category_repo.turnOffAllCategoriesForAccount(
            query_call.from_user.id
        )
        await state.set_state(WorkingStates.stop)
        await bot.send_message(
            chat_id=query_call.from_user.id,
            text="✅ Бот успешно приостановлен",
            reply_markup=nav.control_menu,
        )


@dp.callback_query_handler(
    text="start_button",
    state=[WorkingStates.settings, WorkingStates.run, WorkingStates.stop],
)
async def close_window(query_call: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(
        chat_id=query_call.from_user.id, message_id=query_call.message.message_id
    )
    current_state = await state.get_state()
    if current_state == "WorkingStates:run":
        await bot.send_message(
            chat_id=query_call.from_user.id,
            text="🚫 Бот уже запущен. Нельзя его запустить ещё раз!",
            reply_markup=nav.control_menu,
        )
    else:
        account_and_category_repo.turnOnAllCategoriesForAccount(query_call.from_user.id)
        await state.set_state(WorkingStates.run)
        await bot.send_message(
            chat_id=query_call.from_user.id,
            text="✅ Бот успешно запущен",
            reply_markup=nav.control_menu,
        )


"""
If new message will appears from producer, this function will be called
"""


async def on_message(message):
    async with message.process():
        data = json.loads(message.body.decode())
        # Send the message to Telegram using aiogram
        participants = account_and_category_repo.getAccountsForCategoryByName(
            "Fulfilment"
        )
        for person in participants:
            if person.is_enabled_for_search == True:
                keyboard_for_lead = InlineKeyboardMarkup(row_width=1).insert(
                    InlineKeyboardButton(
                        text="👨‍🏭 Связаться с заказчиком",
                        url="https://t.me/" + data["username"],
                    )
                )
                await bot.send_message(
                    person.account_telegram_id,
                    data["message"],
                    reply_markup=keyboard_for_lead,
                )


"""
Function for registering RabbitMQ consumer
"""


async def register():
    connection = await aio_pika.connect_robust("amqp://guest:guest@localhost/")
    rabbit_mq_channel = await connection.channel()
    queue = await rabbit_mq_channel.declare_queue("messages")
    await queue.consume(on_message)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(register())
    executor.start_polling(dp, skip_updates=True)
