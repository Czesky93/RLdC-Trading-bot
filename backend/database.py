import sqlite3
import config

def connect_db():
    return sqlite3.connect(config.DATABASE_PATH)
