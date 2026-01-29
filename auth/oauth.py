import logging
import os

from flask import jsonify, redirect, url_for, session
from authlib.integrations.flask_client import OAuth

oauth = OAuth()
google = None


def init_oauth(app):
    oauth.init_app(app)
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    if not client_id or not client_secret:
        logging.warning(
            "Google OAuth is disabled. Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET."
        )
        return None
    global google
    google = oauth.register(
        name="google",
        client_id=client_id,
        client_secret=client_secret,
        access_token_url="https://accounts.google.com/o/oauth2/token",
        authorize_url="https://accounts.google.com/o/oauth2/auth",
        client_kwargs={"scope": "email profile"},
    )
    return google

def google_login():
    if google is None:
        return jsonify({"error": "Google OAuth is not configured"}), 503
    return google.authorize_redirect(url_for("authorize_google", _external=True))

def authorize():
    if google is None:
        return jsonify({"error": "Google OAuth is not configured"}), 503
    token = google.authorize_access_token()
    if not token:
        return jsonify({"error": "Google OAuth failed"}), 401
    user_info = google.get("https://www.googleapis.com/oauth2/v2/userinfo").json()
    session["user"] = user_info
    return redirect("/")
