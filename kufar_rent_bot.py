import asyncio
import json

import time
from datetime import datetime
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from telebot import types
from aiogram import Bot, types, executor
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State

from main1 import refresh_list
from keyboards import room_kbrd, period_kbrd, reset_kbrd

storage = MemoryStorage()
token = '6121619731:AAH6AsrTl-R346pGKctHyCwsARto2Gaz3Ow'
bot = Bot(token=token)
dp = Dispatcher(bot, storage=storage)

stop_iteration = False


async def on_startup(_):
    print('Бот запущен!')


class RentGroup(StatesGroup):
    room_count = State()
    period = State()


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Привет! Для поиска квартир выберите количество комнат.", reply_markup=room_kbrd)


@dp.message_handler(Text("Обновить объявления"))
async def reset(message: types.Message):
    await message.answer("Для поиска квартир выберите количество комнат.",
                         reply_markup=room_kbrd)


@dp.message_handler(
    lambda message: message.text in ["1 комната", "2 комнаты", "3 комнаты", "4 комнаты", "5 и более", "Все"])
async def choose_quant(message: types.Message, state: FSMContext):
    if message.text == "Все":
        room_count = None
    else:
        room_count = message.text.split()[0]
    await RentGroup.room_count.set()
    await state.update_data(room_count=room_count)
    await message.answer('Как часто вы хотите получать обновление объявлений?',
                         reply_markup=period_kbrd)
    await RentGroup.next()


@dp.message_handler(Text(startswith="1/"), state=RentGroup.period)
async def flat_list(message: types.Message, state: FSMContext):
    periods = {"1/30 мин": 30, "1/1 час": 60, "1/2 часа": 120}
    if message.text in periods:
        period = periods[message.text]
        await state.update_data(period=period)
        data = await state.get_data()
        r_count = data['room_count']
        await state.finish()
        while True:
            now = datetime.now()
            if now.hour > 9:
                refresh_list(r_count=r_count)
                await send_data(message)
            else:
                pass
            time.sleep(period * 60)


@dp.message_handler(Text('Остановить'))
async def stop_signal(message):
    global stop_iteration
    stop_iteration = True


async def send_data(message):
    with open('flats.json', encoding='utf-8') as file:
        fl_list = json.load(file)
    for i in fl_list:
        time.sleep(4)
        photos = i['photos']
        media = [types.InputMediaPhoto(photo) for photo in photos]
        try:
            await  bot.send_media_group(chat_id=message.chat.id, media=media)
        except Exception as ex:
            print(ex)
            await bot.send_message(message.chat.id,
                                   "Возникли проблемы, фото можно посмотреть по ссылке..")
        if 'description' in i.keys():
            await bot.send_message(message.chat.id, f"<a href='{i['link']}'>"
                                                    f"🏠<b>{i['apartment']}</b>\n"
                                                    f"💵<i>{i['price']}</i>\n"
                                                    f"📍{i['address']}\n"
                                                    f"\n"
                                                    f"💬<i>{i['description']}</i>"
                                                    f"</a>", parse_mode='html',
                                   reply_markup=reset_kbrd)
        else:
            await bot.send_message(message.chat.id, f"<a href='{i['link']}'>"
                                                    f"🏠<b>{i['apartment']}</b>\n"
                                                    f"💵<i>{i['price']}</i>\n"
                                                    f"📍{i['address']}\n"
                                                    f"</a>", parse_mode='html',
                                   reply_markup=reset_kbrd)



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
