"""
FastAPI Gateway Server for RLdC Trading Bot
Provides REST API and WebSocket endpoints for trading bot management
"""

import asyncio
import json
import os
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sqlite3
from contextlib import contextmanager


# Database configuration
DB_FILE = "trading_bot.db"

# In-memory state
bot_state = {
    "status": "stopped",
    "started_at": None,
    "last_update": None,
}

positions_store = []
trades_history = []
equity_data = {}
websocket_clients = []


# Pydantic models
class ClosePositionRequest(BaseModel):
    percent: float


class ModifyPositionRequest(BaseModel):
    sl: Optional[float] = None
    tp: Optional[float] = None


class ConfigUpdateRequest(BaseModel):
    config: Dict[str, Any]


class QuickTradeRequest(BaseModel):
    symbol: str
    side: str  # "LONG" or "SHORT"
    amount: float
    leverage: int
    sl_percent: float
    tp_percent: float


# Database helper
@contextmanager
def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db():
    """Initialize SQLite database"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Positions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                amount REAL NOT NULL,
                entry_price REAL NOT NULL,
                current_price REAL,
                leverage INTEGER NOT NULL,
                sl REAL,
                tp REAL,
                pnl REAL DEFAULT 0,
                pnl_percent REAL DEFAULT 0,
                status TEXT DEFAULT 'open',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Trades history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                side TEXT NOT NULL,
                amount REAL NOT NULL,
                entry_price REAL NOT NULL,
                exit_price REAL NOT NULL,
                leverage INTEGER NOT NULL,
                pnl REAL NOT NULL,
                pnl_percent REAL NOT NULL,
                closed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Equity history table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS equity_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                equity REAL NOT NULL,
                balance REAL NOT NULL,
                unrealized_pnl REAL DEFAULT 0
            )
        """)


# Binance Futures API integration (mock for now, can be replaced with real API)
class BinanceFuturesClient:
    """Mock Binance Futures client - replace with real implementation"""
    
    def __init__(self):
        self.api_key = os.getenv("BINANCE_API_KEY", "")
        self.api_secret = os.getenv("BINANCE_API_SECRET", "")
        
    async def get_price(self, symbol: str) -> float:
        """Get current price for a symbol"""
        # Mock implementation - replace with real Binance API call
        # For now, return mock prices
        mock_prices = {
            "BTC/USDT": 43500.0,
            "ETH/USDT": 2300.0,
            "BTCUSDT": 43500.0,
            "ETHUSDT": 2300.0,
        }
        return mock_prices.get(symbol, 40000.0)
    
    async def get_account_balance(self) -> dict:
        """Get account balance"""
        # Mock implementation
        return {
            "total_balance": 10000.0,
            "available_balance": 8000.0,
            "unrealized_pnl": 200.0
        }
    
    async def place_order(self, symbol: str, side: str, amount: float, leverage: int, sl: float = None, tp: float = None):
        """Place a futures order"""
        # Mock implementation
        entry_price = await self.get_price(symbol)
        return {
            "symbol": symbol,
            "side": side,
            "amount": amount,
            "entry_price": entry_price,
            "leverage": leverage,
            "sl": sl,
            "tp": tp,
            "status": "filled"
        }


binance_client = BinanceFuturesClient()


# Background task to simulate market data updates
async def market_data_updater():
    """Background task to update market data and broadcast to WebSocket clients"""
    while True:
        await asyncio.sleep(5)  # Update every 5 seconds
        
        if websocket_clients:
            # Get current positions and update prices
            positions = get_positions_from_db()
            
            for position in positions:
                current_price = await binance_client.get_price(position["symbol"])
                
                # Broadcast price update
                await broadcast_to_websockets({
                    "type": "price_update",
                    "symbol": position["symbol"],
                    "price": current_price,
                    "timestamp": datetime.now().isoformat()
                })


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler"""
    # Startup
    init_db()
    
    # Start background task for market data updates
    task = asyncio.create_task(market_data_updater())
    
    print("✅ RLdC Trading Bot API started successfully")
    print("📡 WebSocket endpoint available at: ws://0.0.0.0:8000/ws")
    print("📊 API documentation available at: http://0.0.0.0:8000/docs")
    
    yield
    
    # Shutdown
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


# Initialize FastAPI app with lifespan
app = FastAPI(title="RLdC Trading Bot API", version="1.0.0", lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Helper functions
async def broadcast_to_websockets(message: dict):
    """Broadcast message to all connected WebSocket clients"""
    disconnected = []
    for client in websocket_clients:
        try:
            await client.send_json(message)
        except:
            disconnected.append(client)
    
    # Remove disconnected clients
    for client in disconnected:
        if client in websocket_clients:
            websocket_clients.remove(client)


def get_positions_from_db() -> List[dict]:
    """Get all open positions from database"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, symbol, side, amount, entry_price, current_price, 
                   leverage, sl, tp, pnl, pnl_percent, status, 
                   created_at, updated_at
            FROM positions 
            WHERE status = 'open'
            ORDER BY created_at DESC
        """)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_trades_history_from_db(limit: int = 100) -> List[dict]:
    """Get trades history from database"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, symbol, side, amount, entry_price, exit_price, 
                   leverage, pnl, pnl_percent, closed_at
            FROM trades_history 
            ORDER BY closed_at DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_equity_data_from_db(range_str: str) -> List[dict]:
    """Get equity data for specified time range"""
    # Calculate time range
    now = datetime.now()
    if range_str == "1H":
        start_time = now - timedelta(hours=1)
    elif range_str == "4H":
        start_time = now - timedelta(hours=4)
    elif range_str == "1D":
        start_time = now - timedelta(days=1)
    elif range_str == "1W":
        start_time = now - timedelta(weeks=1)
    elif range_str == "1M":
        start_time = now - timedelta(days=30)
    else:
        start_time = now - timedelta(days=1)
    
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT timestamp, equity, balance, unrealized_pnl
            FROM equity_history 
            WHERE timestamp >= ?
            ORDER BY timestamp ASC
        """, (start_time.isoformat(),))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


# API Endpoints

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "RLdC Trading Bot API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/status")
async def get_status():
    """Get bot status"""
    balance = await binance_client.get_account_balance()
    positions = get_positions_from_db()
    
    return {
        "status": bot_state["status"],
        "started_at": bot_state["started_at"],
        "last_update": datetime.now().isoformat(),
        "balance": balance["total_balance"],
        "available_balance": balance["available_balance"],
        "unrealized_pnl": balance["unrealized_pnl"],
        "open_positions": len(positions),
        "total_positions": len(positions)
    }


@app.get("/positions")
async def get_positions():
    """Get all open positions"""
    positions = get_positions_from_db()
    
    # Update current prices
    for position in positions:
        current_price = await binance_client.get_price(position["symbol"])
        position["current_price"] = current_price
        
        # Calculate PnL
        entry_price = position["entry_price"]
        if position["side"].upper() in ["LONG", "BUY"]:
            pnl_percent = ((current_price - entry_price) / entry_price) * 100 * position["leverage"]
        else:
            pnl_percent = ((entry_price - current_price) / entry_price) * 100 * position["leverage"]
        
        position["pnl_percent"] = round(pnl_percent, 2)
        position["pnl"] = round((position["amount"] * entry_price) * (pnl_percent / 100), 2)
    
    return {
        "positions": positions,
        "total": len(positions)
    }


@app.post("/positions/{position_id}/close")
async def close_position(position_id: int, request: ClosePositionRequest):
    """Close a position (partially or fully)"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Get position
        cursor.execute("SELECT * FROM positions WHERE id = ? AND status = 'open'", (position_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Position not found")
        
        position = dict(row)
        
        # Get current price
        current_price = await binance_client.get_price(position["symbol"])
        
        # Calculate PnL
        entry_price = position["entry_price"]
        close_amount = position["amount"] * (request.percent / 100)
        
        if position["side"].upper() in ["LONG", "BUY"]:
            pnl_percent = ((current_price - entry_price) / entry_price) * 100 * position["leverage"]
        else:
            pnl_percent = ((entry_price - current_price) / entry_price) * 100 * position["leverage"]
        
        pnl = (close_amount * entry_price) * (pnl_percent / 100)
        
        if request.percent >= 100:
            # Close entire position
            cursor.execute("""
                UPDATE positions 
                SET status = 'closed', updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (position_id,))
            
            # Add to trades history
            cursor.execute("""
                INSERT INTO trades_history 
                (symbol, side, amount, entry_price, exit_price, leverage, pnl, pnl_percent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (position["symbol"], position["side"], position["amount"], 
                  entry_price, current_price, position["leverage"], pnl, pnl_percent))
        else:
            # Partial close - update position amount
            new_amount = position["amount"] * ((100 - request.percent) / 100)
            cursor.execute("""
                UPDATE positions 
                SET amount = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (new_amount, position_id))
            
            # Add partial close to trades history
            cursor.execute("""
                INSERT INTO trades_history 
                (symbol, side, amount, entry_price, exit_price, leverage, pnl, pnl_percent)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (position["symbol"], position["side"], close_amount, 
                  entry_price, current_price, position["leverage"], pnl, pnl_percent))
    
    # Broadcast update
    await broadcast_to_websockets({
        "type": "position_closed",
        "position_id": position_id,
        "percent": request.percent,
        "pnl": pnl
    })
    
    return {
        "ok": True,
        "position_id": position_id,
        "closed_percent": request.percent,
        "pnl": round(pnl, 2),
        "pnl_percent": round(pnl_percent, 2)
    }


@app.post("/positions/{position_id}/modify")
async def modify_position(position_id: int, request: ModifyPositionRequest):
    """Modify position SL/TP"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check if position exists
        cursor.execute("SELECT * FROM positions WHERE id = ? AND status = 'open'", (position_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Position not found")
        
        # Update SL/TP
        updates = []
        params = []
        
        if request.sl is not None:
            updates.append("sl = ?")
            params.append(request.sl)
        
        if request.tp is not None:
            updates.append("tp = ?")
            params.append(request.tp)
        
        if updates:
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(position_id)
            
            query = f"UPDATE positions SET {', '.join(updates)} WHERE id = ?"
            cursor.execute(query, params)
    
    # Broadcast update
    await broadcast_to_websockets({
        "type": "position_modified",
        "position_id": position_id,
        "sl": request.sl,
        "tp": request.tp
    })
    
    return {
        "ok": True,
        "position_id": position_id,
        "sl": request.sl,
        "tp": request.tp
    }


@app.get("/trades/history")
async def get_trades_history(limit: int = Query(100, ge=1, le=1000)):
    """Get trades history"""
    trades = get_trades_history_from_db(limit)
    
    # Calculate statistics
    total_pnl = sum(t["pnl"] for t in trades)
    winning_trades = [t for t in trades if t["pnl"] > 0]
    losing_trades = [t for t in trades if t["pnl"] < 0]
    
    return {
        "trades": trades,
        "total": len(trades),
        "statistics": {
            "total_pnl": round(total_pnl, 2),
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": round((len(winning_trades) / len(trades) * 100) if trades else 0, 2)
        }
    }


@app.get("/equity")
async def get_equity(range: str = Query("1D", pattern="^(1H|4H|1D|1W|1M)$")):
    """Get equity data for specified time range"""
    equity_points = get_equity_data_from_db(range)
    
    # If no data, create some sample data
    if not equity_points:
        # Add some mock equity data
        from builtins import range as range_func
        now = datetime.now()
        equity_points = []
        for i in range_func(20):
            equity_points.append({
                "timestamp": (now - timedelta(hours=i)).isoformat(),
                "equity": 10000 + (i * 50),
                "balance": 10000,
                "unrealized_pnl": i * 50
            })
        equity_points.reverse()
    
    return {
        "range": range,
        "data": equity_points,
        "total_points": len(equity_points)
    }


@app.post("/bot/start")
async def start_bot():
    """Start the trading bot"""
    bot_state["status"] = "running"
    bot_state["started_at"] = datetime.now().isoformat()
    bot_state["last_update"] = datetime.now().isoformat()
    
    # Broadcast update
    await broadcast_to_websockets({
        "type": "bot_status",
        "status": "running",
        "started_at": bot_state["started_at"]
    })
    
    return {"ok": True, "status": "running"}


@app.post("/bot/pause")
async def pause_bot():
    """Pause the trading bot"""
    bot_state["status"] = "paused"
    bot_state["last_update"] = datetime.now().isoformat()
    
    # Broadcast update
    await broadcast_to_websockets({
        "type": "bot_status",
        "status": "paused"
    })
    
    return {"ok": True, "status": "paused"}


@app.post("/bot/stop")
async def stop_bot():
    """Stop the trading bot"""
    bot_state["status"] = "stopped"
    bot_state["last_update"] = datetime.now().isoformat()
    
    # Broadcast update
    await broadcast_to_websockets({
        "type": "bot_status",
        "status": "stopped"
    })
    
    return {"ok": True, "status": "stopped"}


@app.post("/config/update")
async def update_config(request: ConfigUpdateRequest):
    """Update bot configuration"""
    # Save config to file
    config_file = "bot_config.json"
    
    with open(config_file, "w") as f:
        json.dump(request.config, f, indent=2)
    
    # Broadcast update
    await broadcast_to_websockets({
        "type": "config_updated",
        "config": request.config
    })
    
    return {
        "ok": True,
        "message": "Configuration updated successfully"
    }


@app.post("/trade/quick")
async def quick_trade(request: QuickTradeRequest):
    """Execute a quick trade"""
    try:
        # Get current price
        entry_price = await binance_client.get_price(request.symbol)
        
        # Calculate SL and TP prices
        if request.side.upper() in ["LONG", "BUY"]:
            sl_price = entry_price * (1 - request.sl_percent / 100) if request.sl_percent else None
            tp_price = entry_price * (1 + request.tp_percent / 100) if request.tp_percent else None
        else:
            sl_price = entry_price * (1 + request.sl_percent / 100) if request.sl_percent else None
            tp_price = entry_price * (1 - request.tp_percent / 100) if request.tp_percent else None
        
        # Place order (mock for now)
        order = await binance_client.place_order(
            symbol=request.symbol,
            side=request.side,
            amount=request.amount,
            leverage=request.leverage,
            sl=sl_price,
            tp=tp_price
        )
        
        # Save position to database
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO positions 
                (symbol, side, amount, entry_price, current_price, leverage, sl, tp, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'open')
            """, (request.symbol, request.side, request.amount, entry_price, 
                  entry_price, request.leverage, sl_price, tp_price))
            
            position_id = cursor.lastrowid
        
        # Broadcast update
        await broadcast_to_websockets({
            "type": "new_position",
            "position_id": position_id,
            "symbol": request.symbol,
            "side": request.side,
            "amount": request.amount,
            "entry_price": entry_price,
            "leverage": request.leverage
        })
        
        return {
            "ok": True,
            "position_id": position_id,
            "symbol": request.symbol,
            "side": request.side,
            "amount": request.amount,
            "entry_price": entry_price,
            "leverage": request.leverage,
            "sl": sl_price,
            "tp": tp_price,
            "status": "filled"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    websocket_clients.append(websocket)
    
    try:
        # Send initial status
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to RLdC Trading Bot",
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep connection alive and handle incoming messages
        while True:
            try:
                data = await websocket.receive_text()
                # Echo back or handle commands
                await websocket.send_json({
                    "type": "echo",
                    "message": f"Received: {data}",
                    "timestamp": datetime.now().isoformat()
                })
            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"WebSocket error: {e}")
                break
                
    finally:
        if websocket in websocket_clients:
            websocket_clients.remove(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
