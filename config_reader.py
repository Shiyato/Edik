import os
token = os.environ['token']

try:
    db_url = os.environ['db_url']
except:
    raise ValueError(" Wrong database URL! ")

