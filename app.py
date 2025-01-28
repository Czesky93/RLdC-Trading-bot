from flask import Flask, render_template, request, redirect, url_for, jsonify
from binance.client import Client
import os

app = Flask(__name__)

# Placeholder na dane użytkowników
USER_KEYS = {}

# Strona główna
@app.route('/')
def home():
    return render_template('index.html')

# Formularz wprowadzania kluczy API
@app.route('/add_keys', methods=['POST'])
def add_keys():
    username = request.form.get('username')
    api_key = request.form.get('api_key')
    api_secret = request.form.get('api_secret')

    if username and api_key and api_secret:
        USER_KEYS[username] = {'api_key': api_key, 'api_secret': api_secret}
        return redirect(url_for('dashboard', username=username))
    
    return redirect(url_for('home'))

# Dashboard użytkownika
@app.route('/dashboard/<username>')
def dashboard(username):
    if username not in USER_KEYS:
        return redirect(url_for('home'))
    
    return render_template('dashboard.html', username=username)

# Pobieranie cen dla użytkownika
@app.route('/analyze/<username>')
def analyze(username):
    if username not in USER_KEYS:
        return jsonify({'error': 'User not found'}), 404

    api_key = USER_KEYS[username]['api_key']
    api_secret = USER_KEYS[username]['api_secret']
    client = Client(api_key, api_secret)

    try:
        prices = client.get_all_tickers()
        return jsonify(prices)
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
