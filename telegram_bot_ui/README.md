# RLdC Telegram Bot UI

Enhanced Telegram bot with graphical interface for managing your RLdC Trading Bot portfolio.

## Features

### 🎨 Graphical Interface
- **Interactive Inline Keyboards** - Easy navigation with buttons
- **Price Charts** - Visual representation of cryptocurrency prices using matplotlib
- **Rich Formatting** - Emoji-enhanced messages for better readability
- **Real-time Updates** - Live data from Binance API

### 💰 Portfolio Management
- View complete portfolio with all crypto holdings
- Total portfolio value in USD
- 24h profit/loss tracking
- Individual asset balances and values

### 📊 Market Data
- Current prices for major cryptocurrencies (BTC, ETH, BNB, SOL, ADA)
- Graphical price charts
- Real-time market updates

### 👛 Account Balance
- Total portfolio value
- Available balance for trading
- Performance metrics (daily, weekly, monthly)
- Asset count

## Installation

### Prerequisites
- Python 3.8+
- Telegram Bot Token (from @BotFather)
- Optional: Binance API keys for account data

### Dependencies

```bash
pip install -r requirements.txt
```

### Configuration

1. Create a `config.json` file in the parent directory:

```json
{
    "TELEGRAM_BOT_TOKEN": "your_telegram_bot_token",
    "CHAT_ID": "your_telegram_chat_id",
    "BINANCE_API_KEY": "your_binance_api_key",
    "BINANCE_API_SECRET": "your_binance_api_secret"
}
```

Or set environment variables:
```bash
export TELEGRAM_BOT_TOKEN="your_token"
export CHAT_ID="your_chat_id"
export BINANCE_API_KEY="your_key"
export BINANCE_API_SECRET="your_secret"
```

2. Get your Telegram Bot Token:
   - Message @BotFather on Telegram
   - Create a new bot with `/newbot`
   - Copy the token

3. Get your Chat ID:
   - Message your bot
   - Visit: `https://api.telegram.com/bot<YOUR_TOKEN>/getUpdates`
   - Find your chat ID in the response

## Usage

### Start the Bot

```bash
cd telegram_bot_ui
python bot.py
```

### Bot Commands

Send `/start` to your bot to see the main menu.

### Interactive Buttons

- **💰 Portfolio** - View your complete crypto portfolio
- **📊 Market** - See graphical price charts
- **📈 Prices** - Get current cryptocurrency prices
- **🪙 Balance** - Check account balance and performance
- **⚙️ Settings** - View bot configuration
- **🔙 Back to Menu** - Return to main menu

## Features in Detail

### Portfolio View
Shows:
- Total portfolio value in USD
- 24h change (amount and percentage)
- Individual holdings for each cryptocurrency
- Free vs locked balances
- USD value per asset
- Available USDT balance

### Market Charts
- Bar chart visualization of major cryptocurrencies
- Color-coded by asset
- Current prices displayed on bars
- Custom RLdC themed colors

### Price Tracking
- Real-time prices from Binance API
- Major trading pairs (BTC, ETH, BNB, SOL, ADA)
- Timestamp of last update
- Formatted with emojis for easy reading

### Account Balance
- Total portfolio value
- Available trading balance
- Performance metrics:
  - Daily change
  - Weekly change
  - Monthly change
- Asset count
- Last update timestamp

## Architecture

### Technology Stack
- **python-telegram-bot** - Telegram Bot API wrapper
- **matplotlib** - Chart generation
- **requests** - HTTP requests to Binance API

### Data Sources
- **Binance Public API** - Market prices (no authentication required)
- **Simulated Data** - Portfolio holdings (for demo purposes)

**Note:** In production, account data would be fetched from Binance Account API using proper authentication through a secure backend server.

## Security Notes

⚠️ **Important Security Information:**

1. **Never commit config.json** - Add it to `.gitignore`
2. **API Keys** - Store securely, never expose in code
3. **Read-Only Permissions** - Use API keys with minimal permissions
4. **Backend Required** - For production, implement a secure backend to handle API signing
5. **HTTPS Only** - Telegram bots use HTTPS automatically

## Development

### File Structure
```
telegram_bot_ui/
├── bot.py              # Main bot application
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

### Adding New Features

To add a new menu button:

1. Add button to `get_main_keyboard()`:
```python
InlineKeyboardButton("🔔 Alerts", callback_data="alerts")
```

2. Create handler function:
```python
async def alerts_command(update, context):
    # Your code here
    pass
```

3. Register in `button_handler()`:
```python
handlers = {
    ...
    "alerts": alerts_command,
}
```

## Troubleshooting

### Bot not responding
- Check if bot token is correct
- Verify bot is running (`python bot.py`)
- Check console for error messages

### No prices showing
- Verify internet connection
- Check if Binance API is accessible
- Review error logs

### Charts not generating
- Ensure matplotlib is installed
- Check if `matplotlib.use('Agg')` is set before imports
- Verify sufficient disk space for temporary files

## License

Part of the RLdC Trading Bot project.

## Support

For issues and questions, refer to the main RLdC Trading Bot repository.
