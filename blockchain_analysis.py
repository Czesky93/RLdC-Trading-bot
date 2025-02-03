import requests
import json
import os

CONFIG_FILE = "config.json"

if not os.path.exists(CONFIG_FILE):
    print("🚨 Brak pliku config.json! Ustaw API do analizy blockchain.")
    exit(1)

with open(CONFIG_FILE) as config_file:
    config = json.load(config_file)

ETHERSCAN_API_KEY = config["ETHERSCAN_API_KEY"]
BITCOIN_API_URL = "https://api.blockchain.info/stats"

def get_ethereum_transactions():
    """Pobiera najnowsze transakcje Ethereum"""
    url = f"https://api.etherscan.io/api?module=account&action=txlist&address={config['ETHEREUM_TRACK_ADDRESS']}&sort=desc&apikey={ETHERSCAN_API_KEY}"
    response = requests.get(url)
    transactions = response.json().get("result", [])
    return transactions[:5]

def get_bitcoin_data():
    """Pobiera aktualne statystyki Bitcoina"""
    response = requests.get(BITCOIN_API_URL)
    return response.json()

if __name__ == "__main__":
    eth_transactions = get_ethereum_transactions()
    btc_data = get_bitcoin_data()

    print("🔍 Ostatnie transakcje Ethereum:")
    for tx in eth_transactions:
        print(f"- Hash: {tx['hash']}, Wartość: {int(tx['value']) / 1e18} ETH")

    print("
📊 Statystyki Bitcoina:")
    print(f"🚀 Cena: {btc_data['market_price_usd']} USD")
    print(f"⚡ Transakcje na sekundę: {btc_data['transactions_per_second']}")
