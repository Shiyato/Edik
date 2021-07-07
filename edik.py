import telebot
import os

token = pass #reading a token from txt file


bot = telebot.TeleBot("TOKEN")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.from_user.id, "Привет")

bot.polling(none_stop=True, interval=0)