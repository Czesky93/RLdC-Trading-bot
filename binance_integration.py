"""
Binance Futures API Integration Module
Integrates real Binance Futures API with the Gateway Server
"""

from binance.client import Client
from binance.exceptions import BinanceAPIException
from typing import Optional, Dict, Any
import os
import logging

logger = logging.getLogger(__name__)


class BinanceFuturesClient:
    """Binance Futures API client wrapper"""
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        """
        Initialize Binance Futures client
        
        Args:
            api_key: Binance API key (defaults to BINANCE_API_KEY env var)
            api_secret: Binance API secret (defaults to BINANCE_API_SECRET env var)
        """
        self.api_key = api_key or os.getenv("BINANCE_API_KEY")
        self.api_secret = api_secret or os.getenv("BINANCE_API_SECRET")
        
        if not self.api_key or not self.api_secret:
            logger.warning("Binance API credentials not provided. Running in demo mode.")
            self.client = None
        else:
            try:
                self.client = Client(self.api_key, self.api_secret)
                # Test connection
                self.client.ping()
                logger.info("Successfully connected to Binance API")
            except BinanceAPIException as e:
                logger.error(f"Failed to connect to Binance API: {e}")
                self.client = None
    
    def get_account_balance(self) -> Dict[str, float]:
        """Get Futures account balance"""
        if not self.client:
            return {"USDT": 10000.0}  # Demo balance
        
        try:
            account = self.client.futures_account_balance()
            balances = {}
            for balance in account:
                if float(balance['balance']) > 0:
                    balances[balance['asset']] = float(balance['balance'])
            return balances
        except BinanceAPIException as e:
            logger.error(f"Error fetching account balance: {e}")
            return {}
    
    def get_current_price(self, symbol: str) -> float:
        """Get current market price for a symbol"""
        if not self.client:
            # Demo prices
            demo_prices = {
                "BTCUSDT": 50000.0,
                "ETHUSDT": 3000.0,
                "BNBUSDT": 400.0,
            }
            return demo_prices.get(symbol, 1000.0)
        
        try:
            ticker = self.client.futures_symbol_ticker(symbol=symbol)
            return float(ticker['price'])
        except BinanceAPIException as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            return 0.0
    
    def get_open_positions(self) -> list:
        """Get all open Futures positions"""
        if not self.client:
            return []  # Demo mode
        
        try:
            positions = self.client.futures_position_information()
            # Filter only positions with non-zero quantity
            open_positions = [
                p for p in positions 
                if float(p['positionAmt']) != 0
            ]
            return open_positions
        except BinanceAPIException as e:
            logger.error(f"Error fetching positions: {e}")
            return []
    
    def place_market_order(
        self, 
        symbol: str, 
        side: str, 
        quantity: float,
        leverage: int = 1
    ) -> Optional[Dict[str, Any]]:
        """
        Place a market order on Binance Futures
        
        Args:
            symbol: Trading pair (e.g., BTCUSDT)
            side: BUY or SELL
            quantity: Order quantity
            leverage: Leverage to use (1-125)
        
        Returns:
            Order response or None if failed
        """
        if not self.client:
            logger.info(f"Demo mode: Would place {side} order for {quantity} {symbol} with {leverage}x leverage")
            return {
                "orderId": "demo_order_123",
                "symbol": symbol,
                "side": side,
                "quantity": quantity,
                "status": "FILLED"
            }
        
        try:
            # Set leverage
            self.client.futures_change_leverage(symbol=symbol, leverage=leverage)
            
            # Place market order
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='MARKET',
                quantity=quantity
            )
            logger.info(f"Order placed: {order}")
            return order
        except BinanceAPIException as e:
            logger.error(f"Error placing order: {e}")
            return None
    
    def set_stop_loss_take_profit(
        self,
        symbol: str,
        side: str,
        quantity: float,
        stop_price: Optional[float] = None,
        take_profit_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Set stop loss and/or take profit for a position
        
        Args:
            symbol: Trading pair
            side: Position side (LONG -> SELL for SL/TP, SHORT -> BUY for SL/TP)
            quantity: Position quantity
            stop_price: Stop loss price
            take_profit_price: Take profit price
        
        Returns:
            Dict with SL and TP order IDs
        """
        if not self.client:
            logger.info(f"Demo mode: Would set SL={stop_price}, TP={take_profit_price}")
            return {"sl_order": "demo_sl", "tp_order": "demo_tp"}
        
        result = {}
        
        try:
            # Determine order side (opposite of position side)
            order_side = "SELL" if side == "LONG" else "BUY"
            
            # Set stop loss
            if stop_price:
                sl_order = self.client.futures_create_order(
                    symbol=symbol,
                    side=order_side,
                    type='STOP_MARKET',
                    quantity=quantity,
                    stopPrice=stop_price
                )
                result['sl_order'] = sl_order['orderId']
            
            # Set take profit
            if take_profit_price:
                tp_order = self.client.futures_create_order(
                    symbol=symbol,
                    side=order_side,
                    type='TAKE_PROFIT_MARKET',
                    quantity=quantity,
                    stopPrice=take_profit_price
                )
                result['tp_order'] = tp_order['orderId']
            
            logger.info(f"SL/TP set: {result}")
            return result
        except BinanceAPIException as e:
            logger.error(f"Error setting SL/TP: {e}")
            return {}
    
    def close_position(
        self,
        symbol: str,
        side: str,
        quantity: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Close a position
        
        Args:
            symbol: Trading pair
            side: Position side (LONG or SHORT)
            quantity: Quantity to close (None = close all)
        
        Returns:
            Order response or None if failed
        """
        if not self.client:
            logger.info(f"Demo mode: Would close {quantity or 'all'} of {symbol} {side} position")
            return {"orderId": "demo_close_123", "status": "FILLED"}
        
        try:
            # Get position info if quantity not specified
            if quantity is None:
                positions = self.get_open_positions()
                for pos in positions:
                    if pos['symbol'] == symbol:
                        quantity = abs(float(pos['positionAmt']))
                        break
                
                if quantity is None or quantity == 0:
                    logger.warning(f"No open position found for {symbol}")
                    return None
            
            # Close order side is opposite of position side
            close_side = "SELL" if side == "LONG" else "BUY"
            
            # Place market order to close
            order = self.client.futures_create_order(
                symbol=symbol,
                side=close_side,
                type='MARKET',
                quantity=quantity,
                reduceOnly=True
            )
            logger.info(f"Position closed: {order}")
            return order
        except BinanceAPIException as e:
            logger.error(f"Error closing position: {e}")
            return None


# Singleton instance
_binance_client: Optional[BinanceFuturesClient] = None


def get_binance_client() -> BinanceFuturesClient:
    """Get or create Binance Futures client singleton"""
    global _binance_client
    if _binance_client is None:
        _binance_client = BinanceFuturesClient()
    return _binance_client


# Usage example
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize client
    client = get_binance_client()
    
    # Get account balance
    balance = client.get_account_balance()
    print(f"Account Balance: {balance}")
    
    # Get current price
    btc_price = client.get_current_price("BTCUSDT")
    print(f"BTC Price: ${btc_price}")
    
    # Get open positions
    positions = client.get_open_positions()
    print(f"Open Positions: {len(positions)}")
    
    # Demo order (won't execute without API keys)
    order = client.place_market_order("BTCUSDT", "BUY", 0.001, leverage=10)
    print(f"Order: {order}")
