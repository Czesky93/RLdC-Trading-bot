import telepot
import json
import os
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

bot = telepot.Bot(config["TELEGRAM_BOT_TOKEN"])
CHAT_ID = config["CHAT_ID"]

def send_telegram_message(message):
    """Wysyła powiadomienie do Telegrama"""
    try:
        bot.sendMessage(CHAT_ID, message)
    except Exception as e:
        print(f"❌ Błąd wysyłania wiadomości: {e}")

def handle_message(msg):
    """Obsługuje wiadomości z Telegrama"""
    chat_id = msg["chat"]["id"]
    text = msg["text"].strip().lower()

    if text == "/status":
        send_telegram_message("✅ RLdC Trading Bot działa!")
    elif text == "/sygnał":
        send_telegram_message("📈 Pobieranie najnowszego sygnału handlowego...")
        place_order("BTCUSDT", amount=0.001)
    elif text == "/whale":
        send_telegram_message("🐋 Sprawdzam wielkie transakcje...")
        whales = track_whale_activity("BTCUSDT")
        send_telegram_message(f"🐳 Wykryte ruchy: {whales}")
    elif text == "/dump":
        send_telegram_message("🚨 Sprawdzam Pump & Dump...")
        pump_dump_alerts = detect_pump_and_dump("BTCUSDT")
        send_telegram_message(f"⚠️ Detekcja manipulacji: {pump_dump_alerts}")
    elif text == "/ai":
        send_telegram_message("🧠 Analiza rynku przy użyciu AI...")
        analysis = analyze_market_with_gpt("BTC: $42,500, ETH: $3,200, S&P500: 4,150")
        send_telegram_message(f"📊 GPT-4 Turbo: {analysis}")
    elif text.startswith("/demo"):
        send_telegram_message("🎯 Uruchamiam symulację demo...")
        result = simulate_trade("RSI", start_balance=1000)
        send_telegram_message(f"📉 Wynik symulacji: {result['final_balance']} USDT")
    else:
        send_telegram_message("❓ Dostępne komendy:
/status - Status bota
/sygnał - Najnowszy sygnał
/whale - Analiza wielkich transakcji
/dump - Wykrywanie manipulacji
/ai - Analiza AI
/demo - Symulacja demo")

bot.message_loop(handle_message)

print("✅ Telegram AI Bot działa!")
send_telegram_message("🚀 RLdC Trading Bot aktywowany!")

import time
while True:
    time.sleep(5)
