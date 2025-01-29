from flask import Flask, redirect, url_for, session
from authlib.integrations.flask_client import OAuth

oauth = OAuth()
google = oauth.register(
    name="google",
    client_id="GOOGLE_CLIENT_ID",
    client_secret="GOOGLE_CLIENT_SECRET",
    access_token_url="https://accounts.google.com/o/oauth2/token",
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    client_kwargs={"scope": "email profile"},
)

def google_login():
    return google.authorize_redirect(url_for("authorize", _external=True))

def authorize():
    token = google.authorize_access_token()
    user_info = google.get("https://www.googleapis.com/oauth2/v2/userinfo").json()
    session["user"] = user_info
    return redirect("/")
