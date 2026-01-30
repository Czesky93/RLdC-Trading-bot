#!/bin/bash
# Startup script for RLdC Trading Bot FastAPI Gateway

echo "🚀 Starting RLdC Trading Bot FastAPI Gateway..."

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
fi

# Check if dependencies are installed
if ! python -c "import fastapi" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -r requirements.txt
fi

# Check for config files
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "⚠️  .env file not found. Copying from .env.example..."
        echo "   Please update .env with your Binance API keys!"
        cp .env.example .env
    fi
fi

# Start the server
echo "✅ Starting server on http://0.0.0.0:8000"
echo "📊 API Documentation: http://0.0.0.0:8000/docs"
echo "📡 WebSocket endpoint: ws://0.0.0.0:8000/ws"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

uvicorn main:app --host 0.0.0.0 --port 8000 --reload
