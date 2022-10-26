from aiogram.types import ReplyKeyboardMarkup, KeyboardButton #, ReplyKeyboardRemove


btn1 = KeyboardButton('/get_exchange_rates')
btn2 = KeyboardButton('/cancel')

client_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
client_kb.row(btn1, btn2)
