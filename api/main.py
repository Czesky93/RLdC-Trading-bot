"""
FastAPI backend for RLdC Trading Bot
Provides REST API and WebSocket endpoints for the Flutter Web frontend
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import json
import asyncio
from datetime import datetime

app = FastAPI(title="RLdC Trading Bot API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Store active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Error sending to client: {e}")
                disconnected.append(connection)
        
        # Remove disconnected clients
        for conn in disconnected:
            if conn in self.active_connections:
                self.active_connections.remove(conn)

manager = ConnectionManager()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "RLdC Trading Bot API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "status": "/status",
            "websocket": "/ws"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_connections": len(manager.active_connections)
    }


@app.get("/status")
async def get_status():
    """Get trading bot status"""
    return {
        "bot_status": "running",
        "trading_active": True,
        "connections": len(manager.active_connections),
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/markets")
async def get_markets():
    """Get market data"""
    # This would connect to actual trading data
    return {
        "markets": [
            {"symbol": "BTC/USDT", "price": 45000.00, "change": 2.5},
            {"symbol": "ETH/USDT", "price": 3200.00, "change": 1.8},
            {"symbol": "BNB/USDT", "price": 420.00, "change": -0.5}
        ]
    }


@app.get("/api/trades")
async def get_trades():
    """Get recent trades"""
    return {
        "trades": [
            {
                "id": 1,
                "symbol": "BTC/USDT",
                "side": "buy",
                "price": 44500.00,
                "amount": 0.1,
                "timestamp": datetime.now().isoformat()
            }
        ]
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates
    Sends periodic updates to connected clients
    """
    await manager.connect(websocket)
    
    try:
        # Send initial connection message
        await websocket.send_json({
            "type": "connection",
            "status": "connected",
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep connection alive and send periodic updates
        counter = 0
        while True:
            # Receive any messages from client (for ping/pong)
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=5.0)
                # Echo back or process client messages
                await websocket.send_json({
                    "type": "echo",
                    "message": data,
                    "timestamp": datetime.now().isoformat()
                })
            except asyncio.TimeoutError:
                # Send periodic update every 5 seconds
                counter += 1
                await websocket.send_json({
                    "type": "update",
                    "data": {
                        "counter": counter,
                        "status": "active",
                        "timestamp": datetime.now().isoformat()
                    }
                })
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("WebSocket client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@app.post("/api/broadcast")
async def broadcast_message(message: dict):
    """
    Broadcast a message to all connected WebSocket clients
    Used for testing
    """
    await manager.broadcast(message)
    return {"status": "broadcasted", "recipients": len(manager.active_connections)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
