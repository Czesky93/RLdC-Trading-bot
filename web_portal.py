from flask import Flask, render_template, request, jsonify
import json
import os
import requests

app = Flask(__name__)

CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    return {}

@app.route("/")
def home():
    config = load_config()
    return render_template("dashboard.html", config=config)

@app.route("/settings", methods=["POST"])
def update_settings():
    new_config = request.json
    with open(CONFIG_FILE, "w") as file:
        json.dump(new_config, file, indent=4)
    return jsonify({"status": "success", "message": "Ustawienia zapisane!"})

@app.route("/market_analysis", methods=["GET"])
def market_analysis():
    response = requests.get("https://api.binance.com/api/v3/ticker/price")
    market_data = response.json()
    return jsonify(market_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
