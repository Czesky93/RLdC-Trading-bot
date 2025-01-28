from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from binance.client import Client
import os
import pandas as pd
import ta

app = Flask(__name__)
app.secret_key = 'tajny_klucz'  # Klucz sesji

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

@app.route('/')
def home():
    return render_template('index.html', logo='/static/images/logo.webp')

@app.route('/zaloguj', methods=['POST'])
def login():
    username = request.form.get('username')
    api_key = request.form.get('api_key')
    api_secret = request.form.get('api_secret')

    if username and api_key and api_secret:
        session['username'] = username
        session['api_key'] = api_key
        session['api_secret'] = api_secret
        client = Client(api_key, api_secret)
        USER_TRANSACTIONS[username] = client.get_account()
        return redirect(url_for('dashboard'))
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('home'))
    return render_template('dashboard.html', username=session['username'], logo='/static/images/logo.webp')

@app.route('/analyze/<pair>')
def analyze(pair):
    if 'api_key' not in session or 'api_secret' not in session:
        return jsonify({'error': 'Brak kluczy API'}), 403
    client = Client(session['api_key'], session['api_secret'])
    data = analyze_market_data(client, pair)
    return jsonify(data.tail(10).to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)
