#!/bin/bash

# Skrypt startowy dla FastAPI Gateway
# RLdC Trading Bot

echo "================================================"
echo "🚀 RLdC Trading Bot - FastAPI Gateway"
echo "================================================"
echo ""

# Sprawdź czy Python jest zainstalowany
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 nie jest zainstalowany!"
    echo "Zainstaluj Python 3: sudo apt install python3"
    exit 1
fi

# Sprawdź czy uvicorn jest zainstalowany
if ! python3 -c "import uvicorn" 2>/dev/null; then
    echo "⚠️  Uvicorn nie jest zainstalowany!"
    echo "Instaluję zależności..."
    pip install -r requirements.txt
fi

# Sprawdź czy config.json istnieje
if [ ! -f "config.json" ]; then
    echo "⚠️  Brak pliku config.json"
    echo "Tworzę domyślną konfigurację..."
    python3 config_manager.py
fi

echo ""
echo "✅ Wszystko gotowe!"
echo ""
echo "📊 Uruchamianie FastAPI Gateway..."
echo ""
echo "🌐 API będzie dostępny pod:"
echo "   - Root API: http://localhost:8000/"
echo "   - Swagger UI: http://localhost:8000/docs"
echo "   - ReDoc: http://localhost:8000/redoc"
echo "   - WebSocket: ws://localhost:8000/ws"
echo ""
echo "💡 Aby zatrzymać serwer, użyj Ctrl+C"
echo ""
echo "================================================"
echo ""

# Uruchom serwer
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
