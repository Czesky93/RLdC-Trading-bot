# Instrukcja uruchomienia na Ubuntu

Poniżej znajdziesz kompletne kroki uruchomienia systemu na Ubuntu oraz krótkie podsumowanie, co jest gotowe „out‑of‑the‑box”, a co wymaga dodatkowej konfiguracji lub danych.

## Wymagania wstępne (Ubuntu 20.04/22.04)

Zainstaluj podstawowe narzędzia i biblioteki:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip build-essential libpq-dev
```

Opcjonalnie (jeśli chcesz uruchamiać część Node.js z katalogu `node_trading_bot/`):

```bash
sudo apt install -y nodejs npm
```

## Instalacja zależności Python

1. Wejdź do repozytorium:
   ```bash
   cd /workspace/RLdC-Trading-bot
   ```

2. Utwórz i aktywuj wirtualne środowisko:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Zainstaluj zależności z `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

> Uwaga: `installer.py` instaluje dodatkowe biblioteki (m.in. `pandas`, `ta`, `binance`, `telepot`, `tweepy`, `gym`, `stable-baselines3`, `openai`, `matplotlib`, `scipy`, `numpy`, `opencv-python`). Jeśli planujesz uruchamianie modułów AI/ML i analitycznych, zainstaluj je ręcznie lub uruchom instalator.
> 
> ```bash
> python installer.py
> ```

## Konfiguracja (`config.json`)

Wiele modułów oczekuje pliku `config.json`. Możesz go utworzyć uruchamiając:

```bash
python config_manager.py
```

Następnie uzupełnij **realne** klucze/parametry (pliku `config.json` używa wiele modułów, m.in. Telegram, Binance, OpenAI, Etherscan, News API):

- `TELEGRAM_BOT_TOKEN`, `CHAT_ID`
- `BINANCE_API_KEY`, `BINANCE_API_SECRET`
- `OPENAI_API_KEY`
- `ETHERSCAN_API_KEY`, `ETHEREUM_TRACK_ADDRESS`
- `NEWS_API_KEY`

## Uruchamianie kluczowych modułów

### Portal WWW (Flask)

```bash
python web_portal.py
```

Domyślny adres: `http://localhost:5000/`

### Demo symulacji tradingu

```bash
python demo_trading.py
```

Domyślny adres: `http://localhost:5002/`

> Demo wymaga pliku `market_data_BTCUSDT.csv`, którego nie ma w repozytorium. Trzeba go wygenerować/pozyskać samodzielnie (np. przez API Binance) i umieścić w katalogu projektu.

### Główny bot (oraz moduły wspierające)

Wersja „all‑in‑one” jest uruchamiana przez `master_ai_trader.py`, ale wymaga poprawnej konfiguracji API (Telegram + Binance + dodatkowe usługi) i korzysta z modułów, które same wykonują zapytania do zewnętrznych API.

```bash
python master_ai_trader.py
```

### Automatyczny handel na podstawie realnych sygnałów

Nowy moduł `auto_trader.py` pobiera **realne dane z giełdy Binance** (ceny, wolumeny, order book) i buduje sygnał w oparciu o **czytelne, konfigurowalne warunki** z `config.json`.

**Warunki sygnału (konfigurowalne w `TRADING_RULES`):**
- Trend (SMA fast > SMA slow lub odwrotnie).
- RSI w zadanym zakresie (byczy/niedźwiedzi).
- Nierównowaga order book (przewaga bidów/asków).
- Skok wolumenu względem średniej.

Wykonanie zlecenia wymaga spełnienia minimalnego progu punktowego (`MIN_SIGNAL_SCORE`).

**Warunki handlu (konfigurowalne w `AUTO_TRADING`):**
- Lista instrumentów (`SYMBOLS`).
- Wielkość zlecenia w USDT (`ORDER_SIZE_USDT`).
- Dopuszczalny poślizg ceny (`MAX_SLIPPAGE_PCT`).
- Tryb testowy `DRY_RUN` (domyślnie `True` – nie składa zleceń).
- Interwał pętli (`LOOP_SECONDS`).

Uruchomienie:

```bash
python auto_trader.py
```

> Uwaga: aby wykonać **realny handel**, ustaw `DRY_RUN` na `false` i upewnij się, że w `config.json` są prawdziwe klucze API Binance oraz wystarczające środki na koncie.

### Node.js trading bot (opcjonalnie)

```bash
cd node_trading_bot
npm install
# utwórz .env z REALNYMI wartościami BINANCE_API_KEY i BINANCE_SECRET_KEY
# PORT ustaw tylko jeśli chcesz zmienić domyślny (3000) z kodu
npm start
```

Domyślny adres: `http://localhost:3000/`

## Co jest gotowe vs. co wymaga uzupełnień

### ✅ Gotowe / działa lokalnie po instalacji zależności

- **Portal WWW** (`web_portal.py`) z endpointami `/`, `/settings`, `/market_analysis` – działa po zainstalowaniu zależności i bez dodatkowej konfiguracji (poza opcjonalnym `config.json`).
- **Menadżer konfiguracji** (`config_manager.py`) – tworzy `config.json` i umożliwia jego edycję.
- **Node.js bot** (`node_trading_bot/`) – działa po instalacji `npm` i dodaniu `.env`.

### ⚠️ Wymaga konfiguracji kluczy API

- **Trading przez Binance** (`binance_trader.py`, `master_ai_trader.py`, `backend/`) – wymagane klucze API Binance.
- **Telegram** (`master_ai_trader.py`, `telegram_ai_bot.py`, `telegram_bot.py`) – wymagany token bota i `CHAT_ID`.
- **OpenAI / Quantum / AI** (`ai_optimizer.py`, `rldc_quantum_ai.py`, `zordon_ai.py`, `ultimate_ai.py`) – wymagany `OPENAI_API_KEY`.
- **Blockchain/News/Twitter** (`blockchain_analysis.py`, `news_watcher.py`, `whale_tracker.py`) – wymagane odpowiednie klucze (Etherscan/News/Twitter).

### ❗ Braki / rzeczy do przygotowania samodzielnie

- **Dane CSV do demo tradingu** – `demo_trading.py` oczekuje `market_data_BTCUSDT.csv`.
- **Baza danych Postgres** – `database.py` ma przykładowy `DATABASE_URL` i nie zawiera migracji ani konfiguracji środowiska.
- **Instalator z README** – README wspomina archiwum `RLdC_Trading_Bot_Installer.zip`, którego nie ma w repozytorium.

## Szybka checklista uruchomienia

1. Zainstaluj pakiety systemowe + Python.
2. Utwórz venv i zainstaluj zależności.
3. Wygeneruj `config.json` i uzupełnij klucze API.
4. Uruchom wybrane moduły (portal, demo, master bot, node bot).

Jeśli potrzebujesz, mogę też przygotować gotowy skrypt startowy (systemd/Procfile) albo uproszczony `.env`/`config.json`.
