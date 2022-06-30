import telebot
import os
from pathlib import Path
from dotenv import load_dotenv

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

TOKEN = os.getenv("TOKEN")


bot = telebot.TeleBot(TOKEN)


# @bot.message_handler(content_types="text")
@bot.message_handler(commands=["start", "help"])
def info(message: telebot.types.Message):
    bot.reply_to(message, "привет")
    # bot.send_message(message.chat.id, f"Welcome, {message.chat.username}")


bot.polling(none_stop=True)
