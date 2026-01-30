# 🔌 FastAPI Gateway - Dokumentacja API

## Spis treści
- [Wprowadzenie](#wprowadzenie)
- [Uruchomienie](#uruchomienie)
- [Konfiguracja CORS](#konfiguracja-cors)
- [Endpointy GET](#endpointy-get)
- [Endpointy POST](#endpointy-post)
- [WebSocket](#websocket)
- [Integracja z Binance](#integracja-z-binance)
- [Przykłady użycia](#przykłady-użycia)

## Wprowadzenie

FastAPI Gateway to nowoczesna bramka REST API z obsługą WebSocket dla RLdC Trading Bot. Zapewnia:

- ✅ Pełną kontrolę nad botem tradingowym
- ✅ Zarządzanie pozycjami w czasie rzeczywistym
- ✅ Historię transakcji i equity
- ✅ WebSocket dla live updates
- ✅ Integrację z Binance Futures API
- ✅ Automatyczną dokumentację (Swagger UI)

## Uruchomienie

### Podstawowe uruchomienie

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Uruchomienie z auto-reload (development)

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Uruchomienie w tle (production)

```bash
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > api.log 2>&1 &
```

### Dostęp do dokumentacji

Po uruchomieniu serwera dostępne są:
- **API root:** http://localhost:8000/
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Konfiguracja CORS

CORS jest skonfigurowany zgodnie z wymaganiami:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # Wszystkie źródła
    allow_credentials=True,         # Credentials dozwolone
    allow_methods=["*"],            # Wszystkie metody HTTP
    allow_headers=["*"],            # Wszystkie nagłówki
)
```

## Endpointy GET

### GET /status

Zwraca aktualny status bota tradingowego.

**Odpowiedź:**
```json
{
    "bot_status": "running",
    "current_balance": 1000.0,
    "total_pnl": 125.0,
    "open_positions": 2,
    "total_trades": 5,
    "btc_price": 43000.0,
    "last_update": "2026-01-30T12:00:00"
}
```

**Przykład:**
```bash
curl http://localhost:8000/status
```

---

### GET /positions

Zwraca listę aktywnych pozycji.

**Odpowiedź:**
```json
{
    "positions": [
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
            "opened_at": "2026-01-30T10:00:00"
        }
    ],
    "count": 1
}
```

**Przykład:**
```bash
curl http://localhost:8000/positions
```

---

### GET /trades/history

Zwraca historię zamkniętych transakcji.

**Odpowiedź:**
```json
{
    "trades": [
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
            "opened_at": "2026-01-29T10:00:00",
            "closed_at": "2026-01-29T18:00:00",
            "status": "closed"
        }
    ],
    "count": 1
}
```

**Przykład:**
```bash
curl http://localhost:8000/trades/history
```

---

### GET /equity

Zwraca historię equity w zadanym przedziale czasowym.

**Parametry:**
- `range` - Zakres czasowy: `1H`, `4H`, `1D`, `1W`, `1M`

**Odpowiedź:**
```json
{
    "range": "1D",
    "data": [
        {
            "timestamp": "2026-01-29T12:00:00",
            "equity": 1366.53
        },
        {
            "timestamp": "2026-01-29T13:00:00",
            "equity": 1406.97
        }
    ],
    "count": 24,
    "current_equity": 1125.0
}
```

**Przykłady:**
```bash
# Equity z ostatniej godziny
curl http://localhost:8000/equity?range=1H

# Equity z ostatniego dnia
curl http://localhost:8000/equity?range=1D

# Equity z ostatniego tygodnia
curl http://localhost:8000/equity?range=1W
```

---

## Endpointy POST

### POST /bot/start

Uruchamia bota tradingowego.

**Odpowiedź:**
```json
{
    "status": "success",
    "message": "Bot uruchomiony",
    "bot_status": "running"
}
```

**Przykład:**
```bash
curl -X POST http://localhost:8000/bot/start
```

---

### POST /bot/pause

Wstrzymuje działanie bota (nie zamyka pozycji).

**Odpowiedź:**
```json
{
    "status": "success",
    "message": "Bot wstrzymany",
    "bot_status": "paused"
}
```

**Przykład:**
```bash
curl -X POST http://localhost:8000/bot/pause
```

---

### POST /bot/stop

Zatrzymuje bota tradingowego.

**Odpowiedź:**
```json
{
    "status": "success",
    "message": "Bot zatrzymany",
    "bot_status": "stopped"
}
```

**Przykład:**
```bash
curl -X POST http://localhost:8000/bot/stop
```

---

### POST /positions/{id}/close

Zamyka pozycję całkowicie lub częściowo.

**Body:**
```json
{
    "percent": 100
}
```

**Parametry:**
- `percent` - Procent pozycji do zamknięcia (1-100)

**Odpowiedź:**
```json
{
    "status": "success",
    "message": "Pozycja 1 zamknięta w 100%",
    "pnl": 75.0
}
```

**Przykłady:**
```bash
# Zamknięcie całej pozycji
curl -X POST http://localhost:8000/positions/1/close \
  -H "Content-Type: application/json" \
  -d '{"percent": 100}'

# Zamknięcie 50% pozycji
curl -X POST http://localhost:8000/positions/1/close \
  -H "Content-Type: application/json" \
  -d '{"percent": 50}'
```

---

### POST /positions/{id}/modify

Modyfikuje stop-loss i take-profit pozycji.

**Body:**
```json
{
    "sl": 41500.0,
    "tp": 45000.0
}
```

**Parametry:**
- `sl` (opcjonalny) - Nowy poziom stop-loss
- `tp` (opcjonalny) - Nowy poziom take-profit

**Odpowiedź:**
```json
{
    "status": "success",
    "message": "Pozycja 1 zmodyfikowana",
    "position": {
        "id": 1,
        "symbol": "BTC/USDT",
        "sl": 41500.0,
        "tp": 45000.0,
        ...
    }
}
```

**Przykłady:**
```bash
# Zmiana SL i TP
curl -X POST http://localhost:8000/positions/1/modify \
  -H "Content-Type: application/json" \
  -d '{"sl": 41500, "tp": 45000}'

# Zmiana tylko SL
curl -X POST http://localhost:8000/positions/1/modify \
  -H "Content-Type: application/json" \
  -d '{"sl": 41500}'
```

---

### POST /trade/quick

Szybkie otwarcie nowej pozycji.

**Body:**
```json
{
    "symbol": "BTC/USDT",
    "side": "LONG",
    "amount": 0.01,
    "leverage": 10,
    "sl_percent": 2.0,
    "tp_percent": 4.0
}
```

**Parametry:**
- `symbol` - Para walutowa (np. "BTC/USDT")
- `side` - Kierunek: "LONG" lub "SHORT"
- `amount` - Ilość
- `leverage` - Dźwignia (domyślnie 1)
- `sl_percent` (opcjonalny) - Stop-loss w procentach
- `tp_percent` (opcjonalny) - Take-profit w procentach

**Odpowiedź:**
```json
{
    "status": "success",
    "message": "Pozycja otwarta",
    "position": {
        "id": 3,
        "symbol": "BTC/USDT",
        "side": "LONG",
        "amount": 0.01,
        "entry_price": 43000.0,
        "leverage": 10,
        "sl": 42140.0,
        "tp": 44720.0,
        ...
    }
}
```

**Przykład:**
```bash
curl -X POST http://localhost:8000/trade/quick \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTC/USDT",
    "side": "LONG",
    "amount": 0.01,
    "leverage": 10,
    "sl_percent": 2,
    "tp_percent": 4
  }'
```

---

### POST /config/update

Aktualizuje konfigurację bota.

**Body:**
```json
{
    "updates": {
        "START_BALANCE": 2000,
        "STOP_LOSS": 0.03
    }
}
```

**Odpowiedź:**
```json
{
    "status": "success",
    "message": "Konfiguracja zaktualizowana",
    "config": {
        "START_BALANCE": 2000,
        "STOP_LOSS": 0.03,
        ...
    }
}
```

**Przykład:**
```bash
curl -X POST http://localhost:8000/config/update \
  -H "Content-Type: application/json" \
  -d '{"updates": {"START_BALANCE": 2000}}'
```

---

## WebSocket

WebSocket endpoint `/ws` zapewnia real-time updates.

### Połączenie

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
    console.log('Połączono z RLdC Trading Bot');
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Otrzymano:', data);
};

ws.onerror = (error) => {
    console.error('WebSocket error:', error);
};

ws.onclose = () => {
    console.log('Połączenie zamknięte');
};
```

### Typy wiadomości

#### Wiadomość powitalna (automatyczna)
```json
{
    "type": "connected",
    "message": "Połączono z RLdC Trading Bot WebSocket",
    "timestamp": "2026-01-30T12:00:00"
}
```

#### Ping/Pong
```javascript
// Wysłanie ping
ws.send(JSON.stringify({ type: 'ping' }));

// Odpowiedź
{
    "type": "pong",
    "timestamp": "2026-01-30T12:00:00"
}
```

#### Subskrypcja ticków cenowych
```javascript
// Subskrypcja
ws.send(JSON.stringify({
    type: 'subscribe',
    symbol: 'BTC/USDT'
}));

// Odpowiedź
{
    "type": "tick",
    "symbol": "BTC/USDT",
    "price": 43000.0,
    "timestamp": "2026-01-30T12:00:00"
}
```

#### Market updates (automatyczne co 5 sekund)
```json
{
    "type": "market_update",
    "positions": [
        {
            "id": 1,
            "symbol": "BTC/USDT",
            "pnl": 75.0,
            ...
        }
    ],
    "bot_status": "running",
    "timestamp": "2026-01-30T12:00:00"
}
```

#### Zdarzenia pozycji
```json
// Pozycja otwarta
{
    "type": "position_opened",
    "position": { ... }
}

// Pozycja zamknięta
{
    "type": "position_closed",
    "position_id": 1,
    "pnl": 75.0
}

// Pozycja zmodyfikowana
{
    "type": "position_modified",
    "position_id": 1,
    "sl": 41500.0,
    "tp": 45000.0
}
```

#### Zmiany statusu bota
```json
{
    "type": "bot_status",
    "status": "running"
}
```

### Przykład klienta Python

```python
import asyncio
import websockets
import json

async def trading_bot_client():
    uri = "ws://localhost:8000/ws"
    async with websockets.connect(uri) as websocket:
        # Odbierz wiadomość powitalną
        welcome = await websocket.recv()
        print(f"Otrzymano: {welcome}")
        
        # Subskrybuj BTC/USDT
        await websocket.send(json.dumps({
            'type': 'subscribe',
            'symbol': 'BTC/USDT'
        }))
        
        # Nasłuchuj wiadomości
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            
            if data['type'] == 'market_update':
                print(f"Market update: {len(data['positions'])} pozycji")
            elif data['type'] == 'tick':
                print(f"{data['symbol']}: {data['price']}")
            else:
                print(f"Otrzymano: {data}")

asyncio.run(trading_bot_client())
```

## Integracja z Binance

API automatycznie próbuje pobrać realne dane z Binance Futures API, jeśli są dostępne klucze w `config.json`.

### Konfiguracja

Dodaj do `config.json`:
```json
{
    "BINANCE_API_KEY": "twoj_klucz_api",
    "BINANCE_API_SECRET": "twoj_sekret_api"
}
```

### Pobieranie realnych cen

```python
# W main.py
def get_binance_price(symbol: str) -> Optional[float]:
    """Pobiera aktualną cenę z Binance API"""
    if not binance_client:
        return None
    
    try:
        binance_symbol = symbol.replace("/", "")
        ticker = binance_client.get_symbol_ticker(symbol=binance_symbol)
        return float(ticker['price'])
    except Exception as e:
        print(f"⚠️ Błąd pobierania ceny: {e}")
        return None
```

Jeśli brak połączenia z Binance, API używa przykładowych cen jako fallback.

## Przykłady użycia

### Dashboard handlowy

```javascript
// Pobierz status co 5 sekund
setInterval(async () => {
    const response = await fetch('http://localhost:8000/status');
    const data = await response.json();
    
    document.getElementById('balance').textContent = data.current_balance;
    document.getElementById('pnl').textContent = data.total_pnl;
    document.getElementById('positions').textContent = data.open_positions;
}, 5000);

// WebSocket dla live updates
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.type === 'market_update') {
        updatePositionsTable(data.positions);
    }
};
```

### Bot automatyczny

```python
import requests
import time

API_URL = "http://localhost:8000"

# Uruchom bota
response = requests.post(f"{API_URL}/bot/start")
print(response.json())

# Monitoruj pozycje
while True:
    positions = requests.get(f"{API_URL}/positions").json()
    
    for pos in positions['positions']:
        # Zamknij zyskowne pozycje powyżej 5%
        if pos['pnl_percent'] > 5:
            requests.post(
                f"{API_URL}/positions/{pos['id']}/close",
                json={'percent': 100}
            )
            print(f"Zamknięto pozycję {pos['id']} z zyskiem {pos['pnl']}")
    
    time.sleep(10)
```

### Trading bot z strategią

```python
import requests

API_URL = "http://localhost:8000"

def check_signals():
    """Sprawdź sygnały z własnej strategii"""
    # Tutaj logika strategii
    return "BTC/USDT", "LONG"

def open_position(symbol, side):
    """Otwórz pozycję"""
    response = requests.post(
        f"{API_URL}/trade/quick",
        json={
            "symbol": symbol,
            "side": side,
            "amount": 0.01,
            "leverage": 10,
            "sl_percent": 2,
            "tp_percent": 4
        }
    )
    return response.json()

# Główna pętla
while True:
    symbol, side = check_signals()
    if side:
        result = open_position(symbol, side)
        print(f"Otwarto pozycję: {result}")
    time.sleep(60)
```

---

## Kody błędów

- `404` - Nie znaleziono zasobu (np. pozycja o podanym ID)
- `400` - Nieprawidłowe parametry zapytania
- `500` - Błąd wewnętrzny serwera

## Wsparcie

W razie problemów:
1. Sprawdź logi serwera
2. Zweryfikuj konfigurację w `config.json`
3. Upewnij się, że Binance API jest prawidłowo skonfigurowany
4. Zobacz dokumentację Swagger UI pod `/docs`

---

**Wersja:** 1.0.0  
**Data:** 2026-01-30  
**Autor:** RLdC Trading Bot Team
