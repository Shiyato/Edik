from sqlalchemy import create_engine
import telebot
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

bot = telebot.TeleBot(token)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    pass #TODO add user in database

@bot.message_handler(commands=['help', 'h', '?'])
def send_welcome(message):
    pass #TODO help message

@bot.message_handler(commands=['edu', 'e'])
def send_welcome(message):
    pass #TODO choise a educattion block


bot.polling(none_stop=True, interval=0) #Start the bot