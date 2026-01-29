import logging

import bcrypt
from flask import request, jsonify, session
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    failed_attempts = db.Column(db.Integer, default=0)

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def register_user():
    data = request.json or {}
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    if not username or not email or not password:
        return jsonify({"error": "Missing username, email, or password"}), 400

    hashed_password = hash_password(password)
    new_user = User(username=username, email=email, password_hash=hashed_password)
    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception:
        logging.exception("Failed to register user")
        db.session.rollback()
        return jsonify({"error": "Registration failed"}), 500
    return jsonify({"message": "User registered successfully"}), 201

def login_user():
    data = request.json or {}
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400

    user = User.query.filter_by(username=username).first()

    if user and check_password(password, user.password_hash):
        session['user'] = user.username
        return jsonify({"message": "Login successful"})
    if user:
        user.failed_attempts += 1
        db.session.commit()
    return jsonify({"error": "Invalid credentials"}), 401
