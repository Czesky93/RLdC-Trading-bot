# RLdC Trading Bot - FastAPI Gateway Server

A comprehensive FastAPI Gateway server for the RLdC Trading Bot application with Binance Futures API integration.

## Features

- **REST API**: Complete set of endpoints for bot control and monitoring
- **WebSocket**: Real-time updates for positions, trades, and alerts
- **State Management**: SQLite persistence with in-memory caching
- **Binance Integration**: Ready for Binance Futures API integration
- **LAN Access**: Runs on 0.0.0.0:8000 for network-wide access

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python gateway_server.py
```

The server will start on `http://0.0.0.0:8000`

## API Documentation

Once the server is running, visit:
- **Interactive API docs**: http://localhost:8000/docs
- **Alternative docs**: http://localhost:8000/redoc

## API Endpoints

### Bot Status
- **GET** `/status` - Get current bot status
  - Returns: state, balance, equity, PnL metrics, uptime

### Positions
- **GET** `/positions` - List all open positions
- **POST** `/positions/{id}/close` - Close a position
  - Body: `{"percent": 100.0}` (0-100, default 100)
- **POST** `/positions/{id}/modify` - Modify position SL/TP
  - Body: `{"sl": 48500.0, "tp": 53000.0}`

### Trades
- **GET** `/trades/history` - Get closed trades history

### Equity
- **GET** `/equity` - Get equity curve data
  - Query param: `range` (1H, 4H, 1D, 1W, 1M)
  - Example: `/equity?range=1D`

### Bot Control
- **POST** `/bot/start` - Start the bot
- **POST** `/bot/pause` - Pause the bot
- **POST** `/bot/stop` - Stop the bot

### Configuration
- **POST** `/config/update` - Update bot configuration
  - Body: `{"kelly": 0.35, "atr": {"period": 20, "multiplier": 2.5}, "hedge": {"enabled": true, "ratio": 0.5}}`

### Quick Trade
- **POST** `/trade/quick` - Execute a quick trade
  - Body:
  ```json
  {
    "symbol": "BTCUSDT",
    "side": "LONG",
    "amount": 0.01,
    "leverage": 10,
    "sl_percent": 2,
    "tp_percent": 5
  }
  ```

### WebSocket
- **WebSocket** `/ws` - Real-time updates
  - Connects and sends periodic status updates
  - Broadcasts position changes, alerts, and ticks

### Health Check
- **GET** `/health` - Server health status

## Usage Examples

### Check Bot Status
```bash
curl http://localhost:8000/status
```

### Create a Quick Trade
```bash
curl -X POST http://localhost:8000/trade/quick \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTCUSDT",
    "side": "LONG",
    "amount": 0.01,
    "leverage": 10,
    "sl_percent": 2,
    "tp_percent": 5
  }'
```

### Modify Position
```bash
curl -X POST http://localhost:8000/positions/pos_1/modify \
  -H "Content-Type: application/json" \
  -d '{"sl": 48500.0, "tp": 53000.0}'
```

### Close Position (Partial)
```bash
curl -X POST http://localhost:8000/positions/pos_1/close \
  -H "Content-Type: application/json" \
  -d '{"percent": 50}'
```

### WebSocket Connection (Python)
```python
import asyncio
import websockets
import json

async def connect():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Received: {data}")

asyncio.run(connect())
```

## Data Models

### BotStatus
- `state`: RUN/PAUSE/ERROR
- `balance`: Current balance
- `equity`: Current equity (balance + unrealized PnL)
- `pnl`: Total unrealized PnL
- `pnlPercent`: PnL percentage
- `openPositions`: Number of open positions
- `dailyPnl`: PnL for last 24 hours
- `weeklyPnl`: PnL for last 7 days
- `monthlyPnl`: PnL for last 30 days
- `drawdown`: Current drawdown percentage
- `uptime`: Bot uptime in seconds

### Position
- `id`: Unique position identifier
- `symbol`: Trading pair (e.g., BTCUSDT)
- `side`: LONG or SHORT
- `entryPrice`: Entry price
- `currentPrice`: Current market price
- `quantity`: Position size
- `leverage`: Leverage multiplier (1-125)
- `pnl`: Unrealized profit/loss
- `pnlPercent`: PnL percentage
- `sl`: Stop loss price (optional)
- `tp`: Take profit price (optional)
- `openedAt`: Position open timestamp

### Trade
- All Position fields plus:
- `exitPrice`: Exit price
- `closedAt`: Trade close timestamp

## State Management

The server uses primarily in-memory state management for fast access:
- **In-memory**: Fast access to current state (positions, trades, equity, config)
- **SQLite**: Database schema prepared for future persistence implementation

**Note**: Current implementation stores all data in memory. Data will be lost on server restart.
Database persistence is planned for future releases.

Database file: `trading_bot.db` (schema created automatically)

## Configuration

Default configuration includes:
- Kelly criterion: 0.25
- ATR settings: period 14, multiplier 2.0
- Hedge settings: disabled by default

Update via `/config/update` endpoint.

## Development

### Running in Development
```bash
uvicorn gateway_server:app --reload --host 0.0.0.0 --port 8000
```

### Running with Custom Port
```python
# Edit gateway_server.py, change the last line:
uvicorn.run(app, host="0.0.0.0", port=8080)
```

## Production Deployment

For production use with multiple workers:
```bash
gunicorn gateway_server:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## Security Notes

⚠️ **IMPORTANT SECURITY WARNINGS**:
- The server currently has NO authentication/authorization
- CORS is enabled for all origins (development mode)
- All API endpoints are publicly accessible

**For Production Use**:
1. Implement authentication middleware (JWT, OAuth2, API keys)
2. Restrict CORS origins in the middleware configuration
3. Use HTTPS/TLS in production environments
4. Consider IP whitelisting for API access
5. Add rate limiting to prevent abuse
6. Never expose this API directly to the internet without proper security

**Recommended**: Run behind a reverse proxy (nginx, Caddy) with authentication.

## License

See main repository for license information.
