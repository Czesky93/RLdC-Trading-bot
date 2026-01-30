#!/usr/bin/env python3
"""
RLdC Trading Bot Gateway Server Launcher
Starts the FastAPI gateway server with proper configuration
"""

import os
import sys
import argparse
import uvicorn
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description="RLdC Trading Bot Gateway Server",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start server on default port (8000)
  python start_gateway.py
  
  # Start on custom port
  python start_gateway.py --port 8080
  
  # Start with auto-reload for development
  python start_gateway.py --reload
  
  # Start with multiple workers (production)
  python start_gateway.py --workers 4
  
  # Start with Binance API credentials
  BINANCE_API_KEY=your_key BINANCE_API_SECRET=your_secret python start_gateway.py
        """
    )
    
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )
    
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        help="Number of worker processes (production only, default: 1)"
    )
    
    parser.add_argument(
        "--log-level",
        default="info",
        choices=["critical", "error", "warning", "info", "debug"],
        help="Log level (default: info)"
    )
    
    args = parser.parse_args()
    
    # Check if gateway_server.py exists
    if not Path("gateway_server.py").exists():
        print("ERROR: gateway_server.py not found in current directory")
        print("Please run this script from the RLdC-Trading-bot directory")
        sys.exit(1)
    
    # Display startup info
    print("=" * 60)
    print("RLdC Trading Bot Gateway Server")
    print("=" * 60)
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"Workers: {args.workers}")
    print(f"Reload: {args.reload}")
    print(f"Log Level: {args.log_level}")
    print()
    
    # Check for Binance API credentials
    if os.getenv("BINANCE_API_KEY") and os.getenv("BINANCE_API_SECRET"):
        print("✓ Binance API credentials detected")
    else:
        print("⚠ Binance API credentials not found - running in DEMO mode")
        print("  Set BINANCE_API_KEY and BINANCE_API_SECRET to use real trading")
    
    print()
    print(f"API Documentation: http://localhost:{args.port}/docs")
    print(f"Alternative Docs: http://localhost:{args.port}/redoc")
    print(f"Health Check: http://localhost:{args.port}/health")
    print("=" * 60)
    print()
    
    # Start the server
    try:
        uvicorn.run(
            "gateway_server:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            workers=args.workers if not args.reload else 1,
            log_level=args.log_level
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        print(f"\nERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
