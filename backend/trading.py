from binance.client import Client
import config

client = Client(config.BINANCE_API_KEY, config.BINANCE_SECRET_KEY)

def execute_trade(symbol, side, quantity):
    order = client.order_market(symbol=symbol, side=side, quantity=quantity)
    return order
