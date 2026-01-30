"""
FastAPI Gateway Server for RLdC Trading Bot
Provides REST API and WebSocket endpoints for bot control and monitoring
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime, timedelta, timezone
import asyncio
import json
import sqlite3
from contextlib import contextmanager
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="RLdC Trading Bot Gateway",
    description="API Gateway for RLdC Trading Bot with Binance Futures integration",
    version="1.0.0"
)

# CORS middleware - SECURITY WARNING: Restrict origins in production!
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Change to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enums
class BotState(str, Enum):
    RUN = "RUN"
    PAUSE = "PAUSE"
    ERROR = "ERROR"

class PositionSide(str, Enum):
    LONG = "LONG"
    SHORT = "SHORT"

class TimeRange(str, Enum):
    ONE_HOUR = "1H"
    FOUR_HOUR = "4H"
    ONE_DAY = "1D"
    ONE_WEEK = "1W"
    ONE_MONTH = "1M"

# Request/Response Models
class BotStatus(BaseModel):
    state: BotState
    balance: float
    equity: float
    pnl: float
    pnlPercent: float
    openPositions: int
    dailyPnl: float
    weeklyPnl: float
    monthlyPnl: float
    drawdown: float
    uptime: int  # seconds

class Position(BaseModel):
    model_config = ConfigDict(validate_assignment=True)
    
    id: str
    symbol: str
    side: PositionSide
    entryPrice: float
    currentPrice: float
    quantity: float
    leverage: int
    pnl: float
    pnlPercent: float
    sl: Optional[float] = None
    tp: Optional[float] = None
    openedAt: datetime

class ClosePositionRequest(BaseModel):
    percent: float = Field(default=100.0, ge=0.0, le=100.0)

class ModifyPositionRequest(BaseModel):
    sl: Optional[float] = None
    tp: Optional[float] = None

class Trade(BaseModel):
    id: str
    symbol: str
    side: PositionSide
    entryPrice: float
    exitPrice: float
    quantity: float
    leverage: int
    pnl: float
    pnlPercent: float
    openedAt: datetime
    closedAt: datetime

class EquityPoint(BaseModel):
    timestamp: datetime
    equity: float
    balance: float

class ConfigUpdate(BaseModel):
    kelly: Optional[float] = None
    atr: Optional[Dict[str, Any]] = None
    hedge: Optional[Dict[str, Any]] = None

class QuickTradeRequest(BaseModel):
    symbol: str
    side: PositionSide
    amount: float
    leverage: int = Field(default=1, ge=1, le=125)
    sl_percent: Optional[float] = None
    tp_percent: Optional[float] = None

# Global state management
class StateManager:
    """In-memory state manager with SQLite persistence"""
    
    def __init__(self, db_path: str = "trading_bot.db"):
        self.db_path = db_path
        self.bot_state = BotState.PAUSE
        self.balance = 10000.0
        self.equity = 10000.0
        self.start_time = datetime.now(timezone.utc)
        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []
        self.equity_history: List[EquityPoint] = []
        self.config = {
            "kelly": 0.25,
            "atr": {"period": 14, "multiplier": 2.0},
            "hedge": {"enabled": False, "ratio": 0.5}
        }
        self._init_database()
    
    @contextmanager
    def get_db(self):
        """Database connection context manager"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _init_database(self):
        """Initialize SQLite database schema"""
        with self.get_db() as conn:
            cursor = conn.cursor()
            
            # Positions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS positions (
                    id TEXT PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    current_price REAL NOT NULL,
                    quantity REAL NOT NULL,
                    leverage INTEGER NOT NULL,
                    pnl REAL NOT NULL,
                    pnl_percent REAL NOT NULL,
                    sl REAL,
                    tp REAL,
                    opened_at TIMESTAMP NOT NULL,
                    status TEXT DEFAULT 'open'
                )
            """)
            
            # Trades table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    id TEXT PRIMARY KEY,
                    symbol TEXT NOT NULL,
                    side TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    exit_price REAL NOT NULL,
                    quantity REAL NOT NULL,
                    leverage INTEGER NOT NULL,
                    pnl REAL NOT NULL,
                    pnl_percent REAL NOT NULL,
                    opened_at TIMESTAMP NOT NULL,
                    closed_at TIMESTAMP NOT NULL
                )
            """)
            
            # Equity history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS equity_history (
                    timestamp TIMESTAMP PRIMARY KEY,
                    equity REAL NOT NULL,
                    balance REAL NOT NULL
                )
            """)
            
            # Config table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS config (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            
            conn.commit()
    
    def get_status(self) -> BotStatus:
        """Get current bot status"""
        # Calculate PnL metrics
        total_pnl = sum(p.pnl for p in self.positions.values())
        pnl_percent = (total_pnl / self.balance * 100) if self.balance > 0 else 0.0
        
        # Calculate time-based PnL (simplified)
        now = datetime.now(timezone.utc)
        daily_pnl = self._calculate_period_pnl(now - timedelta(days=1))
        weekly_pnl = self._calculate_period_pnl(now - timedelta(weeks=1))
        monthly_pnl = self._calculate_period_pnl(now - timedelta(days=30))
        
        # Calculate drawdown
        max_equity = max([ep.equity for ep in self.equity_history], default=self.equity)
        drawdown = ((max_equity - self.equity) / max_equity * 100) if max_equity > 0 else 0.0
        
        # Calculate uptime
        uptime = int((datetime.now(timezone.utc) - self.start_time).total_seconds())
        
        return BotStatus(
            state=self.bot_state,
            balance=self.balance,
            equity=self.equity,
            pnl=total_pnl,
            pnlPercent=pnl_percent,
            openPositions=len(self.positions),
            dailyPnl=daily_pnl,
            weeklyPnl=weekly_pnl,
            monthlyPnl=monthly_pnl,
            drawdown=drawdown,
            uptime=uptime
        )
    
    def _calculate_period_pnl(self, since: datetime) -> float:
        """Calculate PnL for a specific time period"""
        period_trades = [t for t in self.trades if t.closedAt >= since]
        return sum(t.pnl for t in period_trades)
    
    def get_positions(self) -> List[Position]:
        """Get all open positions"""
        return list(self.positions.values())
    
    def get_position(self, position_id: str) -> Optional[Position]:
        """Get a specific position"""
        return self.positions.get(position_id)
    
    def close_position(self, position_id: str, percent: float = 100.0):
        """Close a position (full or partial)"""
        position = self.positions.get(position_id)
        if not position:
            raise ValueError(f"Position {position_id} not found")
        
        # For full close, remove position and add to trades
        if percent >= 100.0:
            trade = Trade(
                id=position.id,
                symbol=position.symbol,
                side=position.side,
                entryPrice=position.entryPrice,
                exitPrice=position.currentPrice,
                quantity=position.quantity,
                leverage=position.leverage,
                pnl=position.pnl,
                pnlPercent=position.pnlPercent,
                openedAt=position.openedAt,
                closedAt=datetime.now(timezone.utc)
            )
            self.trades.append(trade)
            self.balance += position.pnl
            self.equity = self.balance + sum(p.pnl for p in self.positions.values())
            del self.positions[position_id]
        else:
            # Partial close - reduce quantity
            close_qty = position.quantity * (percent / 100.0)
            close_pnl = position.pnl * (percent / 100.0)
            
            # Create trade for closed portion
            trade = Trade(
                id=f"{position.id}_partial_{len(self.trades)}",
                symbol=position.symbol,
                side=position.side,
                entryPrice=position.entryPrice,
                exitPrice=position.currentPrice,
                quantity=close_qty,
                leverage=position.leverage,
                pnl=close_pnl,
                pnlPercent=position.pnlPercent,
                openedAt=position.openedAt,
                closedAt=datetime.now(timezone.utc)
            )
            self.trades.append(trade)
            
            # Update position
            position.quantity -= close_qty
            position.pnl -= close_pnl
            self.balance += close_pnl
            self.equity = self.balance + sum(p.pnl for p in self.positions.values())
    
    def modify_position(self, position_id: str, sl: Optional[float] = None, tp: Optional[float] = None):
        """Modify position SL/TP"""
        position = self.positions.get(position_id)
        if not position:
            raise ValueError(f"Position {position_id} not found")
        
        if sl is not None:
            position.sl = sl
        if tp is not None:
            position.tp = tp
    
    def get_trade_history(self) -> List[Trade]:
        """Get all closed trades"""
        return self.trades
    
    def get_equity_curve(self, time_range: TimeRange) -> List[EquityPoint]:
        """Get equity curve data for a specific time range"""
        now = datetime.now(timezone.utc)
        
        # Calculate cutoff time
        if time_range == TimeRange.ONE_HOUR:
            cutoff = now - timedelta(hours=1)
        elif time_range == TimeRange.FOUR_HOUR:
            cutoff = now - timedelta(hours=4)
        elif time_range == TimeRange.ONE_DAY:
            cutoff = now - timedelta(days=1)
        elif time_range == TimeRange.ONE_WEEK:
            cutoff = now - timedelta(weeks=1)
        else:  # ONE_MONTH
            cutoff = now - timedelta(days=30)
        
        # Filter equity history
        filtered = [ep for ep in self.equity_history if ep.timestamp >= cutoff]
        
        # If no data, return current point
        if not filtered:
            filtered = [EquityPoint(timestamp=now, equity=self.equity, balance=self.balance)]
        
        return filtered
    
    def update_config(self, updates: ConfigUpdate):
        """Update bot configuration"""
        if updates.kelly is not None:
            self.config["kelly"] = updates.kelly
        if updates.atr is not None:
            self.config["atr"].update(updates.atr)
        if updates.hedge is not None:
            self.config["hedge"].update(updates.hedge)
    
    def execute_quick_trade(self, request: QuickTradeRequest) -> Position:
        """Execute a quick trade"""
        position_id = f"pos_{len(self.positions) + len(self.trades) + 1}"
        
        # Calculate SL/TP prices if percentages provided
        sl_price = None
        tp_price = None
        
        # For demo, use a mock current price
        current_price = 50000.0  # This would come from Binance API
        
        if request.sl_percent:
            if request.side == PositionSide.LONG:
                sl_price = current_price * (1 - request.sl_percent / 100)
            else:
                sl_price = current_price * (1 + request.sl_percent / 100)
        
        if request.tp_percent:
            if request.side == PositionSide.LONG:
                tp_price = current_price * (1 + request.tp_percent / 100)
            else:
                tp_price = current_price * (1 - request.tp_percent / 100)
        
        # Create position
        position = Position(
            id=position_id,
            symbol=request.symbol,
            side=request.side,
            entryPrice=current_price,
            currentPrice=current_price,
            quantity=request.amount,
            leverage=request.leverage,
            pnl=0.0,
            pnlPercent=0.0,
            sl=sl_price,
            tp=tp_price,
            openedAt=datetime.now(timezone.utc)
        )
        
        self.positions[position_id] = position
        return position

# Initialize state manager
state_manager = StateManager()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()

# REST API Endpoints

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "RLdC Trading Bot Gateway",
        "version": "1.0.0",
        "status": "online"
    }

@app.get("/status", response_model=BotStatus)
async def get_status():
    """Get current bot status"""
    return state_manager.get_status()

@app.get("/positions", response_model=List[Position])
async def get_positions():
    """Get all open positions"""
    return state_manager.get_positions()

@app.post("/positions/{position_id}/close")
async def close_position(position_id: str, request: ClosePositionRequest):
    """Close a position by ID"""
    try:
        state_manager.close_position(position_id, request.percent)
        
        # Broadcast update
        await manager.broadcast({
            "type": "position_closed",
            "position_id": position_id,
            "percent": request.percent
        })
        
        return {"status": "success", "message": f"Position {position_id} closed"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/positions/{position_id}/modify")
async def modify_position(position_id: str, request: ModifyPositionRequest):
    """Modify position SL/TP"""
    try:
        state_manager.modify_position(position_id, request.sl, request.tp)
        
        # Broadcast update
        await manager.broadcast({
            "type": "position_modified",
            "position_id": position_id,
            "sl": request.sl,
            "tp": request.tp
        })
        
        return {"status": "success", "message": f"Position {position_id} modified"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/trades/history", response_model=List[Trade])
async def get_trade_history():
    """Get trade history"""
    return state_manager.get_trade_history()

@app.get("/equity", response_model=List[EquityPoint])
async def get_equity(range: TimeRange = Query(default=TimeRange.ONE_DAY)):
    """Get equity curve data"""
    return state_manager.get_equity_curve(range)

@app.post("/bot/start")
async def start_bot():
    """Start the bot"""
    state_manager.bot_state = BotState.RUN
    
    await manager.broadcast({
        "type": "bot_state_changed",
        "state": "RUN"
    })
    
    return {"status": "success", "message": "Bot started"}

@app.post("/bot/pause")
async def pause_bot():
    """Pause the bot"""
    state_manager.bot_state = BotState.PAUSE
    
    await manager.broadcast({
        "type": "bot_state_changed",
        "state": "PAUSE"
    })
    
    return {"status": "success", "message": "Bot paused"}

@app.post("/bot/stop")
async def stop_bot():
    """Stop the bot (sets to PAUSE state)"""
    state_manager.bot_state = BotState.PAUSE
    
    await manager.broadcast({
        "type": "bot_state_changed",
        "state": "PAUSE"
    })
    
    return {"status": "success", "message": "Bot stopped (paused)"}

@app.post("/config/update")
async def update_config(config: ConfigUpdate):
    """Update bot configuration"""
    state_manager.update_config(config)
    
    await manager.broadcast({
        "type": "config_updated",
        "config": state_manager.config
    })
    
    return {"status": "success", "message": "Configuration updated", "config": state_manager.config}

@app.post("/trade/quick", response_model=Position)
async def execute_quick_trade(request: QuickTradeRequest):
    """Execute a quick trade"""
    position = state_manager.execute_quick_trade(request)
    
    await manager.broadcast({
        "type": "position_opened",
        "position": position.model_dump()
    })
    
    return position

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    
    try:
        # Send initial status
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to RLdC Trading Bot"
        })
        
        # Keep connection alive and send periodic updates
        while True:
            try:
                # Receive any messages from client
                data = await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
                
                # Echo back (optional)
                await websocket.send_json({
                    "type": "echo",
                    "data": data
                })
            except asyncio.TimeoutError:
                # Send periodic updates
                status = state_manager.get_status()
                await websocket.send_json({
                    "type": "status_update",
                    "data": status.model_dump()
                })
                await asyncio.sleep(5)  # Update every 5 seconds
            except WebSocketDisconnect:
                break
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                break
    finally:
        manager.disconnect(websocket)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
