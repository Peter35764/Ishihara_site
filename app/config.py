import os

DEBUG = True
SECRET_KEY = os.urandom(32)
IMG_AMOUNT = 10  # 15

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

DATABASE = os.path.join(BASE_DIR, 'db/flask.db')
DB_TABLE_CREATE = os.path.join(BASE_DIR, 'db/table_create.sql')
DB_TABLE_NAME = 'pictures'
DB_EMPTY_ANS_VALUE = -1000

RESOURCES = os.path.join(BASE_DIR, 'resources')
SAVE_DIR = os.path.join(BASE_DIR, 'resources/recolor')
ALLOWED_EXTENSIONS = "png"
