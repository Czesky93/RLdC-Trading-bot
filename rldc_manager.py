import json
import os
import subprocess
import time
from datetime import datetime

from flask import Flask, jsonify, render_template, request

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "rldc_manager.log")
CONFIG_FILE = "config.json"

app = Flask(__name__)

def log(message, level="INFO"):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] [{level}] {message}"
    with open(LOG_FILE, "a") as log_file:
        log_file.write(formatted + "\n")
    print(formatted)


def run_command(command, description, check=True, retries=0, retry_delay=2):
    attempts = 0
    while True:
        attempts += 1
        log(f"▶️ {description}: {' '.join(command)} (attempt {attempts})")
        result = subprocess.run(command, capture_output=True, text=True)
        if result.stdout:
            log(result.stdout.strip())
        if result.stderr:
            log(result.stderr.strip(), level="WARN")
        if result.returncode == 0:
            return True, result.stdout
        log(
            f"❌ Command failed ({description}) with exit code {result.returncode}.",
            level="ERROR",
        )
        if attempts > retries:
            if check:
                return False, result.stderr
            return False, result.stderr
        log(f"🔁 Retrying in {retry_delay}s...", level="WARN")
        time.sleep(retry_delay)


def ensure_venv():
    if not os.path.exists("venv"):
        log("🌍 Brak środowiska Python, tworzę nowe...")
        success, _ = run_command(["python3", "-m", "venv", "venv"], "Create venv")
        return success
    pip_path = os.path.join("venv", "bin", "pip")
    if not os.path.exists(pip_path):
        log("⚠️ Brak pip w venv, odtwarzam środowisko...", level="WARN")
        subprocess.run(["rm", "-rf", "venv"])
        success, _ = run_command(["python3", "-m", "venv", "venv"], "Recreate venv")
        return success
    return True


def ensure_requirements():
    if not os.path.exists("requirements.txt"):
        log("🚨 Brak requirements.txt!", level="ERROR")
        return False
    success, _ = run_command(
        ["venv/bin/pip", "install", "--upgrade", "pip"],
        "Upgrade pip",
        retries=1,
    )
    if not success:
        return False
    success, _ = run_command(
        ["venv/bin/pip", "install", "-r", "requirements.txt"],
        "Install requirements",
        retries=1,
    )
    if not success:
        return False
    run_command(["venv/bin/pip", "check"], "Validate dependencies", check=False)
    return True


def ensure_config():
    if os.path.exists(CONFIG_FILE):
        return True
    log("🚨 Brak config.json! Tworzenie domyślnego pliku...", level="WARN")
    with open(CONFIG_FILE, "w") as f:
        json.dump(
            {
                "TELEGRAM_BOT_TOKEN": "WPROWADŹ_TWÓJ_BOT_TOKEN",
                "CHAT_ID": "WPROWADŹ_CHAT_ID",
                "BINANCE_API_KEY": "WPROWADŹ_BINANCE_API",
                "BINANCE_API_SECRET": "WPROWADŹ_BINANCE_SECRET",
            },
            f,
            indent=4,
        )
    return True

def install():
    log("🔄 Rozpoczynamy instalację RLdC Trading Bot...")

    success, _ = run_command(["sudo", "apt", "update", "-y"], "System update", retries=1)
    if not success:
        return False, "Nie udało się zaktualizować pakietów systemu."
    success, _ = run_command(
        ["sudo", "apt", "install", "-y", "python3", "python3-venv", "python3-pip", "git"],
        "Install system dependencies",
        retries=1,
    )
    if not success:
        return False, "Nie udało się zainstalować zależności systemowych."

    if not ensure_venv():
        return False, "Nie udało się utworzyć środowiska Python."
    if not ensure_requirements():
        return False, "Nie udało się zainstalować zależności Python."

    log("✅ Instalacja zakończona!")
    return True, "Instalacja zakończona!"

def update():
    log("🔄 Aktualizacja RLdC Trading Bot...")

    backup_name = f"backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.tar.gz"
    success, _ = run_command(
        ["tar", "--exclude=venv", "--exclude=.git", "-czf", backup_name, "."],
        "Create backup",
    )
    if not success:
        return False, "Nie udało się utworzyć kopii zapasowej."

    success, _ = run_command(["git", "pull", "origin", "main"], "Git pull", retries=1)
    if not success:
        log("⚠️ Próba naprawy repozytorium...", level="WARN")
        run_command(["git", "fetch", "origin"], "Git fetch", check=False)
        fallback_success, _ = run_command(
            ["git", "reset", "--hard", "origin/main"],
            "Git reset hard",
            check=False,
        )
        if not fallback_success:
            return False, "Nie udało się zaktualizować repozytorium."

    subprocess.run(["rm", "-rf", "venv"])
    if not ensure_venv():
        return False, "Nie udało się odtworzyć środowiska Python."
    if not ensure_requirements():
        return False, "Nie udało się zaktualizować zależności."

    log("✅ Aktualizacja zakończona!")
    return True, "Aktualizacja zakończona!"

def repair():
    log("🔄 Naprawa RLdC Trading Bot...")

    if not ensure_venv():
        return False, "Nie udało się naprawić środowiska Python."

    if not ensure_requirements():
        log("⚠️ Instalacja zależności nie powiodła się, ponawiam instalację...", level="WARN")
        if not ensure_requirements():
            return False, "Nie udało się naprawić zależności Python."

    if not ensure_config():
        return False, "Nie udało się utworzyć pliku config.json."

    log("✅ Naprawa zakończona!")
    return True, "Naprawa zakończona!"

def restart():
    log("🔄 Restartowanie RLdC Trading Bot...")

    run_command(
        ["pkill", "-f", "run_rldc_trading_bot.py"],
        "Stop running bot",
        check=False,
    )
    if not os.path.exists("venv/bin/python"):
        return False, "Brak środowiska Python. Uruchom instalację lub naprawę."
    with open("bot.log", "a") as log_file:
        subprocess.Popen(
            ["venv/bin/python", "run_rldc_trading_bot.py"],
            stdout=log_file,
            stderr=log_file,
            start_new_session=True,
        )

    log("✅ RLdC Trading Bot uruchomiony!")
    return True, "Bot zrestartowany!"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/install", methods=["POST"])
def install_api():
    success, message = install()
    status = 200 if success else 500
    return jsonify({"status": "ok" if success else "error", "message": message}), status

@app.route("/update", methods=["POST"])
def update_api():
    success, message = update()
    status = 200 if success else 500
    return jsonify({"status": "ok" if success else "error", "message": message}), status

@app.route("/repair", methods=["POST"])
def repair_api():
    success, message = repair()
    status = 200 if success else 500
    return jsonify({"status": "ok" if success else "error", "message": message}), status

@app.route("/restart", methods=["POST"])
def restart_api():
    success, message = restart()
    status = 200 if success else 500
    return jsonify({"status": "ok" if success else "error", "message": message}), status

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
