import telebot
import os

with open('token.txt', 'r') as file:
    token = file.read()

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Reply")

bot.polling(none_stop=True, interval=0)