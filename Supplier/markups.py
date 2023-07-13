from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

start_menu = InlineKeyboardMarkup(row_width=2)
next_button = InlineKeyboardMarkup(InlineKeyboardButton("Далее"))

register_button = InlineKeyboardButton(text='Зарегистрироваться', callback_data='register')
login_button = InlineKeyboardButton(text='Войти', callback_data='login')
back_button = InlineKeyboardButton(text='Назад', callback_data='back')
start_menu.insert(register_button).insert(login_button)

account_menu = InlineKeyboardMarkup(row_width=2)
button_subscription = InlineKeyboardButton(text='Подписки', callback_data='subscription_menu')
button_category = InlineKeyboardButton(text='Категории', callback_data='category_menu')
button_exit = InlineKeyboardButton(text='Выйти', callback_data='exit_menu')
button_close = InlineKeyboardButton(text="Закрыть", callback_data="close")
account_menu.insert(button_category)

categories_menu = InlineKeyboardMarkup(row_width=1)
category_button_1 = InlineKeyboardButton(text='Первый тип', callback_data='first_type')
category_button_2 = InlineKeyboardButton(text='Второй тип', callback_data='second_type')
category_button_3 = InlineKeyboardButton(text='Фулфилмент', callback_data='fulfilment')
category_button_4 = InlineKeyboardButton(text='Логистика', callback_data='logistics')
categories_menu.insert(category_button_3).insert(button_close)

control_menu = InlineKeyboardMarkup(row_width=2)
start_button = InlineKeyboardButton(text='Запустить', callback_data='start_button')
stop_button = InlineKeyboardButton(text='Приостановить', callback_data='stop_button')
control_menu.insert(start_button).insert(stop_button).insert(button_close)
