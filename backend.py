
from flask import Flask, request, jsonify, render_template
import sqlite3

app = Flask(__name__)
DATABASE = "database.sqlite"

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return "RLdC Trading Bot is running!"

@app.route('/register', methods=['POST'])
def register():
    email = request.form.get("email")
    password = request.form.get("password")
    conn = get_db()
    try:
        conn.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        conn.commit()
        return jsonify({"message": "Rejestracja zakończona sukcesem"}), 200
    except sqlite3.IntegrityError:
        return jsonify({"error": "Użytkownik już istnieje"}), 400
    finally:
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get("email")
    password = request.form.get("password")
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password)).fetchone()
    conn.close()
    if user:
        return jsonify({"message": "Zalogowano pomyślnie"}), 200
    return jsonify({"error": "Nieprawidłowe dane logowania"}), 400

@app.route('/set_binance', methods=['POST'])
def set_binance():
    user_id = request.form.get("user_id")
    api_key = request.form.get("api_key")
    api_secret = request.form.get("api_secret")
    max_amount = request.form.get("max_amount")
    conn = get_db()
    conn.execute(
        "INSERT INTO binance_settings (user_id, api_key, api_secret, max_amount) VALUES (?, ?, ?, ?)",
        (user_id, api_key, api_secret, max_amount)
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "Ustawienia Binance zapisane"}), 200

if __name__ == '__main__':
    app.run(debug=True)
