import json
import os

CONFIG_FILE = "config.json"

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
    "OPENAI_API_KEY": ""
}

def load_config():
    """Ładuje konfigurację z pliku lub tworzy domyślną."""
    if not os.path.exists(CONFIG_FILE):
        print("🚨 Brak config.json! Tworzę domyślną konfigurację...")
        save_config(DEFAULT_CONFIG)
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

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
