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

## Portale AI (MVP)
```
rldc portal --port 5004
rldc portal-config --port 5003
rldc portal-zordon --port 5005
rldc portal-ultimate --port 5006
```

## Telegram
```
rldc telegram
```

## Raportowanie
```
rldc report --pair BTC/USDT --timeframe 1h --html
```

## Moduły eksperymentalne
```
rldc quantum-optimize
rldc deep-rl --episodes 50
rldc predictive --horizon 24h
rldc hft-sim --orders 1000
rldc blockchain-scan --transactions 0
rldc ultimate-ai
```
