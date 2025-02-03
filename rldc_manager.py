import os
import subprocess
import json
from flask import Flask, render_template, request, jsonify

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "rldc_manager.log")
CONFIG_FILE = "config.json"

app = Flask(__name__)

def log(message):
    with open(LOG_FILE, "a") as log_file:
        log_file.write(message + "\n")
    print(message)

def install():
    log("🔄 Rozpoczynamy instalację RLdC Trading Bot...")

    subprocess.run(["sudo", "apt", "update", "-y"])
    subprocess.run(["sudo", "apt", "install", "-y", "python3", "python3-venv", "python3-pip", "git"])

    if not os.path.exists("venv"):
        log("🌍 Tworzenie środowiska Python...")
        subprocess.run(["python3", "-m", "venv", "venv"])

    subprocess.run(["venv/bin/pip", "install", "--upgrade", "pip"])
    subprocess.run(["venv/bin/pip", "install", "-r", "requirements.txt"])

    log("✅ Instalacja zakończona!")

def update():
    log("🔄 Aktualizacja RLdC Trading Bot...")

    backup_name = f"backup_{subprocess.getoutput('date +%Y%m%d_%H%M%S')}.tar.gz"
    subprocess.run(["tar", "--exclude=venv", "--exclude=.git", "-czf", backup_name, "."])

    subprocess.run(["git", "pull", "origin", "main"])

    subprocess.run(["rm", "-rf", "venv"])
    subprocess.run(["python3", "-m", "venv", "venv"])
    subprocess.run(["venv/bin/pip", "install", "-r", "requirements.txt"])

    log("✅ Aktualizacja zakończona!")

def repair():
    log("🔄 Naprawa RLdC Trading Bot...")

    if not os.path.exists("venv"):
        install()
    else:
        subprocess.run(["venv/bin/pip", "install", "-r", "requirements.txt"])

    if not os.path.exists(CONFIG_FILE):
        log("🚨 Brak config.json! Tworzenie domyślnego pliku...")
        with open(CONFIG_FILE, "w") as f:
            json.dump({
                "TELEGRAM_BOT_TOKEN": "WPROWADŹ_TWÓJ_BOT_TOKEN",
                "CHAT_ID": "WPROWADŹ_CHAT_ID",
                "BINANCE_API_KEY": "WPROWADŹ_BINANCE_API",
                "BINANCE_API_SECRET": "WPROWADŹ_BINANCE_SECRET"
            }, f, indent=4)

    log("✅ Naprawa zakończona!")

def restart():
    log("🔄 Restartowanie RLdC Trading Bot...")

    subprocess.run(["pkill", "-f", "run_rldc_trading_bot.py"], stderr=subprocess.DEVNULL)
    subprocess.run(["nohup", "venv/bin/python", "run_rldc_trading_bot.py", ">", "bot.log", "2>&1", "&"])

    log("✅ RLdC Trading Bot uruchomiony!")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/install", methods=["POST"])
def install_api():
    install()
    return jsonify({"status": "ok", "message": "Instalacja zakończona!"})

@app.route("/update", methods=["POST"])
def update_api():
    update()
    return jsonify({"status": "ok", "message": "Aktualizacja zakończona!"})

@app.route("/repair", methods=["POST"])
def repair_api():
    repair()
    return jsonify({"status": "ok", "message": "Naprawa zakończona!"})

@app.route("/restart", methods=["POST"])
def restart_api():
    restart()
    return jsonify({"status": "ok", "message": "Bot zrestartowany!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
