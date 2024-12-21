#utils/db_utils
import sqlite3

def init_connection():
    return sqlite3.connect('db/library.db')