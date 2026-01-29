# RLdC Trading AiNalyzer Bot v0.7.0-beta

> **Uwaga:** To narzędzie służy do analizy rynku i edukacji. Nie stanowi porady inwestycyjnej. Handel wiąże się z ryzykiem i może prowadzić do strat.

## PL — Opis
RLdC Trading AiNalyzer Bot to modularny projekt do pobierania danych OHLCV (read-only), liczenia wskaźników technicznych, generowania ostrożnych sygnałów oraz raportów. System ma wbudowany moduł samodoskonalenia przez propozycje poprawek, PR-y i testy.

### Najważniejsze funkcje
- Pobieranie OHLCV z giełdy (ccxt, tylko read-only).
- SQLite jako lokalna baza danych + eksport CSV/Parquet.
- Wskaźniki: RSI, MACD, Bollinger Bands, Ichimoku.
- Sygnały BUY/SELL/WAIT z konserwatywnymi poziomami ryzyka.
- Raporty JSON + opcjonalnie HTML.
- Telegram bot + Web UI (FastAPI).
- Scheduler (APScheduler).
- Mechanizm self-improve: analiza logów i propozycje poprawek.

## EN — Short description
RLdC Trading AiNalyzer Bot is a modular Python project for read-only market data ingestion, indicator calculation, conservative signals, and reports. It includes Telegram, a lightweight web UI, and a safe self-improvement workflow via PRs.

## Instalacja (uv)
```bash
./scripts/setup.sh
```

## Konfiguracja `.env`
Projekt czyta sekrety z:
1. `/home/oem/rldc_full_setup/config/.env`
2. `.env` w katalogu projektu (fallback)

Przykładowa konfiguracja:
```
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
OPENAI_API_KEY=...
GITHUB_TOKEN=...
GITHUB_REPO=owner/repo
RLDC_PAIRS=BTC/USDT,ETH/USDT
RLDC_TIMEFRAMES=1m,15m,1h
```

## Uruchomienie CLI
```bash
rldc --help
rldc fetch --pair BTC/USDT --timeframe 1h
rldc analyze --pair BTC/USDT --timeframe 1h
rldc report --pair BTC/USDT --timeframe 1h --html
rldc run
```

## Web UI
```bash
rldc web --host 0.0.0.0 --port 8000
```

## Telegram
```bash
rldc telegram
```

## Testy i lint
```bash
./scripts/test.sh
./scripts/lint.sh
```

## Samodoskonalenie
Bot nie modyfikuje kodu w locie. Moduł `self_improve` analizuje logi błędów i tworzy propozycje. PR-y mogą być tworzone tylko po przejściu testów i ręcznej akceptacji.

## Log.txt
Każdy eksport lub publikacja artefaktów powinna zawierać plik `log.txt` z opisem projektu, wykonanymi i planowanymi działaniami oraz znanymi błędami.
