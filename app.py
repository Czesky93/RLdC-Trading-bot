import logging
import os

from dotenv import load_dotenv
from flask import Flask, render_template

from auth.oauth import authorize, google_login, init_oauth
from auth.security import db, login_user, register_user
from auth.two_fa import generate_2fa, verify_2fa

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL", "sqlite:///rldc_trading_bot.db"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-only-change-me")

if app.config["SECRET_KEY"] == "dev-only-change-me":
    logging.warning(
        "SECRET_KEY is not set. Use a strong secret in production via .env."
    )

db.init_app(app)
init_oauth(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():
    return register_user()

@app.route("/login", methods=["POST"])
def login():
    return login_user()

@app.route("/login/google")
def login_google():
    return google_login()

@app.route("/authorize")
def authorize_google():
    return authorize()

@app.route("/generate-2fa", methods=["GET"])
def generate_2fa_code():
    return generate_2fa()

@app.route("/verify-2fa", methods=["POST"])
def verify_2fa_code():
    return verify_2fa()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
