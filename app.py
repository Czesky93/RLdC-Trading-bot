from flask import Flask, render_template, request, redirect, url_for, jsonify
from binance.client import Client
import os
import pandas as pd
import ta

app = Flask(__name__)

# Placeholder na dane użytkowników
USER_KEYS = {}

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

def analyze_all_pairs(client, interval='1m', limit=100):
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
    return best_pairs[:10]

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
        return redirect(url_for('dashboard', username=username))
    return redirect(url_for('home'))

@app.route('/dashboard/<username>')
def dashboard(username):
    if username not in USER_KEYS:
        return redirect(url_for('home'))
    return render_template('dashboard.html', username=username)

@app.route('/best_pairs/<username>')
def best_pairs(username):
    if username not in USER_KEYS:
        return jsonify({'error': 'User not found'}), 404

    api_key = USER_KEYS[username]['api_key']
    api_secret = USER_KEYS[username]['api_secret']
    client = Client(api_key, api_secret)
    try:
        best_pairs = analyze_all_pairs(client)
        return jsonify(best_pairs)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/analyze/<username>', methods=['POST'])
def analyze(username):
    if username not in USER_KEYS:
        return jsonify({'error': 'User not found'}), 404

    api_key = USER_KEYS[username]['api_key']
    api_secret = USER_KEYS[username]['api_secret']
    client = Client(api_key, api_secret)
    try:
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
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
