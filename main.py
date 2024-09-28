import telebot
import config
from extension import *

bot = telebot.TeleBot(token=config.TOKEN)


@bot.message_handler(commands=['start', 'help'])
def helps(message: telebot.types.Message):
    bot.send_message(message.chat.id, f'Привет {message.from_user.first_name.capitalize()} '
                                      f'{message.from_user.last_name.capitalize()
                                      if message.from_user.last_name is not None else ""}\n'
                                      f'Для начала работы введите команду /values или /button_ver')


@bot.message_handler(commands=['values'])
def values(message: telebot.types.Message):
    text = 'Доступные валюты:'
    for key in keys:
        text += f'\n{key}: {keys[key]}'
    bot.reply_to(message, text +
                 '\nЗначения вводить в формате {валюта_валюта_количество}')


"""Самостоятельная реализация через InlineButton"""
@bot.message_handler(commands=['button_ver'])
def button_ver(message: telebot.types.Message):
    markup = telebot.types.InlineKeyboardMarkup(row_width=3)
    buttons = []
    for i, key in enumerate(keys_pair):
        button = telebot.types.InlineKeyboardButton(keys_pair[i], callback_data=keys_pair[i])
        buttons.append(button)
    markup.add(*buttons)
    bot.send_message(message.chat.id, 'Выберите валютy', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback(call: telebot.types.CallbackQuery):
    v_1, v_2 = call.data.split('/')[0], call.data.split('/')[1]
    r = requests.get(f'https://min-api.cryptocompare.com/data/price?fsym={v_1}&tsyms={v_2}')
    bot.send_message(call.message.chat.id, f'{v_1} = {json.loads(r.content)[v_2]} {v_2}')


@bot.message_handler(content_types=['text'])
def convert(message: telebot.types.Message):
    try:
        values_ = [cap.capitalize() for cap in message.text.split()]
        if len(values_) > 3:
            raise APIException('Слишком много параметров.')
        elif len(values_) < 3:
            raise APIException('Слишком мало параметров')

        quote, base, amount = values_
        print(quote, base, amount)
        total_base = CryptoConverter.convert(quote, base, amount)
    except APIException as e:
        bot.reply_to(message, f'Ошибка пользователя\n{e}')

    except Exception as e:
        bot.reply_to(message, f'Не удалось обработать команду\n{e}')
    else:
        text = f'{amount} x {quote} = {total_base * float(amount)} {base}'
        bot.send_message(message.chat.id, text)



if __name__ == '__main__':
    bot.polling(none_stop=True)
