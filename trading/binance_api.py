import binance
from binance.client import Client

API_KEY = "your_api_key"
API_SECRET = "your_api_secret"

client = Client(API_KEY, API_SECRET)

def place_order(symbol, quantity, order_type="MARKET"):
    try:
        if order_type == "MARKET":
            order = client.order_market_buy(symbol=symbol, quantity=quantity)
        elif order_type == "LIMIT":
            order = client.order_limit_buy(symbol=symbol, quantity=quantity, price="your_price")
        print(order)
        return order
    except Exception as e:
        print(f"Error placing order: {e}")
        return None
