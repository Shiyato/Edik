import os

bot_token = os.environ['TOKEN']

try:
    db_url = os.environ['DATABASE_URL']
    db_url = f'postgresql+psycopg2{db_url[8:]}'
except:
    raise ValueError("-- Wrong database URL! --")
