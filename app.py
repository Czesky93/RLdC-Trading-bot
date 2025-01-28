from flask import Flask, render_template, request, redirect, url_for, jsonify
from binance.client import Client
import os
import pandas as pd
import ta
import threading
import time

app = Flask(__name__)

USER_KEYS = {}
BEST_PAIRS_CACHE = []
USER_TRANSACTIONS = {}

def analyze_market_data(client, pair, interval='1m', limit=100):
    klines = client.get_klines(symbol=pair, interval=interval, limit=limit)
    data = pd.DataFrame(klines, columns=[
        'open_time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    data['close'] = data['close'].astype(float)
    data['RSI'] = ta.momentum.rsi(data['close'], window=14)
    return data[['close_time', 'close', 'RSI']]

def fetch_best_pairs(client, interval='1m', limit=100):
    global BEST_PAIRS_CACHE
    all_tickers = client.get_ticker()
    best_pairs = []

    for ticker in all_tickers:
        pair = ticker['symbol']
        try:
            data = analyze_market_data(client, pair, interval, limit)
            latest = data.iloc[-1]
            rsi = latest['RSI']
            if rsi < 30:
                best_pairs.append({'pair': pair, 'rsi': rsi, 'signal': 'buy'})
            elif rsi > 70:
                best_pairs.append({'pair': pair, 'rsi': rsi, 'signal': 'sell'})
        except Exception:
            continue

    best_pairs.sort(key=lambda x: x['rsi'])
    BEST_PAIRS_CACHE = best_pairs[:10]

def fetch_user_transactions(client, username):
    USER_TRANSACTIONS[username] = client.get_account()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/add_keys', methods=['POST'])
def add_keys():
    username = request.form.get('username')
    api_key = request.form.get('api_key')
    api_secret = request.form.get('api_secret')

    if username and api_key and api_secret:
        USER_KEYS[username] = {'api_key': api_key, 'api_secret': api_secret}
        client = Client(api_key, api_secret)
        fetch_user_transactions(client, username)  # Pobieranie historii transakcji
        return redirect(url_for('dashboard', username=username))
    return redirect(url_for('home'))

@app.route('/dashboard/<username>')
def dashboard(username):
    if username not in USER_KEYS:
        return redirect(url_for('home'))
    return render_template('dashboard.html', username=username, logo='/static/images/logo.webp')

@app.route('/best_pairs/<username>')
def best_pairs(username):
    if username not in USER_KEYS:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(BEST_PAIRS_CACHE)

@app.route('/transactions/<username>')
def transactions(username):
    if username not in USER_TRANSACTIONS:
        return jsonify({'error': 'No transactions found'})
    return jsonify(USER_TRANSACTIONS[username])

@app.route('/analyze/<username>', methods=['POST'])
def analyze(username):
    if username not in USER_KEYS:
        return jsonify({'error': 'User not found'}), 404

    api_key = USER_KEYS[username]['api_key']
    api_secret = USER_KEYS[username]['api_secret']
    client = Client(api_key, api_secret)
    data = request.get_json()
    pairs = data.get('pairs', [])
    results = []

    for pair in pairs:
        market_data = analyze_market_data(client, pair)
        latest = market_data.iloc[-1]
        results.append({
            'pair': pair,
            'close_time': str(latest['close_time']),
            'close': latest['close'],
            'signal': 'buy' if latest['RSI'] < 30 else 'sell' if latest['RSI'] > 70 else 'hold'
        })
    return jsonify(results)

if __name__ == '__main__':
    def update_best_pairs():
        while True:
            for user in USER_KEYS.values():
                client = Client(user['api_key'], user['api_secret'])
                fetch_best_pairs(client)
                fetch_user_transactions(client, user)  # Pobieranie transakcji uÅ¼ytkownika
            time.sleep(60)

    threading.Thread(target=update_best_pairs, daemon=True).start()

    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
