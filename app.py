import telebot
from telebot import types

from config import *
from extensions import GottenCurrency, APIException

bot = telebot.TeleBot(TOKEN)


conv_markup = types.ReplyKeyboardMarkup(row_width=5, resize_keyboard=True)
button = []
for key in available_currency:
    markup = types.KeyboardButton(key)
    button.append(markup)
conv_markup.add(*button)


@bot.message_handler(commands=['start', 'help'])
def handle_start_help(message: telebot.types.Message):
    text = 'При вводе команды "/value" выводится информация о всех доступных валютах.\n\
При вводе команды "/convert" бот начинает собирать данные для конвертации'
    bot.reply_to(message, text)


@bot.message_handler(commands=['value'])
def handle_value(message: telebot.types.Message):
    text = 'Доступныe для конвертации валюты:'
    for i in available_currency:
        text = text + f'\n- {str(i)}'
    bot.reply_to(message, text)


@bot.message_handler(commands=['convert'])
def handle_convert(message):
    text = 'Ввеедите имя валюты, цену которой вы хотите узнать:'
    bot.send_message(message.chat.id, text, reply_markup=conv_markup)
    bot.register_next_step_handler(message, handle_base)


@bot.message_handler(content_types=['text'])
def handle_base(message):
    base = message.text
    if message.text == "/start" or message.text == "/help":
        handle_start_help(message)
    elif message.text == "/value":
        handle_value(message)
    elif message.text == "/convert":
        handle_convert(message)
    elif not available_currency.get(base):
        bot.send_message(message.chat.id, f'Неправильно введены данные:\n\
Неправильное название валюты "{base}" или ее нет в списке!')
        handle_convert(message)
    else:
        text = 'Введите имя валюты, в которой надо узнать цену первой валюты:'
        bot.send_message(message.chat.id, text, reply_markup=conv_markup)
        bot.register_next_step_handler(message, handle_quote, base)


def handle_quote(message, base):
    quote = message.text
    if not available_currency.get(quote):
        bot.send_message(message.chat.id, f'Неправильно введены данные:\n\
Неправильное название валюты "{quote}" или ее нет в списке!/\n\
Введите имя валюты, в которой надо узнать цену первой валюты:')
        bot.register_next_step_handler(message, handle_quote, base)
    elif base == quote:
        bot.send_message(message.chat.id, f'Неправильно введены данные:\n\
Валюты не должны быть одинаковыми!\n\
Введите имя валюты, в которой надо узнать цену первой валюты:')
        bot.register_next_step_handler(message, handle_quote, base)
    else:
        text = 'Введите количество первой валюты:'
        bot.send_message(message.chat.id, text)
        bot.register_next_step_handler(message, convert_currency, base, quote)


def convert_currency(message, base, quote):
    amount = message.text.replace(',', '.')
    try:
        if amount.isdigit():
            amount = int(amount)
        else:
            amount = float(amount)
        if amount <= 0:
            raise APIException()
    except Exception:
        bot.send_message(message.chat.id, f'Неправильно введены данные:\n\
Количество конвентируемой валюты.\n\
Введите корректное количество!')
        bot.register_next_step_handler(message, convert_currency, base, quote)
    else:
        try:
            request_currency, from_, to_, amount = GottenCurrency.get_price(base, quote, amount)
            text = f'Результат конверсии: {amount} {from_} = {request_currency} {to_}'
        except Exception as e:
            bot.send_message(message.chat.id, f'Непредвиденная ошибка:\n{e}')
        else:
            bot.send_message(message.chat.id, text)


bot.polling()
