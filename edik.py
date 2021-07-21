from config_reader import token
from sqlalchemy import create_engine
from PIL import Image
from time import sleep
from telebot import TeleBot, types
import os, db


# Bot's message handlers
bot = TeleBot(token) # Creating a bot object

@bot.message_handler(func=lambda message: message.id - 1 == db.session.query(db.Support).filter(db.Support.user_id == message.user_from.id).first().last_quesion_id)
def quesion(message):
    bot.send_message(message.chat.id, "quesion")
    bot.send_message(message.chat.id, "-- Извините, эта часть чат бота ещё в разработке (T_T) --") #TODO


@bot.message_handler(commands=['start'])
def start(message):
    username = message.from_user.username
    user_id = message.from_user.id
    user = db.session.query(db.User).filter(db.User.username == username).first()

    print("NEW START", user)

    if not user:
        user = db.User(username=username)
        support = db.Support(user_id=user_id)
        db.session.add_all([user, support])
        db.session.commit()

    bot.send_message(message.chat.id, "Привет, я - Эдик, бот, созданный чтобы помогать людям учиться (^_^)")
    sleep(3)
    bot.send_message(message.chat.id, "Может быть, у тебя есть любимое дело/хобби, которым тебе нравится заниматься? Или просто хочешь стать успешнее и учиться с большей эффективностью?")
    sleep(5)
    bot.send_message(message.chat.id, "Тогда, я помогу тебе.")
    sleep(2)
    help(message)


@bot.message_handler(commands=['help', 'h'])
def help(message):
    bot.send_message(message.chat.id, "Моя основная задача - это рассказать тебе о персональной модели обучения(ПМО) и повысить эффективность твоего обучения.\n\n • Если хочешь начать, используй /edu или /e \n__________________________________________\n\nТакже я могу помочь с постановкой твоих личных целей и составлении планов (Все цели и планы сохраняются).\n\n • Чтобы начать ставить цели используй /aims или /a\n\n • Для планов используй /plans или /p\n__________________________________________\n\n • Вызвать список команд можно, используя /help или /h")

@bot.message_handler(commands=['edu', 'e'])
def education(message):
    username = message.from_user.username
    user_id = message.from_user.id
    progress = db.session.query(db.Progress).filter(db.Progress.user_id == user_id).first()

    def new_edu():
        bot.send_message(message.chat.id, "Итак, начнём")
        sleep(1)
        bot.send_message(message.chat.id, "Для начала, вспомни о том, чему ты хочешь научиться. ")

    if progress:
        bot.send_message(message.chat.id, f"Выбери блок о котором хочешь послушать. (Ты остановился на блоке {progress.part_number}) ")
        bot.send_message(message.chat.id, "-- Извините, эта часть чат бота ещё в разработке (T_T) --") #TODO education block choise
    else:
        prog = db.Progress(user_id=user_id, edu_started=True) #FIXME delete edu_started=True after a table update
        db.session.add(prog)
        db.session.commit()
        new_edu()
    

@bot.message_handler(commands=['aims', 'a'])
def aims(message):
    bot.send_message(message.chat.id, "Вот список твоих целей")


@bot.message_handler(commands=['plans', 'p'])
def plans(message):
    plans_list = db.session.query(db.Plans).filter(db.Plans.user_id == message.from_user.id)
    bot.send_message(message.chat.id, "Вот список твоих планов:\n")

if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0) #Starting the bot