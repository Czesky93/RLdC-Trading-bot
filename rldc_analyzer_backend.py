
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, send_file
from binance.client import Client
import os
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import ta

app = Flask(__name__)
app.secret_key = 'tajny_klucz'  # Klucz sesji

LOG_DIR = 'logs'
os.makedirs(LOG_DIR, exist_ok=True)

# Połączenie z Binance API
def get_binance_client():
    if 'api_key' not in session or 'api_secret' not in session:
        return None
    return Client(session['api_key'], session['api_secret'])

# Pobieranie danych świecowych
def get_candlestick_data(symbol, interval='1h', limit=100):
    client = get_binance_client()
    if not client:
        return None
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    data = pd.DataFrame(klines, columns=[
        'open_time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    data['close'] = data['close'].astype(float)
    return data

# Obliczanie wskaźników technicznych
def calculate_indicators(data):
    data['ichimoku_base'] = ta.trend.ichimoku_base_line(data['high'], data['low'])
    data['upper_band'], data['middle_band'], data['lower_band'] = ta.volatility.bollinger_hband(data['close']), ta.volatility.bollinger_mavg(data['close']), ta.volatility.bollinger_lband(data['close'])
    data['vwap'] = ta.volume.volume_weighted_average_price(data['high'], data['low'], data['close'], data['volume'])
    return data

# Generowanie sygnałów kupna/sprzedaży
def generate_signals(data):
    signals = []
    for i in range(1, len(data)):
        if data['close'].iloc[i] > data['upper_band'].iloc[i]:  # Cena > górny Bollinger Band
            signals.append({'signal': 'Sell', 'price': data['close'].iloc[i]})
        elif data['close'].iloc[i] < data['lower_band'].iloc[i]:  # Cena < dolny Bollinger Band
            signals.append({'signal': 'Buy', 'price': data['close'].iloc[i]})
    return signals

@app.route('/')
def home():
    return render_template('dashboard_merged.html', logo='/static/images/logo.webp')

@app.route('/zaloguj', methods=['POST'])
def login():
    username = request.form.get('username')
    api_key = request.form.get('api_key')
    api_secret = request.form.get('api_secret')

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
    return render_template('dashboard_merged.html', username=session['username'], logo='/static/images/logo.webp')

@app.route('/indicators_with_signals/<symbol>')
def indicators_with_signals(symbol):
    if 'api_key' not in session or 'api_secret' not in session:
        return jsonify({'error': 'Brak kluczy API'}), 403

    data = get_candlestick_data(symbol)
    if data is None:
        return jsonify({'error': 'Błąd pobierania danych'}), 500

    data = calculate_indicators(data)
    signals = generate_signals(data)
    return jsonify({'data': data.tail(50).to_dict(orient='records'), 'signals': signals})

if __name__ == '__main__':
    app.run(debug=True)
