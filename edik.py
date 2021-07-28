from telebot import TeleBot, types
from config_reader import bot_token
import random
import db


bot = TeleBot(bot_token)  # Creating a bot object


# Quesions handler function
def que_handler(message):
    user = db.find_user(message.from_user.id)
    if user:
        user_id = user.id
        support = db.session.query(db.Support).filter(db.Support.user_id == user_id).first()
        if support: return support.last_quesion_id == message.message_id - 1
    return False


# Bot's message handlers

@bot.message_handler(commands=['start'])
def start(message):
    user_tele_id = message.from_user.id
    user = db.find_user(user_tele_id)

    if not user:
        user_o = db.User(tele_id=user_tele_id)
        db.session.add(user_o)
        db.session.commit()
        user = db.find_user(user_tele_id)
        support = db.Support(user_id=user.id)
        db.session.add(support)
        db.session.commit()

    bot.send_message(message.chat.id, "Привет, я - Эдик, бот, созданный чтобы помогать людям учиться (^_^)")
    bot.send_message(message.chat.id, "Может быть, у тебя есть любимое дело/хобби, которым тебе нравится заниматься?" +
                                      " Или просто хочешь стать успешнее и учиться с большей эффективностью?")
    bot.send_message(message.chat.id, "Тогда, я помогу тебе.")
    help(message)


@bot.message_handler(commands=['help', 'h'])
def help(message):
    bot.send_message(message.chat.id, "Моя основная задача - это рассказать тебе о персональной модели обучения(ПМО)" +
                                      " и повысить эффективность твоего обучения.\n\n" +
                                      "• Если хочешь начать, используй /edu или /e\n" +
                                      "__________________________________________\n\n" +
                                      "Также я могу помочь с постановкой твоих личных целей " +
                                      "и составлении планов (Все цели и планы сохраняются).\n\n" +
                                      "• Чтобы начать ставить цели используй /aims или /a\n" +
                                      "• Для планов используй /plans или /p\n" +
                                      "__________________________________________\n\n" +
                                      "• Вызвать список команд можно, используя /help или /h")


@bot.message_handler(commands=['edu', 'e'])
def education(message):
    user_tele_id = message.from_user.id
    user_id = db.find_user(user_tele_id).id
    progress = db.session.query(db.Progress).filter(db.Progress.user_id == user_id).first()

    def new_edu():
        bot.send_message(message.chat.id, "Итак, начнём")
        bot.send_message(message.chat.id, "Для начала, вспомни о том, чему ты хочешь научиться. ")
        bot.send_message(message.chat.id,
                         "-- Извините, эта часть чат бота ещё в разработке (T_T) --")  # TODO education block choise

    if progress:
        bot.send_message(message.chat.id,
                         f"Выбери блок с которого хочешь продолжить. (Ты остановился на блоке {progress.part_number}) ")
        bot.send_message(message.chat.id,
                         "-- Извините, эта часть чат бота ещё в разработке (T_T) --")  # TODO education block choise
    else:
        prog = db.Progress(part_number=1)
        db.session.add(prog)
        db.session.commit()
        new_edu()


@bot.message_handler(commands=['aims', 'a'])
def aims(message):
    user = db.find_user(message.from_user.id)
    aims = db.session.query(db.Aims).filter(db.Aims.user_id == user.id).all()

    def aims_help():
        bot.send_message(message.chat.id, " • Если хочешь добавить цель - используй /add_aim или /aa\n\n" +
                                          "• Если хочешь редактировать цель - используй /edit_aim или /ea\n\n" +
                                          "• Если хочешь удалить цель - используй /del_aim или /da\n\n" +
                                          "• Если хочешь выполнить цель - используй /complete_aim или /ca\n\n" +
                                          " • Если хочешь, чтобы цель " +
                                          "не была выполнена - используй /uncomplete_aim или /ua")

    if aims:
        aims_text = ''
        for aim in aims:
            star = '★' if aim.completed else '☆'
            aims_text += f'  {star} {aim.aim_name}\n'
        bot.send_message(message.chat.id, "Вот список твоих целей:\n" + aims_text)
    else:
        bot.send_message(message.chat.id, "У тебя ещё нет сохранённых целей.\n")

    aims_help()


@bot.message_handler(commands=['add_aim', 'aa'])
def add_aim_h(message):
    user = db.find_user(message.from_user.id)
    db.set_support(user.id, {"last_quesion_id": message.message_id + 1, "last_quesion_num": "a1"})
    bot.send_message(message.chat.id, "Введи цель:")


@bot.message_handler(commands=['edit_aim', 'ea'])
def edit_aim_h(message):
    user = db.find_user(message.from_user.id)
    aims = db.session.query(db.Aims).filter(db.Aims.user_id == user.id).all()

    if db.choise_aim(user.id).all():
        db.set_support(user.id, {"last_quesion_id": message.message_id + 1, "last_quesion_num": "a2"})
        markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, selective=True)
        for aim in aims:
            aim_name = types.KeyboardButton(aim.aim_name)
            markup.add(aim_name)
        bot.send_message(message.chat.id, "Выбери цель:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Ты ещё не сохранял цели")


@bot.message_handler(commands=['delete_aim', 'da'])
def delete_aim_h(message):
    user = db.find_user(message.from_user.id)
    aims = db.session.query(db.Aims).filter(db.Aims.user_id == user.id).all()

    if db.choise_aim(user.id).all():
        db.set_support(user.id, {"last_quesion_id": message.message_id + 1, "last_quesion_num": "a3"})
        markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, selective=True)
        for aim in aims:
            aim_name = types.KeyboardButton(aim.aim_name)
            markup.add(aim_name)
        bot.send_message(message.chat.id, "Выбери цель:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Ты ещё не сохранял цели")


@bot.message_handler(commands=['complete_aim', 'ca'])
def complete_aim_h(message):
    user = db.find_user(message.from_user.id)
    aims = db.session.query(db.Aims).filter(db.Aims.user_id == user.id).all()

    if db.choise_aim(user.id).all():
        db.set_support(user.id, {"last_quesion_id": message.message_id + 1, "last_quesion_num": "a4"})
        markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, selective=True)
        for aim in aims:
            aim_name = types.KeyboardButton(aim.aim_name)
            markup.add(aim_name)
        bot.send_message(message.chat.id, "Выбери цель:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Ты ещё не сохранял цели")


@bot.message_handler(commands=['uncomplete_aim', 'ua'])
def uncomplete_aim_h(message):
    user = db.find_user(message.from_user.id)
    aims = db.session.query(db.Aims).filter(db.Aims.user_id == user.id).all()

    if db.choise_aim(user.id).all():
        db.set_support(user.id, {"last_quesion_id": message.message_id + 1, "last_quesion_num": "a5"})
        markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, selective=True)
        for aim in aims:
            aim_name = types.KeyboardButton(aim.aim_name)
            markup.add(aim_name)
        bot.send_message(message.chat.id, "Выбери цель:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Ты ещё не сохранял цели")


@bot.message_handler(commands=['plans', 'p'])
def plans(message):
    user_tele_id = message.from_user.id
    user = db.find_user(user_tele_id)
    plans_query = db.session.query(db.Plans).filter(db.Plans.user_id == user.id)
    plans_list = plans_query.all()

    def plans_help():
        bot.send_message(message.chat.id, " • Если хочешь добавить план - используй /add_plan или /ap\n\n" +
                                          "• Если хочешь редактировать план - используй /edit_plan или /ep\n\n" +
                                          "• Если хочешь удалить план - используй /del_plan или /dp\n\n" +
                                          "• Если хочешь выполнить план - используй /complete_plan или /cp\n\n" +
                                          "• Если хочешь, чтобы план не был выполнен" +
                                          " - используй /uncomplete_plan или /up")

    if plans_list:
        plans_text = ''
        for plan in plans_list:
            star = '★' if plan.completed else '☆'
            plans_text += f'  {star} {plan.plan_name}\n'
        bot.send_message(message.chat.id, "Вот список твоих планов:\n" + plans_text)
    else:
        bot.send_message(message.chat.id, "У тебя ещё нет сохранённых планов.")

    plans_help()


@bot.message_handler(commands=['add_plan', 'ap'])
def add_plan_h(message):
    user = db.find_user(message.from_user.id)
    db.set_support(user.id, {"last_quesion_id": message.message_id + 1, "last_quesion_num": "p1"})
    bot.send_message(message.chat.id, "Введи название плана:")


@bot.message_handler(commands=['edit_plan', 'ep'])
def edit_plan_h(message):
    user = db.find_user(message.from_user.id)
    plans = db.session.query(db.Plans).filter(db.Plans.user_id == user.id).all()

    if db.choise_plan(user.id).all():
        db.set_support(user.id, {"last_quesion_id": message.message_id + 1, "last_quesion_num": "p2"})
        markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, selective=True)
        for plan in plans:
            plan_name = types.KeyboardButton(plan.plan_name)
            markup.add(plan_name)
        bot.send_message(message.chat.id, "Выбери план:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Ты ещё не сохранял планы")


@bot.message_handler(commands=['delete_plan', 'dp'])
def delete_plan_h(message):
    user = db.find_user(message.from_user.id)
    plans = db.session.query(db.Plans).filter(db.Plans.user_id == user.id).all()

    if db.choise_plan(user.id).all():
        db.set_support(user.id, {"last_quesion_id": message.message_id + 1, "last_quesion_num": "p3"})
        markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, selective=True)
        for plan in plans:
            plan_name = types.KeyboardButton(plan.plan_name)
            markup.add(plan_name)
        bot.send_message(message.chat.id, "Выбери план:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Ты ещё не сохранял планы")


@bot.message_handler(commands=['complete_plan', 'cp'])
def complete_plan_h(message):
    user = db.find_user(message.from_user.id)
    plans = db.session.query(db.Plans).filter(db.Plans.user_id == user.id).all()

    if db.choise_plan(user.id).all():
        db.set_support(user.id, {"last_quesion_id": message.message_id + 1, "last_quesion_num": "p4"})
        markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, selective=True)
        for plan in plans:
            plan_name = types.KeyboardButton(plan.plan_name)
            markup.add(plan_name)
        bot.send_message(message.chat.id, "Выбери план:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Ты ещё не сохранял планы")


@bot.message_handler(commands=['uncomplete_plan', 'up'])
def uncomplete_plan_h(message):
    user = db.find_user(message.from_user.id)
    plans = db.session.query(db.Plans).filter(db.Plans.user_id == user.id).all()

    if db.choise_plan(user.id).all():
        db.set_support(user.id, {"last_quesion_id": message.message_id + 1, "last_quesion_num": "p5"})
        markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, selective=True)
        for plan in plans:
            plan_name = types.KeyboardButton(plan.plan_name)
            markup.add(plan_name)
        bot.send_message(message.chat.id, "Выбери план:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Ты ещё не сохранял планы")


@bot.message_handler(commands=['dev', 'd'])
def dev(message):
    if message.from_user.id == 870182558:
        db.update_tables()
        print(" -- TABLES UPDATED -- ")
    else:
        print(" -- FAIL TO UPDATE TABLES -- ")


@bot.message_handler(func=que_handler)
def quesion(message):
    user = db.find_user(message.from_user.id)
    aim_q = db.choise_aim(user.id, message.text)
    plan_q = db.choise_plan(user.id, message.text)
    rand_smile = random.choice(
        ["┏( ͡❛ ͜ʖ ͡❛)┛", "┌( ಠ‿ಠ)┘", "\( ͡❛ ͜ʖ ͡❛)/", "\(•◡•)/", "( ͡❛ ͜ʖ ͡❛)", "(>‿◠)✌", "ʕ•ᴥ•ʔ", "(◉◡◉)", "(◕‿◕)",
         "( ́ ◕◞ε◟◕`)", "(^ↀᴥↀ^)"])
    support = db.session.query(db.Support).filter(db.Support.user_id == user.id).first()

    def plan_edit():
        bot.send_message(message.chat.id, "Добавь пункты своему плану!") # TODO make an inline menu

    if support.last_quesion_num == 'a1':
        if aim_q.first():
            bot.send_message(message.chat.id, "Прости, но целям нельзя давать одинаковые имена")
        else:
            db.add_aim(user.id, message.text)
            bot.send_message(message.chat.id, "Цель сохранена! " + rand_smile)

    if support.last_quesion_num == 'a2_1':
        db.edit_aim(aim_q, message.text)
        bot.send_message(message.chat.id, "Цель изменена! " + rand_smile)

    if support.last_quesion_num == 'a2':
        db.set_support(user.id, {"last_quesion_id": message.message_id + 1, "last_quesion_num": "a2_1"})
        bot.send_message(message.chat.id, "Введи название:")

    if support.last_quesion_num == 'a3':
        db.delete_aim(aim_q)
        bot.send_message(message.chat.id, "Цель удалена! " + rand_smile)

    if support.last_quesion_num == 'a4':
        db.complete_aim(aim_q)
        bot.send_message(message.chat.id, "Цель выпонена! " + rand_smile)

    if support.last_quesion_num == 'a5':
        db.uncomplete_aim(aim_q)
        bot.send_message(message.chat.id, "Теперь цель не выпонена! " + rand_smile)

    if support.last_quesion_num == 'p1':
        if plan_q.first():
            bot.send_message(message.chat.id, "Прости, но планам нельзя давать одинаковые имена")
        else:
            db.add_plan(user.id, message.text)

            bot.send_message(message.chat.id, "План сохранён! " + rand_smile)

    if support.last_quesion_num == 'p2_1':
        db.edit_plan(plan_q, message.text)
        bot.send_message(message.chat.id, "План изменён! " + rand_smile)

    if support.last_quesion_num == 'p2':
        db.set_support(user.id, {"last_quesion_id": message.message_id + 1, "last_quesion_num": "p2_1"})
        bot.send_message(message.chat.id, "Введи название:")

    if support.last_quesion_num == 'p3':
        db.delete_aim(aim_q)
        bot.send_message(message.chat.id, "План удалён! " + rand_smile)

    if support.last_quesion_num == 'p4':
        db.complete_aim(aim_q)
        bot.send_message(message.chat.id, "План выпонен! " + rand_smile)

    if support.last_quesion_num == 'p5':
        db.uncomplete_aim(aim_q)
        bot.send_message(message.chat.id, "Теперь план не выпонен! " + rand_smile)


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)  # Starting the bot
