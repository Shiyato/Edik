from telebot import TeleBot, types
from config_reader import bot_token
import random
import db

bot = TeleBot(bot_token)  # Creating a bot object


#TODO Ограницения для планов, целей, пунктов планов. Проверка входящих в БД данных. Выбор блока обучения.

# Handler functions
def que_handler(message):
    user = db.find_user(message.from_user.id)
    if user:
        support = db.session.query(db.Support).filter(db.Support.user_id == user.id).first()
        if support: return support.last_quesion_id == message.message_id - 1
    return False


def next_handler(message):
    user = db.find_user(message.from_user.id)
    support = db.session.query(db.Support).filter(db.Support.user_id == user.id).first()
    return True if support.last_quesion_num[0] == "n" else False


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
    bot.send_message(message.chat.id, "Моя основная задача - это помочь тебе с " +
                     "повышением эффективности твоего обучения.\n\n" +
                     "• Если хочешь начать, используй /edu или /e\n" +
                     "__________________________________________\n\n" +
                     "Также я могу помочь с постановкой твоих личных целей " +
                     "и составлении планов (Все цели и планы сохраняются).\n\n" +
                     "• Чтобы начать ставить цели используй /aims или /a\n\n" +
                     "• Для планов используй /plans или /p\n" +
                     "__________________________________________\n\n" +
                     "• Вызвать список команд можно, используя /help или /h")


@bot.message_handler(commands=['edu', 'e'])
def education(message):
    user_tele_id = message.from_user.id
    user = db.find_user(user_tele_id)
    progress = db.session.query(db.Progress).filter(db.Progress.user_id == user.id).first()

    def edu_start():
        bot.send_message(message.chat.id, "Итак, начнём. Если захочешь остановиться отправь мне назад")
        bot.send_message(message.chat.id, "Для начала, вспомни то чему ты хочешь научиться," +
                                          " то чего ты хочешь достичь и то, зачем оно тебе надо." +
                                          " От твоей мотивации зависит, как быстро ты этого добьёшься" +
                                          " и добьёшься ли вообще")
        bot.send_message(message.chat.id, " * Чтобы продолжать отправляй любое сообщение, кроме команд.")
        db.set_support(user.id, {"last_quesion_num": "n1"})

    if progress:
        bot.send_message(message.chat.id,
                         f"Выбери блок с которого хочешь продолжить. (Ты остановился на блоке {progress.part_number}) ")
    else:
        prog = db.Progress(user_id=user.id)
        db.session.add(prog)
        db.session.commit()
        edu_start()


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


@bot.message_handler(func=next_handler)
def next(message):
    user = db.find_user(message.from_user.id)
    support = db.session.query(db.Support).filter(db.Support.user_id == user.id).first()

    if message.text.lower() == 'назад':
        db.set_support(user.id, {"last_quesion_num": "0"})

    if support.last_quesion_num == "n1":
        db.set_support(user.id, {"last_quesion_num": "n2"})
        bot.send_message(message.chat.id, "Самое важное, что нужно сделать для успешного обучения" +
                                          " - это поставить конктретную цель, " +
                                          "учитывая время которое ты потратишь на её выполнение, " +
                                          "поставить себе жёсткие временные рамки.")

    if support.last_quesion_num == "n2":
        db.set_support(user.id, {"last_quesion_num": "n3"})
        bot.send_message(message.chat.id, "Далее нужно разбить цель на этапы, то есть составить план. " +
                                          "План нужно выполнять постепенно, " +
                                          "а также решить сколько времени ты потратишь на выполнение каждого этапа")

    if support.last_quesion_num == "n3":
        db.set_support(user.id, {"last_quesion_num": "n4"})
        bot.send_message(message.chat.id, "Также нужно решить сколько времени на " +
                                          "обучение ты будешь тратить в неделю. " +
                                          "Например: 'я буду заниматься по 1 часу каждый день' или " +
                                          "'я буду заниматься по 2 часа каждые понедельник, среду и пятницу" +
                                          "От кол-ва выденного времени, зависит скорость обучения.")

    if support.last_quesion_num == "n3":
        db.set_support(user.id, {"last_quesion_num": "n4"})
        bot.send_message(message.chat.id, "Не забывай отдыхать! Пик концентрации человека наступает через 45 минут " +
                         "выполнения какой-либо работы, " +
                         "в идеале нужно отдыхать от учёбы по прошествии " +
                         "этого времени хотя-бы 15 мин.")

    if support.last_quesion_num == "n4":
        db.set_support(user.id, {"last_quesion_num": "n5"})
        bot.send_message(message.chat.id, "Тчательно выбирай материалы для получения информации: " +
                                          "если тебя неустраивают источники с помощью которых ты учишься, "
                                          "то найди себе новые.\n" +
                                          "В наше время найти какую либо информацию очень легко, " +
                                          "ты можешь учиться с помощью книг, видеоуроков, курсов, " +
                                          "статей в интернете, просто посещая занятия в своём " +
                                          "образовательном учереждении и т.п")

    if support.last_quesion_num == "n4":
        db.set_support(user.id, {"last_quesion_num": "0"})
        rand_smile = random.choice(
            ["┏( ͡❛ ͜ʖ ͡❛)┛", "┌( ಠ‿ಠ)┘", "\( ͡❛ ͜ʖ ͡❛)/", "\(•◡•)/", "( ͡❛ ͜ʖ ͡❛)", "(>‿◠)✌", "ʕ•ᴥ•ʔ", "(◉◡◉)",
             "(◕‿◕)", "( ́ ◕◞ε◟◕`)", "(^ↀᴥↀ^)"])
        bot.send_message(message.chat.id, "Это всё, что я хотел тебе рассказать. " +
                                          "Надеюсь эта информация поможет тебе и ты добьёшься успеха. " +
                                          "Всё зависит лишь от тебя, удачи!" + rand_smile)


@bot.message_handler(func=que_handler)
def quesion(message):
    user = db.find_user(message.from_user.id)
    aim_q = db.choise_aim(user.id, message.text)
    plan_q = db.choise_plan(user.id, message.text)
    rand_smile = random.choice(
        ["┏( ͡❛ ͜ʖ ͡❛)┛", "┌( ಠ‿ಠ)┘", "\( ͡❛ ͜ʖ ͡❛)/", "\(•◡•)/", "( ͡❛ ͜ʖ ͡❛)", "(>‿◠)✌", "ʕ•ᴥ•ʔ", "(◉◡◉)", "(◕‿◕)",
         "( ́ ◕◞ε◟◕`)", "(^ↀᴥↀ^)"])
    support = db.session.query(db.Support).filter(db.Support.user_id == user.id).first()

    pe_markup = types.ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True, selective=True)
    b1 = types.KeyboardButton("Вписать пункт")
    b2 = types.KeyboardButton("Удалить пункт")
    b3 = types.KeyboardButton("Выполнить пункт")
    b4 = types.KeyboardButton("Сделать пункт невыполненным")
    b5 = types.KeyboardButton("Изменить название плана")
    b6 = types.KeyboardButton("Назад")
    pe_markup.add(b1, b2, b3, b4, b5, b6)

    def show_plan():
        plan = db.session.query(db.Plans).filter(db.Plans.id == support.choised_plan_id).first()
        plan_points = db.session.query(db.PlansPoints).filter(db.PlansPoints.plan_id == plan.id).all()
        pp_text = f" ---  {plan.plan_name}  ---\n\n"
        for plan_point in plan_points:
            mark = "✓" if plan_point.completed else ""
            pp_text += f"{plan_point.number}. {plan_point.text} {mark}\n\n"
        db.set_support(user.id, {"last_quesion_id": support.last_quesion_id + 1})
        bot.send_message(message.chat.id, pp_text)

    def pe():
        db.set_support(user.id, {"last_quesion_id": message.message_id + 1, "last_quesion_num": "pe"})
        show_plan()
        bot.send_message(message.chat.id, "Выбери действие:", reply_markup=pe_markup)

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

    if support.last_quesion_num == 'pe':
        if message.text == "Вписать пункт":
            db.set_support(user.id, {"last_quesion_id": message.message_id + 1, "last_quesion_num": "pp1"})
        elif message.text == "Удалить пункт":
            db.set_support(user.id, {"last_quesion_id": message.message_id + 1, "last_quesion_num": "pp3"})
        elif message.text == "Выполнить пункт":
            db.set_support(user.id, {"last_quesion_id": message.message_id + 1, "last_quesion_num": "pp4"})
        elif message.text == "Сделать пункт невыполненным":
            db.set_support(user.id, {"last_quesion_id": message.message_id + 1, "last_quesion_num": "pp5"})
        elif message.text == "Изменить название плана":
            db.set_support(user.id, {"last_quesion_id": message.message_id + 1, "last_quesion_num": "p2_1"})
        else:
            bot.send_message(message.chat.id, "Возвращаюсь назад " + rand_smile)

    if support.last_quesion_num == 'p1':
        if plan_q.first():
            bot.send_message(message.chat.id, "Прости, но планам нельзя давать одинаковые имена")
        else:
            db.add_plan(user.id, message.text)
            plan = plan_q.first()
            bot.send_message(message.chat.id, "План сохранён! " + rand_smile)
            db.set_support(user.id, {"last_quesion_id": message.message_id + 2, "last_quesion_num": "pe",
                                     "choised_plan_id": plan.id})
            show_plan()
            bot.send_message(message.chat.id, "Добавь пункты своему плану:", reply_markup=pe_markup)

    if support.last_quesion_num == 'p2_2':
        plan_q = db.session.query(db.Plans).filter(db.Plans.id == support.choised_plan_id)
        db.edit_plan_name(plan_q, message.text)
        bot.send_message(message.chat.id, "Название плана изменено! " + rand_smile)
        pe()

    if support.last_quesion_num == 'p2_1':
        db.set_support(user.id, {"last_quesion_id": message.message_id + 1, "last_quesion_num": "p2_2"})
        bot.send_message(message.chat.id, "Введи название плана:")

    if support.last_quesion_num == 'p2':
        plan = plan_q.first()
        db.set_support(user.id, {"last_quesion_id": message.message_id + 1, "last_quesion_num": "pe",
                                 "choised_plan_id": plan.id})
        show_plan()
        bot.send_message(message.chat.id, "Выбери действие:", reply_markup=pe_markup)

    if support.last_quesion_num == 'p3':
        db.delete_plan(plan_q)
        bot.send_message(message.chat.id, "План удалён! " + rand_smile)

    if support.last_quesion_num == 'p4':
        db.complete_plan(plan_q)
        bot.send_message(message.chat.id, "План выпонен! " + rand_smile)

    if support.last_quesion_num == 'p5':
        db.uncomplete_plan(plan_q)
        bot.send_message(message.chat.id, "Теперь план не выпонен! " + rand_smile)

    if support.last_quesion_num == 'pp1_2':
        db.add_plan_point(support.choised_plan_id, support.choised_plan_point_num, message.text)
        bot.send_message(message.chat.id, "Пункт добавлен!")
        pe()

    if support.last_quesion_num == 'pp1_1':
        try:
            db.set_support(user.id, {"last_quesion_id": message.message_id + 1, "last_quesion_num": "pp1_2",
                                     "choised_plan_point_num": int(message.text)})
            bot.send_message(message.chat.id, "Введи название пункта:")
        except:
            bot.send_message(message.chat.id, "Невозможный/Неправильный номер пункта!")
            db.set_support(user.id, {"last_quesion_id": support.last_quesion_id + 1})
            pe()

    if support.last_quesion_num == 'pp1':
        db.set_support(user.id, {"last_quesion_id": message.message_id + 1, "last_quesion_num": "pp1_1"})
        bot.send_message(message.chat.id, "Введи будущий номер пункта:")

    if support.last_quesion_num == 'pp3_1':
        try:
            db.delete_plan_point(support.choised_plan_id, int(message.text))
            bot.send_message(message.chat.id, "Пункт удален! " + rand_smile)
            pe()
        except:
            bot.send_message(message.chat.id, "Невозможный/Неправильный номер пункта!")
            db.set_support(user.id, {"last_quesion_id": support.last_quesion_id + 1})
            pe()

    if support.last_quesion_num == 'pp3':
        db.set_support(user.id, {"last_quesion_id": message.message_id + 1, "last_quesion_num": "pp3_1"})
        bot.send_message(message.chat.id, "Введи номер пункта:")

    if support.last_quesion_num == 'pp4_1':
        try:
            db.complete_plan_point(support.choised_plan_id, int(message.text))
            bot.send_message(message.chat.id, "Пункт выпонен! " + rand_smile)
            pe()
        except:
            bot.send_message(message.chat.id, "Невозможный/Неправильный номер пункта!")
            db.set_support(user.id, {"last_quesion_id": support.last_quesion_id + 1})
            pe()

    if support.last_quesion_num == 'pp4':
        db.set_support(user.id, {"last_quesion_id": message.message_id + 1, "last_quesion_num": "pp4_1"})
        bot.send_message(message.chat.id, "Введи номер пункта:")

    if support.last_quesion_num == 'pp5_1':
        try:
            db.uncomplete_plan_point(support.choised_plan_id, int(message.text))
            bot.send_message(message.chat.id, "Теперь пункт теперь не выпонен! " + rand_smile)
            pe()
        except:
            bot.send_message(message.chat.id, "Невозможный/Неправильный номер пункта!")
            db.set_support(user.id, {"last_quesion_id": support.last_quesion_id + 1})
            pe()

    if support.last_quesion_num == 'pp5':
        db.set_support(user.id, {"last_quesion_id": message.message_id + 1, "last_quesion_num": "pp5_1"})
        bot.send_message(message.chat.id, "Введи номер пункта:")


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)  # Starting the bot
