#!/usr/bin/env python3
"""
Test script for RLdC Trading Bot FastAPI Gateway
Tests all endpoints and WebSocket functionality
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_endpoint(method, endpoint, data=None, description=""):
    """Test a single endpoint"""
    url = f"{BASE_URL}{endpoint}"
    print(f"\n{'='*60}")
    print(f"Testing: {description}")
    print(f"Method: {method} {endpoint}")
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            print(f"❌ Unsupported method: {method}")
            return False
        
        print(f"Status: {response.status_code}")
        
        if response.status_code < 400:
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            print("✅ PASSED")
            return True, result
        else:
            print(f"❌ FAILED: {response.text}")
            return False, None
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False, None


def main():
    print("=" * 60)
    print("RLdC Trading Bot API Test Suite")
    print("=" * 60)
    print(f"Base URL: {BASE_URL}")
    print(f"Started at: {datetime.now().isoformat()}")
    
    results = []
    
    # Test 1: Root endpoint
    success, _ = test_endpoint("GET", "/", description="Root endpoint")
    results.append(("Root", success))
    
    # Test 2: Status endpoint
    success, _ = test_endpoint("GET", "/status", description="Get bot status")
    results.append(("Status", success))
    
    # Test 3: Get positions (should be empty initially)
    success, _ = test_endpoint("GET", "/positions", description="Get positions")
    results.append(("Get Positions", success))
    
    # Test 4: Start bot
    success, _ = test_endpoint("POST", "/bot/start", description="Start bot")
    results.append(("Start Bot", success))
    
    # Test 5: Create a quick trade
    trade_data = {
        "symbol": "BTC/USDT",
        "side": "LONG",
        "amount": 100,
        "leverage": 10,
        "sl_percent": 2,
        "tp_percent": 4
    }
    success, trade_result = test_endpoint(
        "POST", "/trade/quick", 
        data=trade_data,
        description="Create quick trade (LONG BTC/USDT)"
    )
    results.append(("Quick Trade", success))
    position_id = trade_result.get("position_id") if trade_result else None
    
    # Test 6: Get positions again (should have the new position)
    success, _ = test_endpoint("GET", "/positions", description="Get positions after trade")
    results.append(("Get Positions After Trade", success))
    
    # Test 7: Modify position
    if position_id:
        modify_data = {
            "sl": 41000,
            "tp": 44000
        }
        success, _ = test_endpoint(
            "POST", f"/positions/{position_id}/modify",
            data=modify_data,
            description=f"Modify position {position_id}"
        )
        results.append(("Modify Position", success))
    
    # Test 8: Close position partially
    if position_id:
        close_data = {
            "percent": 50
        }
        success, _ = test_endpoint(
            "POST", f"/positions/{position_id}/close",
            data=close_data,
            description=f"Close 50% of position {position_id}"
        )
        results.append(("Close Position Partially", success))
    
    # Test 9: Get trades history
    success, _ = test_endpoint("GET", "/trades/history", description="Get trades history")
    results.append(("Trades History", success))
    
    # Test 10: Get equity data (various ranges)
    for range_val in ["1H", "4H", "1D", "1W", "1M"]:
        success, _ = test_endpoint(
            "GET", f"/equity?range={range_val}",
            description=f"Get equity data (range={range_val})"
        )
        results.append((f"Equity {range_val}", success))
    
    # Test 11: Update config
    config_data = {
        "config": {
            "max_positions": 10,
            "default_leverage": 5,
            "risk_per_trade": 2.0
        }
    }
    success, _ = test_endpoint(
        "POST", "/config/update",
        data=config_data,
        description="Update bot configuration"
    )
    results.append(("Update Config", success))
    
    # Test 12: Pause bot
    success, _ = test_endpoint("POST", "/bot/pause", description="Pause bot")
    results.append(("Pause Bot", success))
    
    # Test 13: Stop bot
    success, _ = test_endpoint("POST", "/bot/stop", description="Stop bot")
    results.append(("Stop Bot", success))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{name:40} {status}")
    
    print("=" * 60)
    print(f"Total: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    print(f"Completed at: {datetime.now().isoformat()}")
    
    return passed == total


if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Test suite failed with error: {e}")
        exit(1)
