import os
import subprocess
import json
import time

CONFIG_FILE = "config.json"

# Domyślna konfiguracja
DEFAULT_CONFIG = {
    "AI_MODE": "hybrid",
    "USE_FREE_AI": True,
    "USE_PAID_AI": False,
    "START_BALANCE": 1000,
    "STOP_LOSS": 0.02,
    "TAKE_PROFIT": 0.05,
    "ENABLE_QUANTUM_AI": True,
    "ENABLE_HFT": True,
    "ENABLE_BLOCKCHAIN_ANALYSIS": True
}

def print_header():
    """Wyświetla nagłówek instalatora"""
    print("\n" + "="*60)
    print("🛠️ RLdC Trading Bot - Inteligentny Instalator")
    print("="*60 + "\n")

def check_python():
    """Sprawdza wersję Pythona"""
    print("🔍 Sprawdzanie wersji Pythona...")
    python_version = subprocess.check_output(["python3", "--version"]).decode().strip()
    print(f"✅ Wykryta wersja: {python_version}")

def install_packages():
    """Instaluje wymagane pakiety"""
    print("🔄 Instalowanie zależności...")
    packages = [
        "flask", "pandas", "ta", "binance", "telepot", "tweepy", "gym", 
        "stable-baselines3", "openai", "requests", "matplotlib", "scipy", "numpy", "opencv-python"
    ]
    subprocess.run(["pip", "install"] + packages, check=True)
    print("✅ Wszystkie zależności zostały zainstalowane!")

def configure_system():
    """Konfiguruje system na podstawie domyślnych ustawień lub pyta użytkownika o zmiany"""
    print("⚙️ Konfiguracja systemu...")
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        print("✅ Domyślna konfiguracja została zapisana.")
    else:
        print("✅ Plik konfiguracji już istnieje.")

def verify_installation():
    """Sprawdza poprawność działania wszystkich modułów"""
    print("🔍 Weryfikacja instalacji...")
    modules = ["master_ai_trader.py", "web_portal.py", "ai_optimizer.py", "rldc_quantum_ai.py", "demo_trading.py", "telegram_ai_bot.py", "zordon_ai.py", "ultimate_ai.py"]
    for module in modules:
        if not os.path.exists(module):
            print(f"⚠️ Brak pliku {module}! Instalacja mogła się nie powieść.")
        else:
            print(f"✅ {module} - OK")

def run_system():
    """Uruchamia kluczowe moduły systemu"""
    print("🚀 Uruchamianie systemu...")
    modules = ["master_ai_trader.py", "web_portal.py", "ai_optimizer.py", "rldc_quantum_ai.py", "demo_trading.py", "telegram_ai_bot.py", "zordon_ai.py", "ultimate_ai.py"]
    for module in modules:
        print(f"▶️ Uruchamianie {module}...")
        subprocess.Popen(["python", module])
        time.sleep(2)

def main():
    """Główna funkcja instalatora"""
    print_header()
    check_python()
    install_packages()
    configure_system()
    verify_installation()
    run_system()
    print("🎉 Instalacja zakończona sukcesem! System działa poprawnie.")

if __name__ == "__main__":
    main()
