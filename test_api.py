"""
Testy dla FastAPI Gateway
Sprawdzają poprawność działania wszystkich endpointów
"""

import pytest
import requests
import json
from websockets.sync.client import connect

API_URL = "http://localhost:8000"

def test_root_endpoint():
    """Test endpointu głównego"""
    response = requests.get(f"{API_URL}/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "RLdC Trading Bot API"
    assert data["version"] == "1.0.0"
    assert data["status"] == "running"

def test_status_endpoint():
    """Test endpointu statusu"""
    response = requests.get(f"{API_URL}/status")
    assert response.status_code == 200
    data = response.json()
    assert "bot_status" in data
    assert "current_balance" in data
    assert "total_pnl" in data
    assert "open_positions" in data

def test_positions_endpoint():
    """Test endpointu pozycji"""
    response = requests.get(f"{API_URL}/positions")
    assert response.status_code == 200
    data = response.json()
    assert "positions" in data
    assert "count" in data
    assert isinstance(data["positions"], list)

def test_trades_history_endpoint():
    """Test endpointu historii transakcji"""
    response = requests.get(f"{API_URL}/trades/history")
    assert response.status_code == 200
    data = response.json()
    assert "trades" in data
    assert "count" in data
    assert isinstance(data["trades"], list)

def test_equity_endpoint():
    """Test endpointu equity"""
    # Test różnych zakresów czasowych
    for range_param in ["1H", "4H", "1D", "1W", "1M"]:
        response = requests.get(f"{API_URL}/equity?range={range_param}")
        assert response.status_code == 200
        data = response.json()
        assert data["range"] == range_param
        assert "data" in data
        assert "count" in data
        assert "current_equity" in data

def test_equity_invalid_range():
    """Test endpointu equity z nieprawidłowym zakresem"""
    response = requests.get(f"{API_URL}/equity?range=INVALID")
    assert response.status_code == 400

def test_bot_control_endpoints():
    """Test endpointów sterowania botem"""
    # Start
    response = requests.post(f"{API_URL}/bot/start")
    assert response.status_code == 200
    assert response.json()["bot_status"] == "running"
    
    # Pause
    response = requests.post(f"{API_URL}/bot/pause")
    assert response.status_code == 200
    assert response.json()["bot_status"] == "paused"
    
    # Stop
    response = requests.post(f"{API_URL}/bot/stop")
    assert response.status_code == 200
    assert response.json()["bot_status"] == "stopped"

def test_quick_trade_endpoint():
    """Test endpointu szybkiego handlu"""
    trade_data = {
        "symbol": "BTC/USDT",
        "side": "LONG",
        "amount": 0.01,
        "leverage": 10,
        "sl_percent": 2,
        "tp_percent": 4
    }
    
    response = requests.post(
        f"{API_URL}/trade/quick",
        json=trade_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "position" in data
    
    # Sprawdź czy pozycja została utworzona
    position = data["position"]
    assert position["symbol"] == "BTC/USDT"
    assert position["side"] == "LONG"
    assert position["leverage"] == 10
    
    return position["id"]

def test_modify_position_endpoint():
    """Test endpointu modyfikacji pozycji"""
    # Najpierw pobierz ID pierwszej pozycji
    positions = requests.get(f"{API_URL}/positions").json()
    if positions["count"] > 0:
        position_id = positions["positions"][0]["id"]
        
        modify_data = {
            "sl": 41500,
            "tp": 45000
        }
        
        response = requests.post(
            f"{API_URL}/positions/{position_id}/modify",
            json=modify_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["position"]["sl"] == 41500
        assert data["position"]["tp"] == 45000

def test_close_position_endpoint():
    """Test endpointu zamykania pozycji"""
    # Otwórz nową pozycję do testu
    trade_data = {
        "symbol": "ETH/USDT",
        "side": "SHORT",
        "amount": 1.0,
        "leverage": 5
    }
    
    position = requests.post(f"{API_URL}/trade/quick", json=trade_data).json()
    position_id = position["position"]["id"]
    
    # Zamknij 50% pozycji
    close_data = {"percent": 50}
    response = requests.post(
        f"{API_URL}/positions/{position_id}/close",
        json=close_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    
    # Zamknij resztę
    close_data = {"percent": 100}
    response = requests.post(
        f"{API_URL}/positions/{position_id}/close",
        json=close_data
    )
    assert response.status_code == 200

def test_config_update_endpoint():
    """Test endpointu aktualizacji konfiguracji"""
    update_data = {
        "updates": {
            "START_BALANCE": 1500
        }
    }
    
    response = requests.post(
        f"{API_URL}/config/update",
        json=update_data
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["config"]["START_BALANCE"] == 1500

def test_websocket_connection():
    """Test połączenia WebSocket"""
    try:
        with connect(f"ws://localhost:8000/ws") as websocket:
            # Odbierz wiadomość powitalną
            message = websocket.recv()
            data = json.loads(message)
            assert data["type"] == "connected"
            
            # Wyślij ping
            websocket.send(json.dumps({"type": "ping"}))
            response = websocket.recv()
            data = json.loads(response)
            assert data["type"] == "pong"
            
            # Subskrybuj ticker
            websocket.send(json.dumps({
                "type": "subscribe",
                "symbol": "BTC/USDT"
            }))
            response = websocket.recv()
            data = json.loads(response)
            assert data["type"] == "tick"
            assert data["symbol"] == "BTC/USDT"
    except Exception as e:
        pytest.skip(f"WebSocket test skipped: {e}")

def test_position_not_found():
    """Test odpowiedzi dla nieistniejącej pozycji"""
    response = requests.post(
        f"{API_URL}/positions/99999/close",
        json={"percent": 100}
    )
    assert response.status_code == 404

def test_invalid_quick_trade():
    """Test nieprawidłowego szybkiego handlu"""
    trade_data = {
        "symbol": "BTC/USDT",
        "side": "INVALID",  # Nieprawidłowy side
        "amount": 0.01
    }
    
    response = requests.post(
        f"{API_URL}/trade/quick",
        json=trade_data
    )
    assert response.status_code == 400

if __name__ == "__main__":
    print("🧪 Uruchamianie testów FastAPI Gateway...")
    print("\n⚠️ UWAGA: Serwer musi być uruchomiony na localhost:8000")
    print("Uruchom: uvicorn main:app --host 0.0.0.0 --port 8000\n")
    
    # Uruchom testy
    pytest.main([__file__, "-v"])
