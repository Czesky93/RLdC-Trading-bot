
# RLdC Trading Bot - Moduł analizy rynku
# Wykonane poprawki:
# - Optymalizacja pobierania danych z Binance API
# - Dodanie obsługi różnych interwałów czasowych
# - Zmiany w zarządzaniu sesją użytkownika
# Planowane:
# - Rozbudowa wskaźników technicznych
# - Integracja z zewnętrznymi danymi rynkowymi
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pandas as pd
from binance.client import Client

app = Flask(__name__)
app.secret_key = 'tajny_klucz'

def get_candlestick_data(client, symbol, interval='1h', limit=100):
    klines = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    data = pd.DataFrame(klines, columns=[
        'open_time', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ])
    data['close'] = data['close'].astype(float)
    return data

@app.route('/indicators/<symbol>')
def indicators(symbol):
    if 'api_key' not in session or 'api_secret' not in session:
        return jsonify({'error': 'Brak kluczy API'}), 403

    client = Client(session['api_key'], session['api_secret'])
    data = get_candlestick_data(client, symbol)

    # Obliczanie wskaźników technicznych

    return jsonify(data.tail(50).to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=True)

def generate_signals(data):
    # Generowanie prostych sygnałów kupna/sprzedaży na podstawie Bollinger Bands
    signals = []
    for i in range(1, len(data)):
        if data['close'].iloc[i] > data['upper_band'].iloc[i]:  # Cena > górny Bollinger Band
            signals.append({'signal': 'Sell', 'price': data['close'].iloc[i], 'index': i})
        elif data['close'].iloc[i] < data['lower_band'].iloc[i]:  # Cena < dolny Bollinger Band
            signals.append({'signal': 'Buy', 'price': data['close'].iloc[i], 'index': i})
    return signals

@app.route('/indicators_with_signals/<symbol>')
def indicators_with_signals(symbol):
    if 'api_key' not in session or 'api_secret' not in session:
        return jsonify({'error': 'Brak kluczy API'}), 403

    client = Client(session['api_key'], session['api_secret'])
    data = get_candlestick_data(client, symbol)

    # Obliczanie wskaźników technicznych
    data = calculate_ichimoku(data)
    data = calculate_bollinger_bands(data)
    data = calculate_vwap(data)

    # Generowanie sygnałów
    signals = generate_signals(data)
    return jsonify({
        'data': data.tail(50).to_dict(orient='records'),
        'signals': signals
    })

if __name__ == '__main__':
    app.run(debug=True)
