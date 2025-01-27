
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.secret_key = "super_secret_key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///trading_bot.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Database models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

# Routes
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    logs = Log.query.order_by(Log.timestamp.desc()).all()
    return render_template("dashboard.html", logs=logs)

@app.route("/settings", methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()
        if user:
            flash("User already exists!", "warning")
        else:
            new_user = User(email=email, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash("User registered successfully!", "success")
        return redirect(url_for("settings"))
    return render_template("settings.html")

@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.json
    result = {"status": "success", "recommendation": "buy", "confidence": 0.87}
    return jsonify(result)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
