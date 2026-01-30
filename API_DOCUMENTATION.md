# FastAPI Gateway Server - API Documentation

## Overview

The RLdC Trading Bot FastAPI Gateway provides a comprehensive REST API and WebSocket interface for managing trading operations on Binance Futures.

## Getting Started

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

### Configuration

1. Copy the example configuration:
```bash
cp .env.example .env
cp config.json.example config.json
```

2. Edit `.env` and add your Binance API credentials:
```
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
```

### Running the Server

#### Option 1: Using the startup script (recommended)
```bash
./start_gateway.sh
```

#### Option 2: Using uvicorn directly
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

#### Option 3: Using the Python module
```bash
python main.py
```

The server will start on `http://0.0.0.0:8000` and be accessible from:
- Local machine: `http://localhost:8000`
- LAN network: `http://<your-ip>:8000`

## API Documentation

Once the server is running, access the interactive API documentation at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### Bot Control

#### Start Bot
```http
POST /bot/start
```
**Response:**
```json
{
  "ok": true,
  "status": "running"
}
```

#### Pause Bot
```http
POST /bot/pause
```
**Response:**
```json
{
  "ok": true,
  "status": "paused"
}
```

#### Stop Bot
```http
POST /bot/stop
```
**Response:**
```json
{
  "ok": true,
  "status": "stopped"
}
```

### Status & Information

#### Get Bot Status
```http
GET /status
```
**Response:**
```json
{
  "status": "running",
  "started_at": "2026-01-30T11:00:00",
  "last_update": "2026-01-30T11:30:00",
  "balance": 10000.0,
  "available_balance": 8000.0,
  "unrealized_pnl": 200.0,
  "open_positions": 3,
  "total_positions": 3
}
```

### Position Management

#### Get All Positions
```http
GET /positions
```
**Response:**
```json
{
  "positions": [
    {
      "id": 1,
      "symbol": "BTC/USDT",
      "side": "LONG",
      "amount": 100.0,
      "entry_price": 43500.0,
      "current_price": 43600.0,
      "leverage": 10,
      "sl": 42630.0,
      "tp": 45240.0,
      "pnl": 23.0,
      "pnl_percent": 2.3,
      "status": "open",
      "created_at": "2026-01-30 11:00:00",
      "updated_at": "2026-01-30 11:00:00"
    }
  ],
  "total": 1
}
```

#### Modify Position SL/TP
```http
POST /positions/{id}/modify
Content-Type: application/json

{
  "sl": 41000,
  "tp": 44000
}
```
**Response:**
```json
{
  "ok": true,
  "position_id": 1,
  "sl": 41000.0,
  "tp": 44000.0
}
```

#### Close Position
```http
POST /positions/{id}/close
Content-Type: application/json

{
  "percent": 100
}
```
**Parameters:**
- `percent`: Percentage of position to close (1-100)

**Response:**
```json
{
  "ok": true,
  "position_id": 1,
  "closed_percent": 100.0,
  "pnl": 100.0,
  "pnl_percent": 2.3
}
```

### Trading

#### Quick Trade
```http
POST /trade/quick
Content-Type: application/json

{
  "symbol": "BTC/USDT",
  "side": "LONG",
  "amount": 100,
  "leverage": 10,
  "sl_percent": 2,
  "tp_percent": 4
}
```
**Parameters:**
- `symbol`: Trading pair (e.g., "BTC/USDT", "ETH/USDT")
- `side`: "LONG" or "SHORT"
- `amount`: Position size in USDT
- `leverage`: Leverage multiplier (1-125)
- `sl_percent`: Stop loss percentage
- `tp_percent`: Take profit percentage

**Response:**
```json
{
  "ok": true,
  "position_id": 1,
  "symbol": "BTC/USDT",
  "side": "LONG",
  "amount": 100.0,
  "entry_price": 43500.0,
  "leverage": 10,
  "sl": 42630.0,
  "tp": 45240.0,
  "status": "filled"
}
```

### History & Analytics

#### Get Trades History
```http
GET /trades/history?limit=100
```
**Response:**
```json
{
  "trades": [
    {
      "id": 1,
      "symbol": "BTC/USDT",
      "side": "LONG",
      "amount": 100.0,
      "entry_price": 43500.0,
      "exit_price": 43600.0,
      "leverage": 10,
      "pnl": 100.0,
      "pnl_percent": 2.3,
      "closed_at": "2026-01-30 11:30:00"
    }
  ],
  "total": 1,
  "statistics": {
    "total_pnl": 100.0,
    "winning_trades": 1,
    "losing_trades": 0,
    "win_rate": 100.0
  }
}
```

#### Get Equity Data
```http
GET /equity?range=1D
```
**Parameters:**
- `range`: Time range - `1H`, `4H`, `1D`, `1W`, or `1M`

**Response:**
```json
{
  "range": "1D",
  "data": [
    {
      "timestamp": "2026-01-30T10:00:00",
      "equity": 10100.0,
      "balance": 10000.0,
      "unrealized_pnl": 100.0
    }
  ],
  "total_points": 20
}
```

### Configuration

#### Update Configuration
```http
POST /config/update
Content-Type: application/json

{
  "config": {
    "max_positions": 10,
    "default_leverage": 5,
    "risk_per_trade": 2.0
  }
}
```
**Response:**
```json
{
  "ok": true,
  "message": "Configuration updated successfully"
}
```

## WebSocket API

### Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
  console.log('Connected to RLdC Trading Bot');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};
```

### Message Types

#### Connection Confirmation
```json
{
  "type": "connected",
  "message": "Connected to RLdC Trading Bot",
  "timestamp": "2026-01-30T11:00:00"
}
```

#### Price Updates
```json
{
  "type": "price_update",
  "symbol": "BTC/USDT",
  "price": 43500.0,
  "timestamp": "2026-01-30T11:00:00"
}
```

#### Position Updates
```json
{
  "type": "new_position",
  "position_id": 1,
  "symbol": "BTC/USDT",
  "side": "LONG",
  "amount": 100.0,
  "entry_price": 43500.0,
  "leverage": 10
}
```

#### Position Closed
```json
{
  "type": "position_closed",
  "position_id": 1,
  "percent": 100,
  "pnl": 100.0
}
```

#### Position Modified
```json
{
  "type": "position_modified",
  "position_id": 1,
  "sl": 41000.0,
  "tp": 44000.0
}
```

#### Bot Status Change
```json
{
  "type": "bot_status",
  "status": "running",
  "started_at": "2026-01-30T11:00:00"
}
```

## Testing

Run the comprehensive test suite:
```bash
python test_api.py
```

This will test all endpoints and verify:
- ✅ Bot control (start, pause, stop)
- ✅ Position management (create, modify, close)
- ✅ Trading operations
- ✅ History and analytics
- ✅ Configuration updates
- ✅ All API responses

## Database

The server uses SQLite for persistent storage:
- **File**: `trading_bot.db`
- **Tables**:
  - `positions` - Open and closed positions
  - `trades_history` - Historical trade records
  - `equity_history` - Account equity over time

## Architecture

```
FastAPI Server (main.py)
├── REST API Endpoints
│   ├── Bot Control (/bot/*)
│   ├── Position Management (/positions/*)
│   ├── Trading (/trade/*)
│   └── Analytics (/equity, /trades/history)
├── WebSocket (/ws)
│   └── Real-time updates (prices, positions, status)
├── Database (SQLite)
│   ├── positions
│   ├── trades_history
│   └── equity_history
└── Binance Futures Client
    ├── Price fetching
    ├── Order placement
    └── Account balance
```

## Features

✅ **CORS Enabled** - Accessible from any origin  
✅ **Real-time Updates** - WebSocket for live data  
✅ **Persistent Storage** - SQLite database  
✅ **Comprehensive API** - All trading operations  
✅ **Interactive Docs** - Swagger UI and ReDoc  
✅ **Position Management** - Create, modify, close positions  
✅ **Risk Management** - Configurable SL/TP  
✅ **Analytics** - Trade history and equity charts  
✅ **Multi-timeframe** - 1H, 4H, 1D, 1W, 1M data  

## Security Notes

⚠️ **Important Security Considerations:**

1. **API Keys**: Store Binance API keys in `.env` file (never commit to git)
2. **CORS**: Currently allows all origins (`*`) - restrict in production
3. **Network**: Server binds to `0.0.0.0` for LAN access - use firewall rules
4. **Authentication**: No authentication implemented - add auth middleware for production
5. **Rate Limiting**: No rate limiting - add for production use

## Troubleshooting

### Server won't start
- Check if port 8000 is already in use: `lsof -i :8000`
- Verify dependencies are installed: `pip install -r requirements.txt`

### Database errors
- Delete and recreate: `rm trading_bot.db` then restart server
- Check file permissions

### WebSocket connection fails
- Verify server is running
- Check firewall settings
- Use correct WebSocket URL: `ws://` not `wss://`

## Support

For issues and questions:
- Check the Swagger documentation at `/docs`
- Review the test suite in `test_api.py`
- See the main README.md for general information
