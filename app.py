
from flask import Flask, request, render_template, jsonify
import os

app = Flask(__name__)

# Home route
@app.route("/")
def home():
    return render_template("index.html")

# Connect Binance API
@app.route("/connect", methods=["POST"])
def connect():
    api_key = request.form.get("api_key")
    secret_key = request.form.get("api_secret")
    if not api_key or not secret_key:
        return jsonify({"status": "error", "message": "API credentials are required"})
    return jsonify({"status": "success", "message": "Connected successfully!"})

# Log Viewer (placeholder)
@app.route("/logs", methods=["GET"])
def logs():
    return jsonify({"status": "success", "logs": ["Log 1", "Log 2", "Log 3"]})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
