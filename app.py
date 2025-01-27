
from flask import Flask, request, jsonify, render_template
import os

app = Flask(__name__)

users = {"admin": "password"}  # Simple user storage for testing
logs = []  # Placeholder for logs

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    if username in users:
        return jsonify({"status": "error", "message": "User already exists"})
    users[username] = password
    return jsonify({"status": "success", "message": "User registered successfully"})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    if users.get(username) == password:
        return jsonify({"status": "success", "message": "Login successful"})
    return jsonify({"status": "error", "message": "Invalid credentials"})

@app.route("/connect_binance", methods=["POST"])
def connect_binance():
    data = request.json
    api_key = data.get("api_key")
    api_secret = data.get("api_secret")
    if api_key and api_secret:
        logs.append(f"Binance connected with API Key: {api_key}")
        return jsonify({"status": "success", "message": "Binance connected"})
    return jsonify({"status": "error", "message": "Missing Binance credentials"})

@app.route("/logs", methods=["GET"])
def get_logs():
    return jsonify({"status": "success", "logs": logs})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
