from config_reader import token
from sqlalchemy import create_engine
from PIL import Image
from time import sleep
from telebot import TeleBot, types
import os, db, random



bot = TeleBot(token) # Creating a bot object

#TODO Add a check of database entry values

def set_support(user_id, values:dict):
    db.session.query(db.Support).filter(db.Support.user_id == user_id).update(values, synchronize_session='fetch')

# Plans functions

def add_plan(user_id, text):
    plan = db.Plans(plan_name=text, user_id=user_id)
    db.session.add(plan)
    db.session.commit()

def edit_plan(plan_id, text): #FIXME
    db.session.query(db.Plans).filter(db.Plans.id == plan_id).update({"plan_name" == text}, synchronize_session='fetch')

def delete_plan(plan_id): #FIXME
    plan = db.session.query(db.Plans).filter(db.Plans.id == plan_id).first()
    db.session.delete(plan)
    db.session.commit()

def complete_plan():
    pass #TODO


# Plans points functions

def add_plan_point(plan_id, number):
    plan_points = db.session.query(db.PlansPoints).filter(db.PlansPoints.plan_id == plan_id).all()

    for point in plan_points: # Move next points number
        db.session.db.query(db.PlansPoints).filter(db.PlansPoints.number == point.number and db.PlansPoints.number >= number).update({"number": point.number + 1}, synchronize_session='fetch')

    plan_point = db.PlansPoints(plan_id=plan_id, number=number)
    db.session.add(plan_point)
    db.session.commit()

def edit_plan_point():
    pass #TODO

def delete_plan_point():
    pass #TODO


# Aims functions

def add_aim(user_id, text):
        aim = db.Aims(user_id=user_id, aim_name=text)
        db.session.add(aim)
        db.session.commit()

def edit_aim(aim_q, text):
    aim_q.update({"aim_name": text}, synchronize_session='fetch')
    db.session.commit()

def delete_aim(aim_q):
    aim = aim_q.first()
    db.session.delete(aim)
    db.session.commit()

def complete_aim(aim_q):
    aim_q.update({"completed": True}, synchronize_session='fetch')
    db.session.commit()

def uncomplete_aim(aim_q):
    aim_q.update({"completed": False}, synchronize_session='fetch')
    db.session.commit()

def choise_aim(user_id, text=None):
    if text:
        return db.session.query(db.Aims).filter(db.Aims.user_id == user_id and db.Aims.aim_name == text)
    else:
        return db.session.query(db.Aims).filter(db.Aims.user_id == user_id)


# Find user function
def find_user(tele_id):
    return db.session.query(db.User).filter(db.User.tele_id == tele_id).first()


# Quesions handler function
def que_handler(message):
    user = find_user(message.from_user.id)
    if user:
        user_id = user.id
        support = db.session.query(db.Support).filter(db.Support.user_id == user_id).first()
        if support: return support.last_quesion_id == message.message_id - 1
    return False



# Bot's message handlers

@bot.message_handler(commands=['start'])
def start(message):
    user_tele_id = message.from_user.id
    user = find_user(user_tele_id)

    if not user:
            user_o = db.User(tele_id=user_tele_id)
            db.session.add(user_o)
            db.session.commit()
            user = find_user(user_tele_id)
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
    user_tele_id = message.from_user.id
    user_id = find_user(user_tele_id).id
    progress = db.session.query(db.Progress).filter(db.Progress.user_id == user_id).first()

    def new_edu():
        bot.send_message(message.chat.id, "Итак, начнём")
        sleep(1)
        bot.send_message(message.chat.id, "Для начала, вспомни о том, чему ты хочешь научиться. ")
        bot.send_message(message.chat.id, "-- Извините, эта часть чат бота ещё в разработке (T_T) --") #TODO education block choise

    if progress:
        bot.send_message(message.chat.id, f"Выбери блок с которого хочешь продолжить. (Ты остановился на блоке {progress.part_number}) ")
        bot.send_message(message.chat.id, "-- Извините, эта часть чат бота ещё в разработке (T_T) --") #TODO education block choise
    else:
        prog = db.Progress(part_number=1)
        db.session.add(prog)
        db.session.commit()
        new_edu()



@bot.message_handler(commands=['aims', 'a'])
def aims(message):
    user = find_user(message.from_user.id)
    aims = db.session.query(db.Aims).filter(db.Aims.user_id == user.id).all()

    def aims_help():
        bot.send_message(message.chat.id, " • Если хочешь добавить цель - используй /add_aim или /aa\n • Если хочешь редактировать цель - используй /edit_aim или /ea\n • Если хочешь удалить цель - используй /del_aim или /da\n • Если хочешь выполнить цель - используй /complete_aim или /ca\n • Если хочешь, чтобы цель не была выполнена - используй /uncomplete_aim или /ua")

    if aims:
        aims_text = ''
        for aim in aims:
            star = '★' if aim.completed else '☆'
            aims_text += f'  {star} ' + aim.aim_name + '\n'
        bot.send_message(message.chat.id, "Вот список твоих целей:\n" + aims_text)
    else: 
        bot.send_message(message.chat.id, "У тебя ещё нет сохранённых целей.\n")

    aims_help()

@bot.message_handler(commands=['add_aim', 'aa'])
def add_aim_h(message):
    user = find_user(message.from_user.id)
    set_support(user.id, {"last_quesion_id": message.message_id + 1, "last_quesion_num": "a1"})
    bot.send_message(message.chat.id, "Введи цель:")


@bot.message_handler(commands=['edit_aim', 'ea'])
def edit_aim_h(message):
    user = find_user(message.from_user.id)
    aims = db.session.query(db.Aims).filter(db.Aims.user_id == user.id).all()

    if choise_aim(user.id).all(): 
        set_support(user.id, {"last_quesion_id": message.message_id + 1, "last_quesion_num": "a2"})
        markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, selective=True)
        for aim in aims:
            aim_name = types.KeyboardButton(aim.aim_name)
            markup.add(aim_name)
        bot.send_message(message.chat.id, "Выбери цель:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Ты ещё не сохранял цели")

@bot.message_handler(commands=['delete_aim', 'da'])
def delete_aim_h(message):
    user = find_user(message.from_user.id)
    aims = db.session.query(db.Aims).filter(db.Aims.user_id == user.id).all()

    if choise_aim(user.id).all(): 
        set_support(user.id, {"last_quesion_id": message.message_id + 1, "last_quesion_num": "a3"})
        markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, selective=True)
        for aim in aims:
            aim_name = types.KeyboardButton(aim.aim_name)
            markup.add(aim_name)
        bot.send_message(message.chat.id, "Выбери цель:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Ты ещё не сохранял цели")

@bot.message_handler(commands=['complete_aim', 'ca'])
def edit_aim_h(message):
    user = find_user(message.from_user.id)
    aims = db.session.query(db.Aims).filter(db.Aims.user_id == user.id).all()

    if choise_aim(user.id).all(): 
        set_support(user.id, {"last_quesion_id": message.message_id + 1, "last_quesion_num": "a4"})
        markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, selective=True)
        for aim in aims:
            aim_name = types.KeyboardButton(aim.aim_name)
            markup.add(aim_name)
        bot.send_message(message.chat.id, "Выбери цель:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Ты ещё не сохранял цели")

@bot.message_handler(commands=['uncomplete_aim', 'ua'])
def edit_aim_h(message):
    user = find_user(message.from_user.id)
    aims = db.session.query(db.Aims).filter(db.Aims.user_id == user.id).all()

    if choise_aim(user.id).all(): 
        set_support(user.id, {"last_quesion_id": message.message_id + 1, "last_quesion_num": "a5"})
        markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, selective=True)
        for aim in aims:
            aim_name = types.KeyboardButton(aim.aim_name)
            markup.add(aim_name)
        bot.send_message(message.chat.id, "Выбери цель:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Ты ещё не сохранял цели")



@bot.message_handler(commands=['plans', 'p'])
def plans(message):
    plans_list = db.session.query(db.Plans).filter(db.Plans.user_id == find_user(message.from_user.id).id).all()
    bot.send_message(message.chat.id, "Вот список твоих планов:\n")
    bot.send_message(message.chat.id, "-- Извините, эта часть чат бота ещё в разработке (T_T) --") #TODO


@bot.message_handler(commands=['dev', 'd'])
def dev(message):
    if message.from_user.id == 870182558:
        db.update_tables()
        print(" -- TABLES UPDATED -- ")
    else: 
        print(" -- FAIL TABLES UPDATE -- ")


@bot.message_handler(func=que_handler)
def quesion(message):
    user = find_user(message.from_user.id)
    aim_q = choise_aim(user.id, message.text)
    rand_smile = random.choice(["┏( ͡❛ ͜ʖ ͡❛)┛", "┌( ಠ‿ಠ)┘", "\( ͡❛ ͜ʖ ͡❛)/", "\(•◡•)/", "( ͡❛ ͜ʖ ͡❛)", "(>‿◠)✌", "ʕ•ᴥ•ʔ", "(◉◡◉)", "(◕‿◕)", "( ́ ◕◞ε◟◕`)", "(^ↀᴥↀ^)"])
    support = db.session.query(db.Support).filter(db.Support.user_id == user.id).first()

    if support.last_quesion_num == 'a1':
        if db.session.query(db.Aims).filter(db.Aims.user_id == user.id and db.Aims.aim_name == message.text).first():
            print(db.session.query(db.Aims).filter(db.Aims.user_id == user.id and db.Aims.aim_name == message.text).first())
            bot.send_message(message.chat.id, "Прости, но целям нельзя давать одинаковые имена")
        else:
            add_aim(user.id, message.text)
            bot.send_message(message.chat.id, "Цель сохранена! " + rand_smile)

    if support.last_quesion_num == 'a2_1':
        edit_aim(aim_q, message.text)
        bot.send_message(message.chat.id, "Цель изменена! " + rand_smile)

    if support.last_quesion_num == 'a2':
        set_support(user.id, {"last_quesion_id": message.message_id + 1, "last_quesion_num": "a2_1"})
        bot.send_message(message.chat.id, "Введи название:")

    if support.last_quesion_num == 'a3':
        delete_aim(aim_q)
        bot.send_message(message.chat.id, "Цель удалена! " + rand_smile)

    if support.last_quesion_num == 'a4':
        complete_aim(aim_q)
        bot.send_message(message.chat.id, "Цель выпонена! " + rand_smile)

    if support.last_quesion_num == 'a5':
        uncomplete_aim(aim_q)
        bot.send_message(message.chat.id, "Теперь цель не выпонена! " + rand_smile)

    
    
if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0) #Starting the bot