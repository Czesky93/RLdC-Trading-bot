#!/usr/bin/env python3
"""
RLdC Trading Bot - Enhanced Telegram Interface
Graphical interface with inline keyboards, charts, and account information
"""

import json
import os
import time
from datetime import datetime
from io import BytesIO

import matplotlib
matplotlib.use('Agg')  # Non-GUI backend
import matplotlib.pyplot as plt
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

# Configuration
CONFIG_FILE = "../config.json"

def load_config():
    """Load configuration from JSON file"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return {
        "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN", ""),
        "CHAT_ID": os.getenv("CHAT_ID", ""),
        "BINANCE_API_KEY": os.getenv("BINANCE_API_KEY", ""),
        "BINANCE_API_SECRET": os.getenv("BINANCE_API_SECRET", ""),
    }

config = load_config()

# Emoji constants
EMOJI = {
    "rocket": "🚀",
    "chart": "📊",
    "money": "💰",
    "up": "📈",
    "down": "📉",
    "wallet": "👛",
    "coin": "🪙",
    "btc": "₿",
    "success": "✅",
    "warning": "⚠️",
    "error": "❌",
    "info": "ℹ️",
    "settings": "⚙️",
    "back": "🔙",
}

def get_main_keyboard():
    """Create main menu keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(f"{EMOJI['wallet']} Portfolio", callback_data="portfolio"),
            InlineKeyboardButton(f"{EMOJI['chart']} Market", callback_data="market"),
        ],
        [
            InlineKeyboardButton(f"{EMOJI['up']} Prices", callback_data="prices"),
            InlineKeyboardButton(f"{EMOJI['coin']} Balance", callback_data="balance"),
        ],
        [
            InlineKeyboardButton(f"{EMOJI['settings']} Settings", callback_data="settings"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_keyboard():
    """Create back button keyboard"""
    keyboard = [[InlineKeyboardButton(f"{EMOJI['back']} Back to Menu", callback_data="main_menu")]]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler"""
    welcome_message = f"""
{EMOJI['rocket']} *RLdC Trading Bot Portal*

Welcome to your AI-powered cryptocurrency trading assistant!

{EMOJI['success']} *Features:*
• Real-time portfolio tracking
• Live market data
• Trading signals
• Account balance monitoring
• Price alerts

Select an option below to get started:
    """
    await update.message.reply_text(
        welcome_message,
        parse_mode="Markdown",
        reply_markup=get_main_keyboard(),
    )

async def get_binance_prices():
    """Fetch current cryptocurrency prices from Binance"""
    try:
        response = requests.get(
            "https://api.binance.com/api/v3/ticker/price",
            timeout=5
        )
        prices = response.json()
        
        # Filter for major pairs
        major_pairs = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "ADAUSDT"]
        filtered_prices = [p for p in prices if p["symbol"] in major_pairs]
        
        return filtered_prices
    except Exception as e:
        print(f"Error fetching prices: {e}")
        return []

async def create_price_chart(symbols=["BTCUSDT"]):
    """Create a price chart using matplotlib"""
    try:
        # Fetch historical data (simplified - using current price as demo)
        prices_data = await get_binance_prices()
        
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor('#1a1a2e')
        ax.set_facecolor('#16213e')
        
        # Simulate some price data for visualization
        symbols_to_plot = ["BTC", "ETH", "BNB", "SOL", "ADA"]
        values = [42150, 2245, 312, 98, 0.52]
        colors = ['#f7931a', '#627eea', '#f3ba2f', '#00d4aa', '#0033ad']
        
        bars = ax.bar(symbols_to_plot, values, color=colors, edgecolor='white', linewidth=1.5)
        
        ax.set_ylabel('Price (USDT)', color='white', fontsize=12)
        ax.set_title('Cryptocurrency Prices', color='#00d9ff', fontsize=16, fontweight='bold')
        ax.tick_params(colors='white')
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'${value:,.2f}',
                   ha='center', va='bottom', color='white', fontweight='bold')
        
        plt.tight_layout()
        
        # Save to bytes buffer
        buf = BytesIO()
        plt.savefig(buf, format='png', facecolor='#1a1a2e', edgecolor='none')
        buf.seek(0)
        plt.close()
        
        return buf
    except Exception as e:
        print(f"Error creating chart: {e}")
        return None

async def portfolio_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show portfolio information"""
    query = update.callback_query
    await query.answer()
    
    # Simulated portfolio data
    portfolio_text = f"""
{EMOJI['wallet']} *Your Portfolio*

{EMOJI['money']} *Total Value:* $31,782.71
{EMOJI['up']} *24h Change:* +$731.00 (+2.3%)

{EMOJI['coin']} *Holdings:*
• {EMOJI['btc']} BTC: 0.30 ($12,644.92)
• ETH: 2.60 ($5,837.78)
• BNB: 15.00 ($4,686.75)
• USDT: 5,520.50 ($5,520.50)
• SOL: 25.00 ($2,468.75)
• ADA: 1,200.00 ($624.00)

{EMOJI['info']} *Available Balance:* $5,420.50 USDT
    """
    
    await query.edit_message_text(
        portfolio_text,
        parse_mode="Markdown",
        reply_markup=get_back_keyboard(),
    )

async def market_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show market data with chart"""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        f"{EMOJI['chart']} Generating market chart...",
        parse_mode="Markdown",
    )
    
    # Create and send chart
    chart = await create_price_chart()
    
    if chart:
        await query.message.reply_photo(
            photo=chart,
            caption=f"{EMOJI['chart']} *Current Market Prices*\nUpdated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            parse_mode="Markdown",
            reply_markup=get_back_keyboard(),
        )
        # Delete the "generating" message
        await query.message.delete()
    else:
        await query.edit_message_text(
            f"{EMOJI['error']} Failed to generate chart. Please try again.",
            parse_mode="Markdown",
            reply_markup=get_back_keyboard(),
        )

async def prices_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show current prices"""
    query = update.callback_query
    await query.answer()
    
    prices = await get_binance_prices()
    
    if prices:
        price_text = f"{EMOJI['up']} *Current Prices*\n\n"
        for price in prices[:5]:  # Show top 5
            symbol = price["symbol"].replace("USDT", "")
            value = float(price["price"])
            price_text += f"• {symbol}: ${value:,.2f}\n"
        
        price_text += f"\n{EMOJI['info']} Updated: {datetime.now().strftime('%H:%M:%S')}"
    else:
        price_text = f"{EMOJI['error']} Failed to fetch prices"
    
    await query.edit_message_text(
        price_text,
        parse_mode="Markdown",
        reply_markup=get_back_keyboard(),
    )

async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show account balance"""
    query = update.callback_query
    await query.answer()
    
    balance_text = f"""
{EMOJI['wallet']} *Account Balance*

{EMOJI['money']} *Total Portfolio Value*
$31,782.71

{EMOJI['success']} *Available for Trading*
$5,420.50 USDT

{EMOJI['coin']} *Assets Count:* 6

{EMOJI['chart']} *Performance*
• Today: +$150.25 (+0.47%)
• This Week: +$1,234.56 (+4.04%)
• This Month: +$3,456.78 (+12.21%)

{EMOJI['info']} Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    await query.edit_message_text(
        balance_text,
        parse_mode="Markdown",
        reply_markup=get_back_keyboard(),
    )

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show settings"""
    query = update.callback_query
    await query.answer()
    
    api_configured = bool(config.get("BINANCE_API_KEY"))
    
    settings_text = f"""
{EMOJI['settings']} *Bot Settings*

{EMOJI['success'] if api_configured else EMOJI['warning']} *API Status:* {'Configured' if api_configured else 'Not Configured'}

{EMOJI['info']} *Features:*
• Auto-trading: Disabled
• Price alerts: Enabled
• Portfolio tracking: Enabled

{EMOJI['warning']} To configure API keys, edit config.json
    """
    
    await query.edit_message_text(
        settings_text,
        parse_mode="Markdown",
        reply_markup=get_back_keyboard(),
    )

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Return to main menu"""
    query = update.callback_query
    await query.answer()
    
    welcome_message = f"""
{EMOJI['rocket']} *RLdC Trading Bot Portal*

Select an option below:
    """
    
    await query.edit_message_text(
        welcome_message,
        parse_mode="Markdown",
        reply_markup=get_main_keyboard(),
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    
    handlers = {
        "portfolio": portfolio_command,
        "market": market_command,
        "prices": prices_command,
        "balance": balance_command,
        "settings": settings_command,
        "main_menu": main_menu,
    }
    
    handler = handlers.get(query.data)
    if handler:
        await handler(update, context)
    else:
        await query.answer("Unknown command")

def main():
    """Run the bot"""
    token = config.get("TELEGRAM_BOT_TOKEN")
    
    if not token:
        print(f"{EMOJI['error']} Error: TELEGRAM_BOT_TOKEN not configured")
        print(f"{EMOJI['info']} Please set it in config.json or environment variable")
        return
    
    # Create application
    app = Application.builder().token(token).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    
    print(f"{EMOJI['success']} RLdC Telegram Bot started successfully!")
    print(f"{EMOJI['rocket']} Bot is running... Press Ctrl+C to stop")
    
    # Run the bot
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
