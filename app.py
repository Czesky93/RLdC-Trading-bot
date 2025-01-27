from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
import re

# Konfiguracja aplikacji
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')

# Konfiguracja bazy danych
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Model użytkownika
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

# Inicjalizacja bazy danych
with app.app_context():
    db.create_all()

# Walidacja e-maila
def validate_email(email):
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(regex, email)

# Walidacja hasła
def validate_password(password):
    return len(password) >= 6

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    user = User.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        flash("Zalogowano pomyślnie!", "success")
        return redirect(url_for('dashboard'))
    flash("Nieprawidłowe dane logowania", "danger")
    return redirect(url_for('home'))

@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    password = request.form['password']
    if not validate_email(email):
        flash("Nieprawidłowy format e-maila", "warning")
        return redirect(url_for('home'))
    if not validate_password(password):
        flash("Hasło musi mieć co najmniej 6 znaków", "warning")
        return redirect(url_for('home'))
    if User.query.filter_by(email=email).first():
        flash("Użytkownik już istnieje", "warning")
        return redirect(url_for('home'))
    hashed_password = generate_password_hash(password, method='sha256')
    new_user = User(email=email, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    flash("Rejestracja zakończona sukcesem!", "success")
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html', message="Witaj w panelu użytkownika!")

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            flash("Link do resetowania hasła został wysłany.", "info")
        else:
            flash("Nie znaleziono użytkownika.", "danger")
        return redirect(url_for('home'))
    return render_template('reset_password.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

@app.route('/analyze')
def analyze():
    from modules.analysis import analyze_binance_data
    results = analyze_binance_data()
    return render_template('analyze.html', results=results)
