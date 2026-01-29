# RLdC Trading AiNalyzer Bot v0.7 beta

## Szybki start
1. Zainstaluj `uv`.
2. Uruchom `scripts/setup.sh`.
3. Skonfiguruj `.env` (patrz niżej).
4. Pobierz dane i uruchom analizę:
   ```bash
   rldc fetch --pair BTC/USDT --timeframe 1h
   rldc analyze --pair BTC/USDT --timeframe 1h
   ```

## Konfiguracja `.env`
Projekt czyta sekrety z:
1. `/home/oem/rldc_full_setup/config/.env` (domyślnie)
2. `.env` w katalogu projektu (fallback)

Przykład:
```
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
OPENAI_API_KEY=...
GITHUB_TOKEN=...
GITHUB_REPO=owner/repo
RLDC_PAIRS=BTC/USDT,ETH/USDT
RLDC_TIMEFRAMES=1m,15m,1h
```

## Web
```
uvicorn rldc.web.app:create_app --factory --host 0.0.0.0 --port 8000
```

## Telegram
```
rldc telegram
```

## Raportowanie
```
rldc report --pair BTC/USDT --timeframe 1h --html
```
