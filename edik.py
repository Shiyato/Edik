from config_reader import token
from sqlalchemy import create_engine
from PIL import Image
from time import sleep
from telebot import TeleBot, types
from flask import Flask
import os, db

# Code for waking up a heroku dynos

wake = Flask(__name__)

@wake.route('/', methods=['GET'])
def wake_app():
    return "<h1>Go to @self_education_ru_bot for use the bot</h1 style='text-align:center'>"




# Bot's message handlers
bot = TeleBot(token) # Creating a bot object

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет, я - Эдик, бот, созданный чтобы помогать людям учиться (^_^)")
    sleep(3)
    bot.send_message(message.chat.id, "Может быть, у тебя есть любимое дело/хобби, которым тебе нравится заниматься? Или просто хочешь стать успешнее и учиться с намного большей эффективностью?")
    sleep(5)
    bot.send_message(message.chat.id, "Тогда, я помогу тебе.")
    sleep(2)
    help(message)


@bot.message_handler(commands=['help', 'h'])
def help(message):
    bot.send_message(message.chat.id, "Моя основная задача - это рассказать тебе о персональной модели обучения(ПМО).\n\n • Если хочешь узнать о ней, используй /edu или /e \n__________________________________________\n\nТакже я могу помочь с постановкой твоих личных целей и составлении планов (Все цели и планы сохраняются).\n\n • Чтобы начать ставить цели используй /aims или /a\n\n • Для планов используй /plans или /p\n__________________________________________\n\n • Вызвать список команд можно, используя /help или /h")

@bot.message_handler(commands=['edu', 'e'])
def education(message):
    bot.send_message(message.chat.id, "Итак, начнём")
    sleep(1)
    bot.send_message(message.chat.id, "Для начала вспомни то, чему ты хочешь научиться и чётко сформулируй результат которого ты хочешь достичь и за какой промежуток времени.")


@bot.message_handler(commands=['aims', 'a'])
def aims(message):
    bot.send_message(message.chat.id, "Вот список твоих целей")


@bot.message_handler(commands=['plans', 'p'])
def plans(message):
    #plans_list = db.session.query(db.Plans).filter(db.Plans.user_id == message.from_user.id)
    bot.send_message(message.chat.id, "Вот список твоих планов:\n")

bot.polling(none_stop=True, interval=0) #Starting the bot