def analysis_function():
    print('analysis module function executed')

import requests

def analyze_binance_data():
    url = "https://api.binance.com/api/v3/ticker/24hr"
    response = requests.get(url)
    data = response.json()

    profitable_pairs = []
    for item in data:
        price_change = float(item['priceChangePercent'])
        volume = float(item['volume'])
        symbol = item['symbol']

        if price_change > 5 and volume > 1000:
            profitable_pairs.append({
                'symbol': symbol,
                'price_change': price_change,
                'volume': volume
            })

    profitable_pairs.sort(key=lambda x: x['price_change'], reverse=True)
    return profitable_pairs
