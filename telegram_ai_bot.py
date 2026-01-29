import json
import os
import time
from datetime import datetime, timezone

import requests
import telepot
from binance.client import Client

from auto_trader import run_once
from trading.signal_engine import build_signal

CONFIG_FILE = "config.json"

if not os.path.exists(CONFIG_FILE):
    print("🚨 Brak pliku config.json! Ustaw API do Telegrama.")
    exit(1)

with open(CONFIG_FILE) as config_file:
    config = json.load(config_file)

bot = telepot.Bot(config["TELEGRAM_BOT_TOKEN"])
CHAT_ID = int(config["CHAT_ID"])

auto_trading_enabled = False
last_auto_trade = None

def get_client():
    api_key = config.get("BINANCE_API_KEY")
    api_secret = config.get("BINANCE_API_SECRET")
    if not api_key or not api_secret:
        raise ValueError("Brak BINANCE_API_KEY/BINANCE_API_SECRET w config.json.")
    return Client(api_key, api_secret)

def fetch_price(symbol):
    response = requests.get(
        "https://api.binance.com/api/v3/ticker/price",
        params={"symbol": symbol},
        timeout=10,
    )
    response.raise_for_status()
    return response.json()

def send_telegram_message(message):
    """Wysyła powiadomienie do Telegrama z zapobieganiem spamowi"""
    try:
        bot.sendMessage(CHAT_ID, message)
        time.sleep(1)  # Zabezpieczenie przed spamem
    except Exception as e:
        print(f"❌ Błąd wysyłania wiadomości: {e}")

def handle_message(msg):
    """Obsługuje wiadomości z Telegrama"""
    chat_id = msg["chat"]["id"]
    text = msg["text"].strip().lower()

    if chat_id != CHAT_ID:
        send_telegram_message("🚫 Nie masz uprawnień do sterowania tym botem.")
        return

    if text == "/start":
        send_telegram_message(
            "🚀 RLdC Trading Bot aktywowany!\n"
            "Dostępne komendy:\n"
            "/status - status bota\n"
            "/price [SYMBOL] - kurs z Binance (np. /price BTCUSDT)\n"
            "/signal [SYMBOL] - sygnał z realnych danych (np. /signal ETHUSDT)\n"
            "/rules - pokaż aktywne warunki sygnału\n"
            "/autotrade on|off|status - sterowanie auto-tradingiem\n"
            "/trade once - jednorazowe wykonanie auto-tradera"
        )
    elif text == "/status":
        status = "włączony" if auto_trading_enabled else "wyłączony"
        last_run = last_auto_trade.isoformat() if last_auto_trade else "brak"
        send_telegram_message(f"✅ RLdC Trading Bot działa! Auto-trading: {status}. Ostatnie uruchomienie: {last_run}")
    elif text.startswith("/price"):
        symbol = text.split(" ")[1] if len(text.split(" ")) > 1 else "BTCUSDT"
        try:
            price_data = fetch_price(symbol)
            send_telegram_message(f"💵 {symbol}: {price_data['price']}")
        except Exception as exc:
            send_telegram_message(f"❌ Nie udało się pobrać ceny: {exc}")
    elif text.startswith("/signal"):
        symbol = text.split(" ")[1] if len(text.split(" ")) > 1 else "BTCUSDT"
        try:
            trading_rules = config.get("TRADING_RULES", {})
            signal = build_signal(symbol, trading_rules.get("INTERVAL", "1m"), trading_rules)
            message = (
                f"📈 Sygnał {symbol}\n"
                f"Akcja: {signal.action}\n"
                f"Wynik: {signal.score}\n"
                f"Cena: {signal.last_price}\n"
                f"Powody: {', '.join(signal.reasons) if signal.reasons else 'brak'}\n"
                f"Timestamp: {signal.timestamp}"
            )
            send_telegram_message(message)
        except Exception as exc:
            send_telegram_message(f"❌ Błąd generowania sygnału: {exc}")
    elif text == "/rules":
        rules = json.dumps(config.get("TRADING_RULES", {}), indent=2)
        send_telegram_message(f"⚙️ Aktywne warunki sygnału:\n{rules}")
    elif text.startswith("/autotrade"):
        parts = text.split(" ")
        action = parts[1] if len(parts) > 1 else "status"
        if action == "on":
            auto_trading_enabled = True
            send_telegram_message("✅ Auto-trading włączony.")
        elif action == "off":
            auto_trading_enabled = False
            send_telegram_message("🛑 Auto-trading wyłączony.")
        else:
            status = "włączony" if auto_trading_enabled else "wyłączony"
            send_telegram_message(f"ℹ️ Auto-trading: {status}")
    elif text == "/trade once":
        try:
            client = get_client()
            run_once(client, config)
            last_auto_trade = datetime.now(timezone.utc)
            send_telegram_message("✅ Zlecenia auto-tradera wykonane (lub DRY_RUN).")
        except Exception as exc:
            send_telegram_message(f"❌ Błąd auto-tradera: {exc}")
    else:
        send_telegram_message(
            "❓ Dostępne komendy:\n"
            "/status - status bota\n"
            "/price [SYMBOL] - kurs z Binance\n"
            "/signal [SYMBOL] - sygnał z realnych danych\n"
            "/rules - pokaż aktywne warunki sygnału\n"
            "/autotrade on|off|status - sterowanie auto-tradingiem\n"
            "/trade once - jednorazowe wykonanie auto-tradera"
        )

bot.message_loop(handle_message)

print("✅ Telegram AI Bot działa!")
send_telegram_message("🚀 RLdC Trading Bot aktywowany!")

while True:
    if auto_trading_enabled:
        try:
            client = get_client()
            run_once(client, config)
            last_auto_trade = datetime.now(timezone.utc)
        except Exception as exc:
            send_telegram_message(f"❌ Błąd auto-tradera: {exc}")
    time.sleep(config.get("AUTO_TRADING", {}).get("LOOP_SECONDS", 60))
