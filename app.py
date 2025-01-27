
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

users = {}  # Prosta baza danych użytkowników (email -> hasło)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    if email in users and users[email] == password:
        return redirect(url_for('dashboard'))
    return "Nieprawidłowe dane logowania", 401

@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    password = request.form['password']
    if email in users:
        return "Użytkownik już istnieje", 400
    users[email] = password
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    return "Panel użytkownika (w przygotowaniu)"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
