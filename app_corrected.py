from flask import Flask, render_template, request, redirect, url_for, jsonify, session, send_file
from binance.client import Client
import os
import pandas as pd
import ta
import csv

app = Flask(__name__)
app.secret_key = 'tajny_klucz'  # Klucz sesji

LOG_DIR = 'logs'
os.makedirs(LOG_DIR, exist_ok=True)  # Upewnij się, że katalog logów istnieje

def log_transaction(username, action, details):
    log_file = os.path.join(LOG_DIR, f'{username}_transactions.csv')
    file_exists = os.path.isfile(log_file)
    with open(log_file, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Akcja', 'Szczegóły', 'Czas'])
        writer.writerow([action, details, pd.Timestamp.now()])

@app.route('/')
def home():
    return render_template('index.html', logo='/static/images/logo.webp')

@app.route('/zaloguj', methods=['POST'])
def login():
    username = request.form.get('username')
api_key = os.environ.get("BINANCE_API_KEY")
api_secret = os.environ.get("BINANCE_API_SECRET")
api_key = os.environ.get("BINANCE_API_KEY")
api_secret = os.environ.get("BINANCE_API_SECRET")

    if username and api_key and api_secret:
        session['username'] = username
        session['api_key'] = api_key
        session['api_secret'] = api_secret
        return redirect(url_for('dashboard'))
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('home'))
    return render_template('dashboard.html', username=session['username'], logo='/static/images/logo.webp')

@app.route('/logi')
def get_logs():
    if 'username' not in session:
        return jsonify({'error': 'Brak sesji użytkownika'}), 403
    log_file = os.path.join(LOG_DIR, f"{session['username']}_transactions.csv")
    if not os.path.isfile(log_file):
        return jsonify({'error': 'Brak logów'}), 404
    return send_file(log_file, as_attachment=True)

@app.route('/grid_trading', methods=['POST'])
def grid_trading():
    data = request.json
    # Dane potrzebne do grid tradingu: symbol, zakres, liczba poziomów, wielkość pozycji
    symbol = data.get('symbol')
    price_range = data.get('price_range', [0, 0])
    levels = data.get('levels', 5)
    quantity = data.get('quantity', 0.01)

    # Generowanie poziomów siatki (Grid Trading)
    lower, upper = price_range
    grid_levels = [(lower + i * (upper - lower) / levels) for i in range(levels + 1)]

    orders = []
    for price in grid_levels:
        # Tworzenie symulacji zleceń kupna/sprzedaży
        action = 'Kup' if price < (upper + lower) / 2 else 'Sprzedaj'
        orders.append({'price': price, 'quantity': quantity, 'action': action})
        log_transaction(session['username'], action, f"{symbol} po cenie {price}")

    return jsonify({'grid_orders': orders})

if __name__ == '__main__':
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
