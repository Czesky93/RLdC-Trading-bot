import json
import os
from binance.client import Client

CONFIG_FILE = "config.json"

def load_api_keys():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as config_file:
            config = json.load(config_file)
        api_key = config.get("BINANCE_API_KEY")
        api_secret = config.get("BINANCE_API_SECRET")
    else:
        api_key = os.getenv("BINANCE_API_KEY")
        api_secret = os.getenv("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        raise ValueError("Brak kluczy BINANCE_API_KEY/BINANCE_API_SECRET.")

    return api_key, api_secret

API_KEY, API_SECRET = load_api_keys()
client = Client(API_KEY, API_SECRET)

def place_order(symbol, quantity, order_type="MARKET", price=None, stop_price=None):
    try:
        if order_type == "MARKET":
            order = client.order_market_buy(symbol=symbol, quantity=quantity)
        elif order_type == "LIMIT":
            order = client.order_limit_buy(symbol=symbol, quantity=quantity, price=price)
        elif order_type == "STOP_LIMIT":
            order = client.create_order(
                symbol=symbol,
                side="BUY",
                type="STOP_LOSS_LIMIT",
                quantity=quantity,
                price=price,
                stopPrice=stop_price,
                timeInForce="GTC"
            )
        elif order_type == "OCO":
            order = client.create_oco_order(
                symbol=symbol,
                side="BUY",
                quantity=quantity,
                price=price,
                stopPrice=stop_price,
                stopLimitPrice=stop_price * 0.99,
                stopLimitTimeInForce="GTC"
            )
        else:
            raise ValueError("Invalid order type")
        
        print(order)
        return order
    except Exception as e:
        print(f"Error placing order: {e}")
        return None
