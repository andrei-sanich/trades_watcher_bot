import telebot
import config
import time
import logging
<<<<<<< HEAD
from parser import (
    check_instrument,
    parse_table,
    get_info,
    get_diff,
    check,
    get_report)
=======
from parser import *
>>>>>>> 8fbb20598c3c1c0167ba2ee90ee41d1fbe2e4f00


bot = telebot.TeleBot(config.TOKEN)
global instrument
instrument = ''


@bot.message_handler(commands=['start'])
def handle_start(message):
    chat = message.chat.id
    msg = bot.send_message(chat, "Введите код инструмента")
    bot.register_next_step_handler(msg, askInstrument)


def askInstrument(message):
    global instrument
    chat = message.chat.id
    text = message.text
    if check_instrument(text):
        bot.send_message(chat, "Для наблюдения за ходом торгов по " + text + " введите команду /watch")
        instrument = text
    else:
        msg = bot.send_message(chat, "Такого инструмента нет, проверьте и введите повторно")
        bot.register_next_step_handler(msg, askInstrument)


@bot.message_handler(commands=['watch'])
def handle_watch(message):
    global instrument
    chat = message.chat.id
    finish = False
    while not finish:
        html = get_html(config.URL_TRADES)
        info = get_info(get_diff(parse_table(html, instrument)))
        if info:
            for i in info:
                bot.send_message(chat, i)
        finish = check(html)
    bot.send_message(chat, "Торги завершены! Запускается формирование отчета, ожидайте")
    time.sleep(1)    
    report = get_report(html, instrument)
    bot.send_message(chat, report)
    rotate_files()


if __name__ == '__main__':
    try:
        bot.polling(none_stop=True)
    except Exception as err:
        logging.error(err)
        time.sleep(5)
        print("Internet error!")