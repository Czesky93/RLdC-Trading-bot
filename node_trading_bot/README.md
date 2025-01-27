
# Trading Bot Application

## Description
This is a Node.js-based trading bot that integrates with the Binance API for account information and market analysis.

## Setup

1. Clone the repository.
2. Run `npm install` to install dependencies.
3. Create a `.env` file with your Binance API credentials:
   ```
   BINANCE_API_KEY=your_api_key_here
   BINANCE_SECRET_KEY=your_secret_key_here
   PORT=3000
   ```
4. Start the application with `npm start`.
5. Visit `http://localhost:3000` in your browser.

## Endpoints
- `/`: Homepage.
- `/account`: Fetches Binance account information.
- `/analyze`: Analyzes market data (POST request).
