from config_reader import token
from sqlalchemy import create_engine
from PIL import Image
from time import sleep
from telebot import TeleBot, types
import os, db


# Bot's message handlers
bot = TeleBot(token) # Creating a bot object

def find_user(username):
    return db.session.query(db.User).filter(db.User.username == username).first()

def que_handler(message):
    user = find_user(message.from_user.username)
    if user:
        user_id = user.id
        support = db.session.query(db.Support).filter(db.Support.user_id == user_id).first()
        if support: return support.last_quesion_id == message.message_id - 1
    return False


@bot.message_handler(commands=['start'])
def start(message):
    username = message.from_user.username
    user = find_user(username)

    if not user:
        user_o = db.User(username=username)
        db.session.add(user_o)
        db.session.commit()
        user = find_user(username)
        support = db.Support(user_id=user.id)
        db.session.add(support)
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
    user_id = find_user(username).id
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
    plans_list = db.session.query(db.Plans).filter(db.Plans.user_id == find_user(message.from_user.username).id)
    bot.send_message(message.chat.id, "Вот список твоих планов:\n")

@bot.message_handler(func=que_handler)
def quesion(message):
    bot.send_message(message.chat.id, "quesion")
    bot.send_message(message.chat.id, "-- Извините, эта часть чат бота ещё в разработке (T_T) --") #TODO

if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0) #Starting the bot