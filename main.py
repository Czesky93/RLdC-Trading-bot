"""
FastAPI Gateway dla RLdC Trading Bot
Główna bramka API do zarządzania botem tradingowym z integracją Binance Futures API
"""

from fastapi import FastAPI, WebSocket, HTTPException, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import asyncio
import json
import random
import logging
from binance.client import Client
from binance.exceptions import BinanceAPIException
import os
from config_manager import load_config

# Konfiguracja logowania
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Inicjalizacja FastAPI
app = FastAPI(
    title="RLdC Trading Bot API",
    description="Zaawansowany bot tradingowy z AI i integracją Binance Futures",
    version="1.0.0"
)

# Konfiguracja CORS zgodnie z wymaganiami
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Wczytanie konfiguracji
try:
    config = load_config()
    logger.info("Konfiguracja załadowana pomyślnie")
except Exception as e:
    logger.warning(f"Nie można załadować konfiguracji: {e}. Używam wartości domyślnych.")
    config = {
        "BINANCE_API_KEY": "",
        "BINANCE_API_SECRET": "",
        "START_BALANCE": 1000
    }

# Inicjalizacja klienta Binance (jeśli dostępne klucze API)
binance_client = None
if config.get("BINANCE_API_KEY") and config.get("BINANCE_API_SECRET"):
    try:
        binance_client = Client(
            config["BINANCE_API_KEY"],
            config["BINANCE_API_SECRET"]
        )
    except Exception as e:
        print(f"⚠️ Nie można połączyć z Binance API: {e}")

# Stan w pamięci (pozycje, equity, historia)
class TradingState:
    def __init__(self):
        self.bot_status = "stopped"  # stopped, running, paused
        self.positions: List[Dict[str, Any]] = []
        self.trades_history: List[Dict[str, Any]] = []
        self.equity_history: List[Dict[str, float]] = []
        self.current_balance = config.get("START_BALANCE", 1000.0)
        self.websocket_connections: List[WebSocket] = []
        
        # Inicjalizacja przykładowych danych
        self._init_sample_data()
    
    def _init_sample_data(self):
        """Inicjalizacja przykładowych danych dla demonstracji"""
        now = datetime.now()
        
        # Przykładowe pozycje
        self.positions = [
            {
                "id": 1,
                "symbol": "BTC/USDT",
                "side": "LONG",
                "amount": 0.05,
                "entry_price": 42000.0,
                "current_price": 43500.0,
                "leverage": 10,
                "sl": 41000.0,
                "tp": 44000.0,
                "pnl": 75.0,
                "pnl_percent": 3.57,
                "opened_at": (now - timedelta(hours=2)).isoformat()
            },
            {
                "id": 2,
                "symbol": "ETH/USDT",
                "side": "SHORT",
                "amount": 2.0,
                "entry_price": 2250.0,
                "current_price": 2200.0,
                "leverage": 5,
                "sl": 2300.0,
                "tp": 2150.0,
                "pnl": 50.0,
                "pnl_percent": 2.22,
                "opened_at": (now - timedelta(hours=5)).isoformat()
            }
        ]
        
        # Przykładowa historia transakcji
        self.trades_history = [
            {
                "id": 101,
                "symbol": "BTC/USDT",
                "side": "LONG",
                "amount": 0.1,
                "entry_price": 40000.0,
                "exit_price": 41000.0,
                "leverage": 10,
                "pnl": 100.0,
                "pnl_percent": 2.5,
                "opened_at": (now - timedelta(days=1)).isoformat(),
                "closed_at": (now - timedelta(hours=12)).isoformat(),
                "status": "closed"
            },
            {
                "id": 102,
                "symbol": "ETH/USDT",
                "side": "SHORT",
                "amount": 5.0,
                "entry_price": 2300.0,
                "exit_price": 2250.0,
                "leverage": 5,
                "pnl": 125.0,
                "pnl_percent": 2.17,
                "opened_at": (now - timedelta(days=2)).isoformat(),
                "closed_at": (now - timedelta(days=1, hours=12)).isoformat(),
                "status": "closed"
            }
        ]
        
        # Przykładowa historia equity
        base_equity = self.current_balance
        for i in range(100):
            timestamp = now - timedelta(hours=100-i)
            # Symulacja wzrostu equity z fluktuacjami
            equity = base_equity + (i * 5) + random.uniform(-20, 20)
            self.equity_history.append({
                "timestamp": timestamp.isoformat(),
                "equity": round(equity, 2)
            })

state = TradingState()

# Modele Pydantic dla walidacji danych wejściowych
class ClosePositionRequest(BaseModel):
    percent: int = Field(default=100, ge=1, le=100, description="Procent pozycji do zamknięcia (1-100)")

class ModifyPositionRequest(BaseModel):
    sl: Optional[float] = None
    tp: Optional[float] = None

class QuickTradeRequest(BaseModel):
    symbol: str
    side: str  # LONG lub SHORT
    amount: float = Field(gt=0, description="Ilość do handlu (musi być > 0)")
    leverage: int = Field(default=1, ge=1, le=125, description="Dźwignia (1-125)")
    sl_percent: Optional[float] = Field(default=None, ge=0, le=100)
    tp_percent: Optional[float] = Field(default=None, ge=0, le=100)

class ConfigUpdateRequest(BaseModel):
    updates: Dict[str, Any]

# Funkcje pomocnicze
async def broadcast_websocket(message: Dict[str, Any]):
    """Wysyła wiadomość do wszystkich podłączonych klientów WebSocket"""
    if state.websocket_connections:
        message_json = json.dumps(message)
        disconnected = []
        for ws in state.websocket_connections:
            try:
                await ws.send_text(message_json)
            except Exception:
                disconnected.append(ws)
        
        # Usuń rozłączone połączenia
        for ws in disconnected:
            state.websocket_connections.remove(ws)

def get_binance_price(symbol: str) -> Optional[float]:
    """Pobiera aktualną cenę z Binance API"""
    if not binance_client:
        return None
    
    try:
        # Konwersja symbolu z formatu BTC/USDT na BTCUSDT
        binance_symbol = symbol.replace("/", "")
        ticker = binance_client.get_symbol_ticker(symbol=binance_symbol)
        return float(ticker['price'])
    except BinanceAPIException as e:
        print(f"⚠️ Błąd Binance API dla {symbol}: {e}")
        return None
    except Exception as e:
        print(f"⚠️ Nieoczekiwany błąd pobierania ceny dla {symbol}: {e}")
        return None

def update_positions_prices():
    """Aktualizuje aktualne ceny pozycji z Binance API"""
    for position in state.positions:
        current_price = get_binance_price(position["symbol"])
        if current_price:
            position["current_price"] = current_price
            
            # Przelicz PnL
            if position["side"] == "LONG":
                pnl = (current_price - position["entry_price"]) * position["amount"] * position["leverage"]
            else:  # SHORT
                pnl = (position["entry_price"] - current_price) * position["amount"] * position["leverage"]
            
            position["pnl"] = round(pnl, 2)
            position["pnl_percent"] = round((pnl / (position["entry_price"] * position["amount"])) * 100, 2)

# Endpointy API

@app.get("/")
async def root():
    """Endpoint główny z informacjami o API"""
    return {
        "name": "RLdC Trading Bot API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "status": "/status",
            "positions": "/positions",
            "trades_history": "/trades/history",
            "equity": "/equity?range=1D",
            "websocket": "/ws"
        }
    }

@app.get("/status")
async def get_status():
    """Zwraca status bota tradingowego"""
    # Aktualizacja cen pozycji
    update_positions_prices()
    
    # Obliczenie całkowitego PnL
    total_pnl = sum(pos.get("pnl", 0) for pos in state.positions)
    
    # Pobranie ceny BTC dla statusu
    btc_price = get_binance_price("BTC/USDT") or 43000.0
    
    return {
        "bot_status": state.bot_status,
        "current_balance": state.current_balance,
        "total_pnl": round(total_pnl, 2),
        "open_positions": len(state.positions),
        "total_trades": len(state.trades_history),
        "btc_price": btc_price,
        "last_update": datetime.now().isoformat()
    }

@app.get("/positions")
async def get_positions():
    """Zwraca listę aktywnych pozycji"""
    # Aktualizacja cen pozycji
    update_positions_prices()
    
    return {
        "positions": state.positions,
        "count": len(state.positions)
    }

@app.post("/positions/{position_id}/close")
async def close_position(position_id: int, request: ClosePositionRequest):
    """Zamyka pozycję (całkowicie lub częściowo)"""
    # Znajdź pozycję
    position = next((p for p in state.positions if p["id"] == position_id), None)
    if not position:
        raise HTTPException(status_code=404, detail=f"Pozycja {position_id} nie znaleziona")
    
    # Zamknij pozycję
    if request.percent == 100:
        # Całkowite zamknięcie
        closed_position = position.copy()
        closed_position["exit_price"] = position["current_price"]
        closed_position["closed_at"] = datetime.now().isoformat()
        closed_position["status"] = "closed"
        
        # Dodaj do historii
        state.trades_history.insert(0, closed_position)
        
        # Usuń z aktywnych pozycji
        state.positions.remove(position)
        
        # Aktualizuj balans
        state.current_balance += position.get("pnl", 0)
        
        # Powiadomienie WebSocket
        await broadcast_websocket({
            "type": "position_closed",
            "position_id": position_id,
            "pnl": position.get("pnl", 0)
        })
        
        return {
            "status": "success",
            "message": f"Pozycja {position_id} zamknięta w 100%",
            "pnl": position.get("pnl", 0)
        }
    else:
        # Częściowe zamknięcie
        close_amount = position["amount"] * (request.percent / 100)
        remaining_amount = position["amount"] - close_amount
        
        # Oblicz PnL dla zamkniętej części
        if position["side"] == "LONG":
            partial_pnl = (position["current_price"] - position["entry_price"]) * close_amount * position["leverage"]
        else:
            partial_pnl = (position["entry_price"] - position["current_price"]) * close_amount * position["leverage"]
        
        # Aktualizuj pozycję
        position["amount"] = remaining_amount
        state.current_balance += partial_pnl
        
        # Powiadomienie WebSocket o częściowym zamknięciu
        await broadcast_websocket({
            "type": "position_partially_closed",
            "position_id": position_id,
            "percent": request.percent,
            "pnl": round(partial_pnl, 2),
            "remaining_amount": remaining_amount
        })
        
        return {
            "status": "success",
            "message": f"Pozycja {position_id} zamknięta w {request.percent}%",
            "pnl": round(partial_pnl, 2),
            "remaining_amount": remaining_amount
        }

@app.post("/positions/{position_id}/modify")
async def modify_position(position_id: int, request: ModifyPositionRequest):
    """Modyfikuje stop-loss i take-profit pozycji"""
    # Znajdź pozycję
    position = next((p for p in state.positions if p["id"] == position_id), None)
    if not position:
        raise HTTPException(status_code=404, detail=f"Pozycja {position_id} nie znaleziona")
    
    # Zaktualizuj SL/TP
    if request.sl is not None:
        position["sl"] = request.sl
    if request.tp is not None:
        position["tp"] = request.tp
    
    # Powiadomienie WebSocket
    await broadcast_websocket({
        "type": "position_modified",
        "position_id": position_id,
        "sl": position.get("sl"),
        "tp": position.get("tp")
    })
    
    return {
        "status": "success",
        "message": f"Pozycja {position_id} zmodyfikowana",
        "position": position
    }

@app.get("/trades/history")
async def get_trades_history():
    """Zwraca historię zamkniętych transakcji"""
    return {
        "trades": state.trades_history,
        "count": len(state.trades_history)
    }

@app.get("/equity")
async def get_equity(range: str = "1D"):
    """Zwraca historię equity w zadanym przedziale czasowym"""
    # Mapowanie zakresów na ilość godzin
    range_hours = {
        "1H": 1,
        "4H": 4,
        "1D": 24,
        "1W": 168,
        "1M": 720
    }
    
    if range not in range_hours:
        raise HTTPException(status_code=400, detail=f"Nieprawidłowy zakres. Użyj: {', '.join(range_hours.keys())}")
    
    hours = range_hours[range]
    cutoff_time = datetime.now() - timedelta(hours=hours)
    
    # Filtruj dane equity
    filtered_equity = [
        entry for entry in state.equity_history
        if datetime.fromisoformat(entry["timestamp"]) >= cutoff_time
    ]
    
    return {
        "range": range,
        "data": filtered_equity,
        "count": len(filtered_equity),
        "current_equity": state.current_balance + sum(p.get("pnl", 0) for p in state.positions)
    }

@app.post("/bot/start")
async def start_bot():
    """Uruchamia bota tradingowego"""
    if state.bot_status == "running":
        return {"status": "info", "message": "Bot już działa"}
    
    state.bot_status = "running"
    
    # Powiadomienie WebSocket
    await broadcast_websocket({
        "type": "bot_status",
        "status": "running"
    })
    
    return {
        "status": "success",
        "message": "Bot uruchomiony",
        "bot_status": state.bot_status
    }

@app.post("/bot/pause")
async def pause_bot():
    """Wstrzymuje działanie bota"""
    if state.bot_status == "paused":
        return {"status": "info", "message": "Bot już jest wstrzymany"}
    
    state.bot_status = "paused"
    
    # Powiadomienie WebSocket
    await broadcast_websocket({
        "type": "bot_status",
        "status": "paused"
    })
    
    return {
        "status": "success",
        "message": "Bot wstrzymany",
        "bot_status": state.bot_status
    }

@app.post("/bot/stop")
async def stop_bot():
    """Zatrzymuje bota tradingowego"""
    state.bot_status = "stopped"
    
    # Powiadomienie WebSocket
    await broadcast_websocket({
        "type": "bot_status",
        "status": "stopped"
    })
    
    return {
        "status": "success",
        "message": "Bot zatrzymany",
        "bot_status": state.bot_status
    }

@app.post("/config/update")
async def update_config(request: ConfigUpdateRequest):
    """Aktualizuje konfigurację bota"""
    from config_manager import update_config as update_config_file
    
    try:
        updated_config = update_config_file(request.updates)
        
        # Powiadomienie WebSocket
        await broadcast_websocket({
            "type": "config_updated",
            "updates": request.updates
        })
        
        return {
            "status": "success",
            "message": "Konfiguracja zaktualizowana",
            "config": updated_config
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd aktualizacji konfiguracji: {str(e)}")

@app.post("/trade/quick")
async def quick_trade(request: QuickTradeRequest):
    """Wykonuje szybki handel (otwiera nową pozycję)"""
    # Walidacja
    if request.side not in ["LONG", "SHORT"]:
        raise HTTPException(status_code=400, detail="side musi być LONG lub SHORT")
    
    # Pobierz aktualną cenę
    current_price = get_binance_price(request.symbol)
    if not current_price:
        # Jeśli nie ma połączenia z Binance, użyj przykładowej ceny
        current_price = 43000.0 if "BTC" in request.symbol else 2200.0
    
    # Oblicz SL i TP
    sl = None
    tp = None
    if request.sl_percent:
        if request.side == "LONG":
            sl = current_price * (1 - request.sl_percent / 100)
        else:
            sl = current_price * (1 + request.sl_percent / 100)
    
    if request.tp_percent:
        if request.side == "LONG":
            tp = current_price * (1 + request.tp_percent / 100)
        else:
            tp = current_price * (1 - request.tp_percent / 100)
    
    # Utwórz nową pozycję
    new_position = {
        "id": max([p["id"] for p in state.positions], default=0) + 1,
        "symbol": request.symbol,
        "side": request.side,
        "amount": request.amount,
        "entry_price": current_price,
        "current_price": current_price,
        "leverage": request.leverage,
        "sl": sl,
        "tp": tp,
        "pnl": 0.0,
        "pnl_percent": 0.0,
        "opened_at": datetime.now().isoformat()
    }
    
    state.positions.append(new_position)
    
    # Powiadomienie WebSocket
    await broadcast_websocket({
        "type": "position_opened",
        "position": new_position
    })
    
    return {
        "status": "success",
        "message": "Pozycja otwarta",
        "position": new_position
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint dla real-time updates"""
    await websocket.accept()
    state.websocket_connections.append(websocket)
    
    try:
        # Wyślij wiadomość powitalną
        await websocket.send_json({
            "type": "connected",
            "message": "Połączono z RLdC Trading Bot WebSocket",
            "timestamp": datetime.now().isoformat()
        })
        
        # Pętla nasłuchująca wiadomości od klienta
        while True:
            data = await websocket.receive_text()
            
            # Echo lub przetwarzanie wiadomości
            try:
                message = json.loads(data)
                
                # Obsługa różnych typów wiadomości
                if message.get("type") == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    })
                elif message.get("type") == "subscribe":
                    # Subskrypcja ticków cenowych
                    symbol = message.get("symbol", "BTC/USDT")
                    price = get_binance_price(symbol) or 43000.0
                    await websocket.send_json({
                        "type": "tick",
                        "symbol": symbol,
                        "price": price,
                        "timestamp": datetime.now().isoformat()
                    })
                else:
                    # Echo dla innych wiadomości
                    await websocket.send_json({
                        "type": "echo",
                        "data": message,
                        "timestamp": datetime.now().isoformat()
                    })
            except json.JSONDecodeError:
                # Jeśli wiadomość nie jest JSON, wyślij echo tekstowe
                await websocket.send_text(f"Echo: {data}")
    
    except WebSocketDisconnect:
        state.websocket_connections.remove(websocket)
        logger.info("Klient WebSocket rozłączony")
    except Exception as e:
        logger.exception(f"Błąd WebSocket: {e}")
        if websocket in state.websocket_connections:
            state.websocket_connections.remove(websocket)

# Task w tle do okresowego broadcastowania danych
@app.on_event("startup")
async def startup_event():
    """Uruchamia task w tle przy starcie aplikacji"""
    async def broadcast_market_updates():
        while True:
            await asyncio.sleep(5)  # Co 5 sekund
            
            if state.websocket_connections:
                # Aktualizuj ceny pozycji
                update_positions_prices()
                
                # Broadcast aktualnego statusu
                await broadcast_websocket({
                    "type": "market_update",
                    "positions": state.positions,
                    "bot_status": state.bot_status,
                    "timestamp": datetime.now().isoformat()
                })
    
    # Uruchom task w tle
    asyncio.create_task(broadcast_market_updates())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
