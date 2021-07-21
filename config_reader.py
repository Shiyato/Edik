import os
token = os.environ['token']

try:
    db_url = os.environ['DATABASE_URL']
    db_url = f'{db_url[:8]}+psycopg2{db_url[8:]}'
except:
    raise ValueError(" Wrong database URL! ")