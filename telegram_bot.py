import time
import telepot
import json

with open("config.json") as config_file:
    config = json.load(config_file)

bot = telepot.Bot(config["TELEGRAM_BOT_TOKEN"])

def send_telegram_message(message):
    bot.sendMessage(config["TELEGRAM_CHAT_ID"], message)

while True:
    send_telegram_message("📢 RLdC Trading Bot działa!")
    time.sleep(300)
