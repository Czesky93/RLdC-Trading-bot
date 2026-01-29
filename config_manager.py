import json
import os
from datetime import datetime

CONFIG_FILE = "config.json"
FIRST_RUN_FILE = ".rldc_first_run"
LOG_DIR = "logs"
DIAGNOSTIC_LOG_FILE = os.path.join(LOG_DIR, "diagnostics.log")

DEFAULT_CONFIG = {
    "AI_MODE": "hybrid",  # Opcje: "free", "paid", "hybrid"
    "USE_FREE_AI": True,
    "USE_PAID_AI": True,
    "START_BALANCE": 1000,
    "STOP_LOSS": 0.02,
    "TAKE_PROFIT": 0.05,
    "TELEGRAM_BOT_TOKEN": "",
    "CHAT_ID": "",
    "BINANCE_API_KEY": "",
    "BINANCE_API_SECRET": "",
    "ETHERSCAN_API_KEY": "",
    "ETHEREUM_TRACK_ADDRESS": "",
    "NEWS_API_KEY": "",
    "OPENAI_API_KEY": "",
    "TRADING_RULES": {
        "INTERVAL": "1m",
        "FAST_SMA": 9,
        "SLOW_SMA": 21,
        "RSI_PERIOD": 14,
        "RSI_BUY_MIN": 50,
        "RSI_BUY_MAX": 70,
        "RSI_SELL_MIN": 30,
        "RSI_SELL_MAX": 50,
        "ORDERBOOK_IMBALANCE_BUY": 0.1,
        "ORDERBOOK_IMBALANCE_SELL": -0.1,
        "VOLUME_SPIKE_MULTIPLIER": 1.5,
        "MIN_SIGNAL_SCORE": 2
    },
    "AUTO_TRADING": {
        "SYMBOLS": ["BTCUSDT"],
        "ORDER_SIZE_USDT": 25,
        "MAX_SLIPPAGE_PCT": 0.2,
        "DRY_RUN": True,
        "LOOP_SECONDS": 60
    }
}

def load_config():
    """Ładuje konfigurację z pliku lub tworzy domyślną."""
    if not os.path.exists(CONFIG_FILE):
        print("🚨 Brak config.json! Tworzę domyślną konfigurację...")
        save_config(DEFAULT_CONFIG)
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def bootstrap_environment():
    """Konfiguruje środowisko przy pierwszym uruchomieniu i zwraca konfigurację."""
    config = load_config()
    if not os.path.exists(FIRST_RUN_FILE):
        for directory in (LOG_DIR, "data"):
            os.makedirs(directory, exist_ok=True)
        with open(FIRST_RUN_FILE, "w", encoding="utf-8") as f:
            f.write(f"initialized_at={datetime.utcnow().isoformat()}Z\n")
        print("✅ Pierwsze uruchomienie: środowisko zostało skonfigurowane.")
    return config

def diagnose_and_repair(error, context=""):
    """Diagnozuje błąd i próbuje automatycznie naprawić podstawowe problemy."""
    os.makedirs(LOG_DIR, exist_ok=True)
    timestamp = datetime.utcnow().isoformat() + "Z"
    with open(DIAGNOSTIC_LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write(f"[{timestamp}] context={context} error={error}\n")
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
        return "✅ Naprawiono brakujący config.json."
    config = load_config()
    updated = False
    for key, value in DEFAULT_CONFIG.items():
        if key not in config:
            config[key] = value
            updated = True
    if updated:
        save_config(config)
        return "✅ Uzupełniono brakujące wartości w config.json."
    return "⚠️ Diagnostyka zakończona — brak automatycznych napraw."

def save_config(new_config):
    """Zapisuje konfigurację do pliku."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(new_config, f, indent=4)

def update_config(updates):
    """Aktualizuje konfigurację na podstawie podanych zmian."""
    config = load_config()
    config.update(updates)
    save_config(config)
    return config

def export_config(filename="config_backup.json"):
    """Eksportuje konfigurację do pliku JSON."""
    config = load_config()
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)
    return filename

def import_config(filename):
    """Importuje konfigurację z pliku JSON."""
    if not os.path.exists(filename):
        return "❌ Plik nie istnieje!"
    with open(filename, "r", encoding="utf-8") as f:
        new_config = json.load(f)
    save_config(new_config)
    return "✅ Konfiguracja zaimportowana!"

if __name__ == "__main__":
    print("🔧 Aktualna konfiguracja:")
    print(json.dumps(load_config(), indent=4))
