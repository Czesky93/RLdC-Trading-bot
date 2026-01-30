#!/usr/bin/env python3
"""
RLdC Terminal - WebSocket testing tool for the Trading Bot
Tests WebSocket connection and displays live updates
"""
import asyncio
import websockets
import json
import sys
from datetime import datetime


async def test_websocket(url: str):
    """Connect to WebSocket and display live updates"""
    print(f"🔌 Connecting to WebSocket: {url}")
    
    try:
        async with websockets.connect(url) as websocket:
            print("✅ Connected successfully!")
            print("📡 Listening for updates... (Press Ctrl+C to exit)\n")
            
            # Send a test message
            await websocket.send("Hello from RLdC Terminal")
            
            # Receive messages
            while True:
                try:
                    message = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                    data = json.loads(message)
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    
                    print(f"[{timestamp}] 📩 Received:", end=" ")
                    if data.get("type") == "connection":
                        print(f"🔗 {data.get('status', 'unknown')}")
                    elif data.get("type") == "update":
                        print(f"📊 Update #{data.get('data', {}).get('counter', '?')}")
                    elif data.get("type") == "echo":
                        print(f"🔊 Echo: {data.get('message', '')}")
                    else:
                        print(json.dumps(data, indent=2))
                    
                except asyncio.TimeoutError:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] ⏰ No message received (timeout)")
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error: {e}")
                    print(f"   Raw message: {message}")
                
    except websockets.exceptions.WebSocketException as e:
        print(f"❌ WebSocket error: {e}")
        return False
    except KeyboardInterrupt:
        print("\n\n👋 Disconnecting...")
        return True
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    
    return True


def main():
    """Main entry point"""
    # Default URL or from command line
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = "ws://127.0.0.1:8000/ws"
    
    print("=" * 60)
    print("🚀 RLdC Trading Bot - WebSocket Terminal")
    print("=" * 60)
    print()
    
    # Run the async WebSocket test
    try:
        asyncio.run(test_websocket(url))
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")


if __name__ == "__main__":
    main()
