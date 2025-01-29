from flask import Flask, render_template, request, redirect, url_for, jsonify, session, send_file
from binance.client import Client
import os
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF

app = Flask(__name__)
app.secret_key = 'tajny_klucz'  # Klucz sesji

REPORTS_DIR = 'reports'
os.makedirs(REPORTS_DIR, exist_ok=True)  # Upewnij się, że katalog raportów istnieje

def generate_report(username, portfolio_data, strategy_performance):
    report_file = os.path.join(REPORTS_DIR, f'{username}_report.pdf')
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Raport RLdC Trading Bot", ln=True, align='C')

    # Dodanie podsumowania portfela
    pdf.cell(200, 10, txt="Podsumowanie portfela:", ln=True, align='L')
    total_usdt = portfolio_data['total_usdt']
    pdf.cell(200, 10, txt=f"Laczna wartość portfela: {total_usdt} USDT", ln=True, align='L')

    # Dodanie wyników strategii
    pdf.cell(200, 10, txt="Skuteczność strategii:", ln=True, align='L')
    pdf.cell(200, 10, txt=f"RSI/MACD: {strategy_performance['accuracy']}% skuteczności", ln=True, align='L')

    # Zapisanie raportu
    pdf.output(report_file)
    return report_file

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
        return redirect(url_for('dashboard'))
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('home'))
    return render_template('dashboard.html', username=session['username'], logo='/static/images/logo.webp')

@app.route('/generate_report', methods=['GET'])
def report():
    if 'username' not in session:
        return jsonify({'error': 'Brak sesji użytkownika'}), 403

    # Przykładowe dane (powinny pochodzić z analizy portfela)
    portfolio_data = {'total_usdt': 5000.0}
    strategy_performance = {'accuracy': 85.0}

    report_file = generate_report(session['username'], portfolio_data, strategy_performance)
    return send_file(report_file, as_attachment=True)

@app.route('/dynamic_dashboard_data', methods=['GET'])
def dynamic_dashboard_data():
    # Przykładowe dane dla dashboardu
    data = {
        'transactions': [
            {'symbol': 'BTCUSDT', 'action': 'Kup', 'price': 30000, 'quantity': 0.01},
            {'symbol': 'ETHUSDT', 'action': 'Sprzedaj', 'price': 2000, 'quantity': 0.5}
        ],
        'portfolio': {'BTC': 0.1, 'ETH': 2.0, 'USDT': 500}
    }
    return jsonify(data)

if __name__ == '__main__':
    import os
port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port, debug=False)
