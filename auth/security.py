import bcrypt
from flask import Flask, request, jsonify, session
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
    data = request.json
    hashed_password = hash_password(data['password'])
    new_user = User(username=data['username'], email=data['email'], password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully"}), 201

def login_user():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()

    if user and check_password(data['password'], user.password_hash):
        session['user'] = user.username
        return jsonify({"message": "Login successful"})
    else:
        user.failed_attempts += 1
        db.session.commit()
        return jsonify({"error": "Invalid credentials"}), 401
