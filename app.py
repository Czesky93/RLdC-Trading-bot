from flask import Flask, render_template, request, redirect, session
from auth.security import register_user, login_user, db
from auth.oauth import google_login, authorize
from auth.two_fa import generate_2fa, verify_2fa

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/dbname'
app.config['SECRET_KEY'] = 'supersecretkey'

db.init_app(app)

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
    app.run(debug=True)
