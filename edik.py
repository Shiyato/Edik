from sqlalchemy import create_engine
from PIL import Image
from time import sleep
from telebot import TeleBot, types
import os

with open('config.txt', 'r') as file:
    #Set options from config.txt
    options_list = dict()

    for line in file:
        line_name = line[:line.find(':')]
        line_value = line[line.find(':') + 2:].rstrip('\n')
        options_list[line_name] = line_value
    
    token = options_list.get('token')
    db_pass = options_list.get('db_password')
    db_host = options_list.get('db_host')
    db_name = options_list.get('db_name')

engine = create_engine(f"mysql+pymysql://root:{db_pass}@{db_host}/{db_name}") #Connect to DB

bot = TeleBot(token)



@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет, я - Эдик, бот, созданный чтобы помогать людям учиться (^_^)")
    sleep(3)
    bot.send_message(message.chat.id, "Может быть, у тебя есть любимое дело/хобби, которым тебе нравится заниматься? Или просто хочешь стать успешнее и учиться с намного большей эффективностью?")
    sleep(5)
    bot.send_message(message.chat.id, "Тогда, я помогу тебе.")
    sleep(2)
    help(message)

#photo = Image.open('lofi_girl.jpg')
#bot.send_photo(message.chat.id, photo=photo, caption="")

@bot.message_handler(commands=['help', 'h'])
def help(message):
    bot.send_message(message.chat.id, "Моя основная задача - это рассказать тебе о персональной модели обучения(ПМО).\n\n • Если хочешь узнать о ней, используй /edu или /e \n__________________________________________\n\nТакже я могу помочь с постановкой твоих личных целей и составлении планов (Все цели и планы сохраняются).\n\n • Чтобы начать ставить цели используй /aims или /a\n\n • Для планов используй /plans или /p\n__________________________________________\n\n • Вызвать список команд можно, используя /help или /h")

@bot.message_handler(commands=['edu', 'e'])
def education(message):
    bot.send_message(message.chat.id, "Итак, начнём")

    markup = types.ReplyKeyboardMarkup()

    yes = types.KeyboardButton('Есть')
    no = types.KeyboardButton('Нет')

    markup.row(yes, no)

    sleep(1)
    bot.send_message(message.chat.id, "Есть ли у тебя есть любимое дело, которому ты учишься или хотел бы научиться?", reply_markup=markup)

"""@bot.callback_query_handler(func=lambda call: True)
def handle(call):
    answers = {
        "yea1": "Отлично",
        "no1": "Хорошо, тогда выбери его!"
    }
    bot.send_message(call.message.chat.id, answers.get(call.data))"""

@bot.message_handler(commands=['aims', 'a'])
def aims(message):
    pass #TODO aims edit

@bot.message_handler(commands=['plans', 'p'])
def plans(message):
    pass #TODO plans edit


bot.polling(none_stop=True, interval=0) #Start the bot