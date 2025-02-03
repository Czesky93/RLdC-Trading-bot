import time
import json
import os
from binance_trader import place_order
from ai_automl import optimize_strategy
from deep_rl_trader import TradingEnv
from news_watcher import get_crypto_news, get_twitter_trends, analyze_sentiment
from pump_dump_detector import detect_pump_and_dump
from whale_tracker import track_whale_activity
import telepot

CONFIG_FILE = "config.json"

if not os.path.exists(CONFIG_FILE):
    print("🚨 Brak pliku config.json!")
    exit(1)

with open(CONFIG_FILE) as config_file:
    config = json.load(config_file)

bot = telepot.Bot(config["TELEGRAM_BOT_TOKEN"])
CHAT_ID = config["CHAT_ID"]

def send_telegram_message(message):
    try:
        bot.sendMessage(CHAT_ID, message)
    except Exception as e:
        print(f"❌ Błąd wysyłania wiadomości: {e}")

def run_master_bot():
    """Główna pętla Master AI Trading Bot"""
    while True:
        print("🔄 Optymalizacja strategii...")
        best_config = optimize_strategy()

        print("📡 Monitorowanie Whale Tracking...")
        whales = track_whale_activity("BTCUSDT")

        print("📰 Analiza newsów i Twittera...")
        news = get_crypto_news()
        tweets = get_twitter_trends()
        sentiment = analyze_sentiment(news + tweets)
        send_telegram_message(f"📊 Sentyment rynku: {sentiment}")

        print("🚨 Wykrywanie Pump & Dump...")
        pump_dump_alerts = detect_pump_and_dump("BTCUSDT")

        if sentiment == "Pozytywny" and not pump_dump_alerts:
            print("🚀 AI podejmuje decyzję o handlu...")
            place_order("BTCUSDT", amount=0.001)
            send_telegram_message("✅ AI podjęło decyzję o handlu dla BTCUSDT")

        print("⏳ Oczekiwanie 5 minut...")
        time.sleep(300)

if __name__ == "__main__":
    run_master_bot()
