#!/usr/bin/env python

import telebot
import os

from pathlib import Path
from dotenv import load_dotenv
from config import d_massages

from db_and_pars_functions import start_parser, get_cities, get_city_info

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)
TOKEN = os.getenv("TOKEN")


def app_start():
    bot = telebot.TeleBot(TOKEN)
    bot_name = bot.get_me().username  # получаем имя нашего бота

    @bot.message_handler(commands=["start"])
    def bot_info(message: telebot.types.Message):
        bot.reply_to(message, d_massages["start"])

    @bot.message_handler(commands=["parse"])
    def bot_upd_db(message: telebot.types.Message):
        start_parser()
        bot.reply_to(message, d_massages['parse'])

    @bot.message_handler(commands=["cities"])
    def bot_get_cities(message: telebot.types.Message):
        city_list = get_cities()
        city_str = "".join(list(map(lambda x: x + "\n", city_list)))
        bot.reply_to(message, city_str)

    @bot.message_handler(content_types=["text"])
    def get_city_details(message: telebot.types.Message):
        res_text = message.text.title()

        if len(message.text) <= 40:  # cкипаем все сообщения длиной более 40 символов
            if f"@{bot_name}" in message.text.split():  # если тагнут бот
                message.text = "".join(list(filter(lambda x: x != f"@{bot_name}", message.text.split())))
                relevant_cities_list = list(
                    filter(lambda x: message.text.lower() in x, map(lambda s: s.lower(), get_cities())))
                relevant_cities_msg = "".join(list(map(lambda x: x.title() + "\n", relevant_cities_list)))

                # если есть города содержащие введеный текст
                if relevant_cities_msg:
                    bot.send_message(message.chat.id,
                                     f"список подходящих для '{message.text}' городов:\n" + relevant_cities_msg)
                else:
                    bot.send_message(message.chat.id,
                                     f"нет подходящих городов для '{message.text}'" + relevant_cities_msg)

            # Если не тагаем бота, а пишим просто в чат
            elif res_text in get_cities():
                population, link = get_city_info(res_text)
                bot.send_message(message.chat.id, f"""
город: {res_text}
население: {population} человек
ссылка на wiki: {link}""")

    bot.polling(none_stop=True)


if __name__ == "__main__":
    start_parser()  # создаем бд и наполняем/обновляем
app_start()  # cтартуем приложение
