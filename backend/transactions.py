import sqlite3
import config

def init_db():
    conn = sqlite3.connect(config.DATABASE_PATH)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS transactions (
                  id INTEGER PRIMARY KEY, 
                  symbol TEXT, 
                  side TEXT, 
                  quantity REAL, 
                  price REAL, 
                  timestamp TEXT)""")
    conn.commit()
    conn.close()

def add_transaction(symbol, side, quantity, price, timestamp):
    conn = sqlite3.connect(config.DATABASE_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO transactions (symbol, side, quantity, price, timestamp) VALUES (?, ?, ?, ?, ?)",
              (symbol, side, quantity, price, timestamp))
    conn.commit()
    conn.close()
