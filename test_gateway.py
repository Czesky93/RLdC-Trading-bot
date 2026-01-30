#!/usr/bin/env python3
"""
Integration test for Gateway Server
Tests all endpoints to ensure they work correctly
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"


def test_endpoint(method, endpoint, data=None, expected_status=200):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        success = response.status_code == expected_status
        status_symbol = "✓" if success else "✗"
        
        print(f"{status_symbol} {method} {endpoint} - Status: {response.status_code}")
        
        if not success:
            print(f"  Expected: {expected_status}, Got: {response.status_code}")
            print(f"  Response: {response.text[:200]}")
        
        return success, response
    except requests.exceptions.RequestException as e:
        print(f"✗ {method} {endpoint} - Error: {e}")
        return False, None


def main():
    print("=" * 60)
    print("RLdC Trading Bot Gateway - Integration Tests")
    print("=" * 60)
    print()
    
    # Check if server is running
    try:
        requests.get(f"{BASE_URL}/health", timeout=2)
        print("✓ Server is running\n")
    except requests.exceptions.RequestException:
        print("✗ Server is not running!")
        print("Please start the gateway server first:")
        print("  python gateway_server.py")
        sys.exit(1)
    
    results = []
    
    # Test basic endpoints
    print("Testing Basic Endpoints:")
    results.append(test_endpoint("GET", "/"))
    results.append(test_endpoint("GET", "/health"))
    results.append(test_endpoint("GET", "/status"))
    print()
    
    # Test positions endpoints
    print("Testing Position Endpoints:")
    results.append(test_endpoint("GET", "/positions"))
    
    # Create a quick trade
    trade_data = {
        "symbol": "BTCUSDT",
        "side": "LONG",
        "amount": 0.01,
        "leverage": 10,
        "sl_percent": 2,
        "tp_percent": 5
    }
    success, response = test_endpoint("POST", "/trade/quick", trade_data)
    results.append((success, response))
    
    if success and response:
        position = response.json()
        position_id = position['id']
        print(f"  Created position: {position_id}")
        
        # Test modify position
        modify_data = {"sl": 48500.0, "tp": 53000.0}
        results.append(test_endpoint("POST", f"/positions/{position_id}/modify", modify_data))
        
        # Test partial close
        close_data = {"percent": 50.0}
        results.append(test_endpoint("POST", f"/positions/{position_id}/close", close_data))
        
        # Test full close
        close_data = {"percent": 100.0}
        results.append(test_endpoint("POST", f"/positions/{position_id}/close", close_data))
    print()
    
    # Test trade history
    print("Testing Trade History:")
    results.append(test_endpoint("GET", "/trades/history"))
    print()
    
    # Test equity endpoint
    print("Testing Equity Endpoint:")
    for time_range in ["1H", "4H", "1D", "1W", "1M"]:
        results.append(test_endpoint("GET", f"/equity?range={time_range}"))
    print()
    
    # Test bot control
    print("Testing Bot Control:")
    results.append(test_endpoint("POST", "/bot/start"))
    time.sleep(0.5)
    results.append(test_endpoint("POST", "/bot/pause"))
    time.sleep(0.5)
    results.append(test_endpoint("POST", "/bot/stop"))
    print()
    
    # Test config update
    print("Testing Configuration:")
    config_data = {
        "kelly": 0.35,
        "atr": {"period": 20, "multiplier": 2.5},
        "hedge": {"enabled": True, "ratio": 0.6}
    }
    results.append(test_endpoint("POST", "/config/update", config_data))
    print()
    
    # Summary
    print("=" * 60)
    passed = sum(1 for r in results if r[0])
    total = len(results)
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"Results: {passed}/{total} tests passed ({success_rate:.1f}%)")
    
    if passed == total:
        print("✓ All tests passed!")
        return 0
    else:
        print("✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
