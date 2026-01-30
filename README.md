# 🚀 RLdC Trading Bot - Ultimate AI

**Najbardziej zaawansowany bot tradingowy, który kiedykolwiek powstał.**  
Zawiera Quantum AI, Deep RL, Blockchain Analysis, AI Predictive Trading i HFT.

## 🌟 Funkcje
✅ **AI Trading** - Autonomiczna sztuczna inteligencja przewidująca rynki  
✅ **Quantum Optimization** - Kwantowa optymalizacja strategii handlowych  
✅ **Ultimate AI** - AI Wizjoner przewidujący ruchy rynkowe i geopolityczne  
✅ **High-Frequency Trading** - Ultra-szybkie algorytmy tradingowe  
✅ **Blockchain Analysis** - Śledzenie transakcji i anomalii rynkowych  
✅ **Telegram AI** - Sterowanie botem i analiza rynku z poziomu Telegrama  
✅ **Futurystyczny Portal WWW** - Pełne zarządzanie AI z poziomu przeglądarki  

## 📦 Instalacja
```bash
unzip RLdC_Trading_Bot_Installer.zip -d RLdC_Trading_Bot
cd RLdC_Trading_Bot
python installer.py
```

📖 **Szczegółowa instrukcja uruchomienia na Ubuntu** znajduje się w `docs/SETUP_UBUNTU.md`.

## 🌐 Dostęp do systemu
🔹 **FastAPI Gateway (REST API + WebSocket):** 🌐 `http://localhost:8000/`  
🔹 **Dokumentacja API (Swagger):** 🌐 `http://localhost:8000/docs`  
🔹 **Futurystyczny Portal AI:** 🌐 `http://localhost:5004/`  
🔹 **Konfiguracja AI i Strategii:** 🌐 `http://localhost:5003/`  
🔹 **Zordon AI (Interaktywna Wizja AI):** 🌐 `http://localhost:5005/`  
🔹 **ULTIMATE AI (Przewidywanie przyszłości rynków):** 🌐 `http://localhost:5006/`  

## 🚀 Uruchomienie ręczne

### FastAPI Gateway (Główna bramka API)
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Dostępne endpointy:**
- 📊 `GET /status` - Status bota i aktualny stan
- 📈 `GET /positions` - Lista aktywnych pozycji
- 📜 `GET /trades/history` - Historia zamkniętych transakcji
- 💰 `GET /equity?range=1D` - Historia equity (1H, 4H, 1D, 1W, 1M)
- ✂️ `POST /positions/{id}/close` - Zamknięcie pozycji
- ⚙️ `POST /positions/{id}/modify` - Modyfikacja SL/TP
- ▶️ `POST /bot/start` - Uruchomienie bota
- ⏸️ `POST /bot/pause` - Wstrzymanie bota
- ⏹️ `POST /bot/stop` - Zatrzymanie bota
- 🔧 `POST /config/update` - Aktualizacja konfiguracji
- ⚡ `POST /trade/quick` - Szybkie otwarcie pozycji
- 🔌 `WebSocket /ws` - Real-time updates (ticki, pozycje, alerty)

### Pozostałe moduły
```bash
python master_ai_trader.py &
python web_portal.py &
python ai_optimizer.py &
python rldc_quantum_ai.py &
python demo_trading.py &
python telegram_ai_bot.py &
python zordon_ai.py &
python ultimate_ai.py &
```

## 🎯 Cel projektu
Zbudowanie **najpotężniejszej AI tradingowej na świecie** – przewidującej rynki, uczącej się, optymalizującej strategie i przekraczającej granice możliwości.

## 🔌 FastAPI Gateway - REST API i WebSocket

FastAPI Gateway to nowoczesna bramka REST API z obsługą WebSocket, zapewniająca:
- ✅ **CORS** skonfigurowany dla wszystkich źródeł
- ✅ **Integracja z Binance Futures API** dla realnych danych rynkowych
- ✅ **WebSocket** do real-time updates (ticki, pozycje, alerty)
- ✅ **Automatyczna dokumentacja** dostępna pod `/docs`
- ✅ **Stan w pamięci** (pozycje, equity, historia transakcji)

### Szybki start:
```bash
# Instalacja zależności
pip install -r requirements.txt

# Uruchomienie serwera
uvicorn main:app --host 0.0.0.0 --port 8000

# Dokumentacja API
# Otwórz w przeglądarce: http://localhost:8000/docs
```

### Przykładowe zapytania:

```bash
# Sprawdzenie statusu bota
curl http://localhost:8000/status

# Pobranie aktywnych pozycji
curl http://localhost:8000/positions

# Uruchomienie bota
curl -X POST http://localhost:8000/bot/start

# Szybkie otwarcie pozycji LONG na BTC
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

# Zamknięcie pozycji
curl -X POST http://localhost:8000/positions/1/close \
  -H "Content-Type: application/json" \
  -d '{"percent": 100}'
```

### WebSocket (real-time):
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
    console.log('Połączono z RLdC Trading Bot');
    
    // Subskrypcja ticków BTC
    ws.send(JSON.stringify({
        type: 'subscribe',
        symbol: 'BTC/USDT'
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Otrzymano:', data);
};
```
