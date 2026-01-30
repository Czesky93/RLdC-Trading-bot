import json
import os
import subprocess
import sys
import time

from config_manager import DEFAULT_CONFIG, bootstrap_environment, diagnose_and_repair

CONFIG_FILE = "config.json"

# Domyślna konfiguracja


def print_header():
    """Wyświetla nagłówek instalatora"""
    print("\n" + "=" * 60)
    print("🛠️ RLdC Trading Bot - Inteligentny Instalator")
    print("=" * 60 + "\n")


def check_python():
    """Sprawdza wersję Pythona"""
    print("🔍 Sprawdzanie wersji Pythona...")
    python_version = subprocess.check_output(["python3", "--version"]).decode().strip()
    print(f"✅ Wykryta wersja: {python_version}")


def install_packages():
    """Instaluje wymagane pakiety"""
    print("🔄 Instalowanie zależności...")
    packages = [
        "flask",
        "pandas",
        "ta",
        "binance",
        "telepot",
        "tweepy",
        "gym",
        "stable-baselines3",
        "openai",
        "requests",
        "matplotlib",
        "scipy",
        "numpy",
        "opencv-python",
    ]
    # Jeśli nie uruchomiono w virtualenv — przerwij i podaj instrukcję
    if getattr(sys, "base_prefix", None) == getattr(sys, "prefix", None):
        print("⚠️ Wygląda na to, że używasz systemowego Pythona (brak virtualenv).")
        print("💡 Utwórz i aktywuj virtualenv, np.:")
        print("   python3 -m venv .venv")
        print("   source .venv/bin/activate")
        print("   python -m pip install --upgrade pip")
        print("   a następnie uruchom instalator ponownie.")
        raise SystemExit(1)
    completed = subprocess.run(
        [sys.executable, "-m", "pip", "install"] + packages,
        check=False,
        capture_output=True,
    )
    if completed.returncode != 0:
        stderr = completed.stderr.decode(errors="ignore")
        print("❌ Nie udało się zainstalować zależności przy użyciu pip.")
        if "externally-managed-environment" in stderr or "PEP 668" in stderr:
            print(
                "⚠️ Wykryto 'externally-managed-environment' (PEP 668). Użyj virtualenv lub zainstaluj pakiety systemowo przez dystrybucję."
            )
        else:
            print(stderr)
        raise SystemExit(1)
    print("✅ Wszystkie zależności zostały zainstalowane!")


def configure_system():
    """Konfiguruje system na podstawie domyślnych ustawień lub pyta użytkownika o zmiany"""
    print("⚙️ Konfiguracja systemu...")
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
    bootstrap_environment()
    print("✅ Konfiguracja systemu zakończona.")


def verify_installation():
    """Sprawdza poprawność działania wszystkich modułów"""
    print("🔍 Weryfikacja instalacji...")
    modules = [
        "main.py",  # FastAPI Gateway
        "master_ai_trader.py",
        "web_portal.py",
        "ai_optimizer.py",
        "rldc_quantum_ai.py",
        "demo_trading.py",
        "telegram_ai_bot.py",
        "zordon_ai.py",
        "ultimate_ai.py",
    ]
    for module in modules:
        if not os.path.exists(module):
            print(f"⚠️ Brak pliku {module}! Instalacja mogła się nie powieść.")
        else:
            print(f"✅ {module} - OK")


def run_system():
    """Uruchamia kluczowe moduły systemu"""
    print("🚀 Uruchamianie systemu...")
    modules = [
        "master_ai_trader.py",
        "web_portal.py",
        "ai_optimizer.py",
        "rldc_quantum_ai.py",
        "demo_trading.py",
        "telegram_ai_bot.py",
        "zordon_ai.py",
        "ultimate_ai.py",
    ]
    for module in modules:
        print(f"▶️ Uruchamianie {module}...")
        try:
            subprocess.Popen([sys.executable, module])
        except Exception as error:
            repair_status = diagnose_and_repair(error, context=f"start_module:{module}")
            print(repair_status)
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
