import telepot
import json
import os
import time
from binance_trader import place_order
from gpt_market_analysis import analyze_market_with_gpt
from whale_tracker import track_whale_activity
from pump_dump_detector import detect_pump_and_dump
from demo_trading import simulate_trade

CONFIG_FILE = "config.json"

if not os.path.exists(CONFIG_FILE):
    print("🚨 Brak pliku config.json! Ustaw API do Telegrama.")
    exit(1)

with open(CONFIG_FILE) as config_file:
    config = json.load(config_file)

bot = telepot.Bot(config["telegram_token"])
CHAT_ID = config["telegram_chat_id"]

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
        send_telegram_message("🚀 RLdC Trading Bot aktywowany! Dostępne komendy: /status, /sygnał, /whale, /dump, /ai, /demo")
    elif text == "/status":
        send_telegram_message("✅ RLdC Trading Bot działa!")
    elif text.startswith("/sygnał"):
        pair = text.split(" ")[1] if len(text.split(" ")) > 1 else "BTCUSDT"
        send_telegram_message(f"📈 Pobieranie najnowszego sygnału dla {pair}...")
        response = place_order(pair, amount=0.001)
        send_telegram_message(f"✅ {response}")
    elif text.startswith("/whale"):
        pair = text.split(" ")[1] if len(text.split(" ")) > 1 else "BTCUSDT"
        send_telegram_message(f"🐋 Sprawdzam wielkie transakcje dla {pair}...")
        whales = track_whale_activity(pair)
        send_telegram_message(f"🐳 Wykryte ruchy: {whales}")
    elif text.startswith("/dump"):
        pair = text.split(" ")[1] if len(text.split(" ")) > 1 else "BTCUSDT"
        send_telegram_message(f"🚨 Sprawdzam Pump & Dump dla {pair}...")
        pump_dump_alerts = detect_pump_and_dump(pair)
        send_telegram_message(f"⚠️ Detekcja manipulacji: {pump_dump_alerts}")
    elif text.startswith("/ai"):
        send_telegram_message("🧠 Analiza rynku przy użyciu AI...")
        market_data = "BTC: $42,500, ETH: $3,200, S&P500: 4,150"
        analysis = analyze_market_with_gpt(market_data)
        send_telegram_message(f"📊 GPT-4 Turbo: {analysis}")
    elif text.startswith("/demo"):
        strategy = text.split(" ")[1] if len(text.split(" ")) > 1 else "RSI"
        send_telegram_message(f"🎯 Uruchamiam symulację demo dla strategii {strategy}...")
        result = simulate_trade(strategy, start_balance=1000)
        send_telegram_message(f"📉 Wynik symulacji: {result['final_balance']} USDT")
    else:
        send_telegram_message("❓ Dostępne komendy:\n"
                              "/status - Status bota\n"
                              "/sygnał [PAIR] - Najnowszy sygnał (np. /sygnał ETHUSDT)\n"
                              "/whale [PAIR] - Analiza wielkich transakcji\n"
                              "/dump [PAIR] - Wykrywanie manipulacji\n"
                              "/ai - Analiza AI\n"
                              "/demo [STRATEGIA] - Symulacja demo (np. /demo MACD)")

bot.message_loop(handle_message)

print("✅ Telegram AI Bot działa!")
send_telegram_message("🚀 RLdC Trading Bot aktywowany!")

while True:
    time.sleep(5)
