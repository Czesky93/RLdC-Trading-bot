from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Konfiguracja bazy danych SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Model użytkownika
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Inicjalizacja bazy danych
@app.before_first_request
def create_tables():
    db.create_all()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    user = User.query.filter_by(email=email, password=password).first()
    if user:
        return redirect(url_for('dashboard'))
    return "Nieprawidłowe dane logowania", 401

@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    password = request.form['password']
    if User.query.filter_by(email=email).first():
        return "Użytkownik już istnieje", 400
    new_user = User(email=email, password=password)
    db.session.add(new_user)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    return "Panel użytkownika (w przygotowaniu)"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
