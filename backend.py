
from flask import Flask, request, jsonify
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "Welcome to RLdC Trading Bot!"

@app.route("/status", methods=["GET"])
def status():
    return jsonify({"status": "Running", "message": "RLdC Trading Bot is online!"})

if __name__ == "__main__":
    # Heroku requires the app to bind to the $PORT environment variable
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
