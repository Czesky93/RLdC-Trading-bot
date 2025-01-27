from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Simple home route
@app.route("/")
def home():
    return "Welcome to RLdC Trading Bot!"

# Status route for checking if the app is running
@app.route("/status", methods=["GET"])
def status():
    return jsonify({"status": "Running", "message": "RLdC Trading Bot is online!"})

# Example route for user registration (placeholder)
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400
    return jsonify({"message": f"User {email} registered successfully!"}), 200

# Example route for Binance API settings
@app.route("/set_binance", methods=["POST"])
def set_binance():
    data = request.get_json()
    api_key = data.get("api_key")
    api_secret = data.get("api_secret")
    max_amount = data.get("max_amount")
    if not api_key or not api_secret or not max_amount:
        return jsonify({"error": "Missing Binance settings"}), 400
    return jsonify({"message": "Binance settings saved successfully!"}), 200

if __name__ == "__main__":
    # Heroku requires the app to bind to the $PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
