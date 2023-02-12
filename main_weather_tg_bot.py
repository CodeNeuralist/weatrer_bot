import requests
import datetime
from config import tg_bot_token, open_weather_token
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from geopy.geocoders import Nominatim
from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton

bot = Bot(token=tg_bot_token)
dp = Dispatcher(bot)

button_hi = KeyboardButton(text="Запросить геолокацию", request_location=True)

greet_kb = ReplyKeyboardMarkup()
greet_kb.add(button_hi)


@dp.message_handler(commands=["start"])
async def start_command(message: types.Message):
    await message.reply("Привет! Напиши мне название города и я пришлю сводку погоды!", reply_markup=greet_kb)


def get_address_by_location(latlong, language='ru'):
    app = Nominatim(user_agent='tutorial')
    try:
        return app.reverse(latlong, language=language).raw
    except:
        return get_address_by_location(latlong)


def get_weatherr(address):
    code_to_smile = {
        "Clear": "Ясно \U00002600",
        "Clouds": "Облачно \U00002601",
        "Rain": "Дождь \U00002614",
        "Drizzle": "Дождь \U00002614",
        "Thunderstorm": "Гроза \U000026A1",
        "Snow": "Снег \U0001F328",
        "Mist": "Туман \U0001F32B"
    }

    try:
        r = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={address}&appid={open_weather_token}&units=metric"
        )
        data = r.json()

        city = data["name"]
        cur_weather = data["main"]["temp"]

        weather_description = data["weather"][0]["main"]
        if weather_description in code_to_smile:
            wd = code_to_smile[weather_description]
        else:
            wd = "Посмотри в окно, не пойму что там за погода!"

        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind = data["wind"]["speed"]
        sunrise_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunrise"])
        sunset_timestamp = datetime.datetime.fromtimestamp(data["sys"]["sunset"])
        length_of_the_day = datetime.datetime.fromtimestamp(data["sys"]["sunset"]) - datetime.datetime.fromtimestamp(
            data["sys"]["sunrise"])

        return f"Погода в городе: {city}\nТемпература: {cur_weather}C° {wd}\n" + f"Влажность: {humidity}%\nДавление: {pressure} мм.рт.ст\nВетер: {wind} м/с\n" + f"Восход солнца: {sunrise_timestamp}\nЗакат солнца: {sunset_timestamp}\nПродолжительность дня: {length_of_the_day}\n" + f"***Хорошего дня!***"

    except:
        return "Проверьте название города!!!"


@dp.message_handler(content_types=['location'])
async def handle_location(message: types.Message):
    lat = message.location.latitude
    lon = message.location.longitude

    address = get_address_by_location(f"{lat}, {lon}")

    await message.reply("Выбран город: " + address['address']['city'])
    print(address['address']['city'])

    city = address['address']['city']

    zaproc = get_weatherr(city)

    await message.reply(zaproc, reply_markup=greet_kb)


@dp.message_handler()
async def get_weather(message: types.Message):
    await message.reply(get_weatherr(message.text), reply_markup=greet_kb)


if __name__ == '__main__':
    executor.start_polling(dp)
