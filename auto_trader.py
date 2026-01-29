import json
import os
import time
from decimal import Decimal, ROUND_DOWN

from binance.client import Client
from binance.exceptions import BinanceAPIException

from trading.signal_engine import build_signal
from trading.strategy_engine import RiskConfig, build_trade_plan

CONFIG_FILE = "config.json"


def load_config():
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError("Brak pliku config.json. Uruchom config_manager.py i uzupełnij dane.")
    with open(CONFIG_FILE, "r", encoding="utf-8") as config_file:
        return json.load(config_file)


def get_client(config):
    api_key = config.get("BINANCE_API_KEY")
    api_secret = config.get("BINANCE_API_SECRET")
    if not api_key or not api_secret:
        raise ValueError("Brak BINANCE_API_KEY/BINANCE_API_SECRET w config.json.")
    return Client(api_key, api_secret)


def get_symbol_filters(client, symbol):
    info = client.get_symbol_info(symbol)
    if not info:
        raise ValueError(f"Nie znaleziono informacji o symbolu {symbol}.")
    lot_size = next((f for f in info["filters"] if f["filterType"] == "LOT_SIZE"), None)
    if not lot_size:
        raise ValueError(f"Brak filtra LOT_SIZE dla {symbol}.")
    return Decimal(lot_size["stepSize"]), Decimal(lot_size["minQty"])


def quantize_qty(quantity, step_size):
    return quantity.quantize(step_size, rounding=ROUND_DOWN)


def get_last_price(client, symbol):
    ticker = client.get_symbol_ticker(symbol=symbol)
    return Decimal(ticker["price"])


def get_available_quote_balance(client, quote_asset):
    balance = client.get_asset_balance(asset=quote_asset)
    if not balance:
        return Decimal("0")
    return Decimal(balance["free"])


def place_order(client, symbol, side, quantity, dry_run):
    if dry_run:
        return {"dry_run": True, "symbol": symbol, "side": side, "quantity": str(quantity)}
    if side == "BUY":
        return client.order_market_buy(symbol=symbol, quantity=str(quantity))
    if side == "SELL":
        return client.order_market_sell(symbol=symbol, quantity=str(quantity))
    raise ValueError("Nieobsługiwany typ zlecenia.")


def run_once(client, config):
    trading_rules = config.get("TRADING_RULES", {})
    auto_trading = config.get("AUTO_TRADING", {})
    risk_cfg = config.get("RISK_MANAGEMENT", {})

    symbols = auto_trading.get("SYMBOLS", [])
    order_size_usdt = Decimal(str(auto_trading.get("ORDER_SIZE_USDT", 0)))
    max_slippage_pct = Decimal(str(auto_trading.get("MAX_SLIPPAGE_PCT", 0)))
    dry_run = bool(auto_trading.get("DRY_RUN", True))
    use_trade_plan = bool(auto_trading.get("USE_TRADE_PLAN", False))

    if not symbols:
        raise ValueError("AUTO_TRADING.SYMBOLS jest puste.")

    risk = RiskConfig(
        risk_per_trade_pct=Decimal(str(risk_cfg.get("RISK_PER_TRADE_PCT", 1))),
        max_position_pct=Decimal(str(risk_cfg.get("MAX_POSITION_PCT", 10))),
        atr_period=int(risk_cfg.get("ATR_PERIOD", 14)),
        atr_multiplier_sl=Decimal(str(risk_cfg.get("ATR_MULTIPLIER_SL", 1.5))),
        atr_multiplier_tp=Decimal(str(risk_cfg.get("ATR_MULTIPLIER_TP", 3.0))),
        min_signal_score=int(risk_cfg.get("MIN_SIGNAL_SCORE", 2)),
    )

    for symbol in symbols:
        signal = build_signal(symbol, trading_rules.get("INTERVAL", "1m"), trading_rules)
        plan = None
        quote_asset = symbol[-4:] if symbol.endswith("USDT") else symbol[-3:]
        available_quote = get_available_quote_balance(client, quote_asset)
        if use_trade_plan:
            plan = build_trade_plan(
                symbol,
                trading_rules.get("INTERVAL", "1m"),
                trading_rules,
                risk,
                available_quote,
            )
            print(
                f"[{symbol}] plan={plan.action} score={plan.score} order_usdt={plan.order_size_usdt} "
                f"sl={plan.stop_loss} tp={plan.take_profit} reasons={plan.reasons}"
            )
        else:
            print(
                f"[{symbol}] action={signal.action} score={signal.score} price={signal.last_price} reasons={signal.reasons}"
            )

        action = plan.action if plan else signal.action
        if action == "HOLD":
            continue

        step_size, min_qty = get_symbol_filters(client, symbol)
        last_price = get_last_price(client, symbol)

        if action == "BUY":
            if plan and plan.order_size_usdt > 0:
                effective_order_size = plan.order_size_usdt
            else:
                effective_order_size = order_size_usdt
            if effective_order_size <= 0:
                raise ValueError("AUTO_TRADING.ORDER_SIZE_USDT musi być > 0.")
            if available_quote < effective_order_size:
                print(f"[{symbol}] Brak wystarczających środków: {available_quote} {quote_asset}")
                continue

            slippage_price = last_price * (Decimal("1") + max_slippage_pct / Decimal("100"))
            quantity = effective_order_size / slippage_price
            quantity = quantize_qty(quantity, step_size)

            if quantity < min_qty:
                print(f"[{symbol}] Ilość poniżej minQty: {quantity} < {min_qty}")
                continue

            result = place_order(client, symbol, "BUY", quantity, dry_run)
            print(f"[{symbol}] BUY: {result}")

        elif action == "SELL":
            base_asset = symbol.replace(quote_asset, "")
            balance = client.get_asset_balance(asset=base_asset)
            available_base = Decimal(balance["free"]) if balance else Decimal("0")
            quantity = quantize_qty(available_base, step_size)

            if quantity < min_qty:
                print(f"[{symbol}] Brak wolumenu do sprzedaży: {quantity} < {min_qty}")
                continue

            result = place_order(client, symbol, "SELL", quantity, dry_run)
            print(f"[{symbol}] SELL: {result}")


def main():
    config = load_config()
    client = get_client(config)
    loop_seconds = int(config.get("AUTO_TRADING", {}).get("LOOP_SECONDS", 60))

    while True:
        try:
            run_once(client, config)
        except BinanceAPIException as exc:
            print(f"Błąd Binance API: {exc}")
        except Exception as exc:
            print(f"Błąd: {exc}")
        time.sleep(loop_seconds)


if __name__ == "__main__":
    main()
