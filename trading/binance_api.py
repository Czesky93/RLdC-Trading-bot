import binance
from binance.client import Client

API_KEY = "your_api_key"
API_SECRET = "your_api_secret"

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
