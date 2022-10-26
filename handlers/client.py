import logging
from datetime import datetime
from math import floor

import requests
from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove
from aiogram_calendar import (DialogCalendar, SimpleCalendar,
                              dialog_cal_callback, simple_cal_callback)
# from aiogram_datepicker import Datepicker, DatepickerSettings
from decouple import config
from helpers.funcs import deep_get
from keyboards import calendar_kb, client_kb

# from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP


class FSMClient(StatesGroup):
    currency = State()
    amount = State()
    date = State()
    
    
logger = logging.getLogger(__name__)    


async def command_start(msg: types.Message):
    await msg.answer('This bot will allow you to get the exchange rate in lari on the specified date',
                     reply_markup=client_kb)
    
    
async def start_work(msg: types.Message):
    await FSMClient.currency.set()
    await msg.answer('Enter currency code')
    
    
async def get_currency(msg: types.Message, state=FSMContext):
    async with state.proxy() as data:
        data['currency'] = msg.text.upper()
        
    await FSMClient.next()
    await msg.answer('Enter amount')   
    
    
async def process_amount_invalid(msg: types.Message):
    """
    If amount is invalid
    """
    return await msg.reply("Amount gotta be a number.\nEnter amount (digits only)")    
    
    
async def get_amount(msg: types.Message, state=FSMContext):
    async with state.proxy() as data:
        data['amount'] = int(msg.text)
    
    await FSMClient.next()
    
    async with state.proxy() as data:
        data['msg'] = await msg.answer("Please select a date: ", 
                                       reply_markup=await SimpleCalendar().start_calendar())  
  

async def edit_msg(msg: types.Message, s: str):
    await msg.edit_text(f'{s}')
  
    
async def process_simple_calendar(callback_query: types.CallbackQuery, callback_data: dict, state=FSMContext):
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    
    if selected:
        today = date.today().strftime('%Y-%m-%d')
        selected_date = date.strftime("%Y-%m-%d")
        selected_date = selected_date if selected_date <= today else today
        
        async with state.proxy() as data:
            await edit_msg(data['msg'], f'You selected {selected_date}, wait...',)
            data['date'] = selected_date
            response = requests.get(f'{config("URL")}/?currencies={data["currency"]}&date={data["date"]}').json()
        
        result = 'It looks like you\'ve entered wrong currency code'
        
        if len(response[0].get('currencies', [])) > 0:
            rate = deep_get(response[0], 'currencies.0.rate')
            total_sum = round(data['amount'] * rate, 2)
            result = f'{data["currency"]} rate was {rate} on {data["date"]} .\nYour amount: {total_sum} GEL'
        
        await callback_query.message.answer(
            result,
            reply_markup=client_kb
        )
            
        await state.finish()

    
async def cancel_handler(msg: types.Message, state: FSMContext):
    current_state = await state.get_state()
    
    if current_state is None:
        return
    
    logging.info('Cancelling state %r', current_state)
     
    await state.finish()
    await msg.reply('Ok', reply_markup=types.ReplyKeyboardRemove())


def register_client_handlers(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=['start']) 
    dp.register_message_handler(cancel_handler, commands=['cancel'])
    dp.register_message_handler(start_work, commands=['get_exchange_rates'], state=None)  
    dp.register_message_handler(get_currency, content_types='text', state=FSMClient.currency)  
    dp.register_message_handler(get_amount, 
                                lambda msg: msg.text.isdigit(), 
                                content_types='text',
                                state=FSMClient.amount)  
    dp.register_message_handler(process_amount_invalid, 
                                lambda msg: not msg.text.isdigit(), 
                                state=FSMClient.amount)  
    
    dp.register_callback_query_handler(process_simple_calendar, 
                                simple_cal_callback.filter(), 
                                state=FSMClient.date)
    