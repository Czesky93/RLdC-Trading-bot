import json
import os

CONFIG_FILE = "config.json"

if not os.path.exists(CONFIG_FILE):
    print("🚨 Brak pliku config.json! Tworzenie domyślnej konfiguracji...")
    default_config = {
        "AI_MODE": "hybrid",  # Opcje: "free", "paid", "hybrid"
        "FREE_AI_MODEL": "gpt4all-model.bin",
        "PAID_AI_MODEL": "gpt-4-turbo",
        "USE_FREE_AI": True,
        "USE_PAID_AI": True
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(default_config, f, indent=4)

with open(CONFIG_FILE) as config_file:
    config = json.load(config_file)

def get_ai_mode():
    """Pobiera aktualne ustawienia AI"""
    return config["AI_MODE"]

def use_free_ai():
    """Czy używać darmowej AI?"""
    return config["USE_FREE_AI"]

def use_paid_ai():
    """Czy używać płatnej AI?"""
    return config["USE_PAID_AI"]

if __name__ == "__main__":
    print(f"🔧 Aktualny tryb AI: {get_ai_mode()}")
    print(f"🆓 Używanie darmowej AI: {use_free_ai()}")
    print(f"💰 Używanie płatnej AI: {use_paid_ai()}")
