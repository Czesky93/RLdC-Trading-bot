# Paczka do uruchomienia na laptopie

## Cel
Ten dokument opisuje jak wygenerować paczkę plików z repozytorium oraz jak
uruchomić podstawowe sprawdzenie spójności przed uruchomieniem aplikacji lokalnie.

## Generowanie paczki
Skrypt tworzy paczkę ZIP w katalogu `dist/` oraz uruchamia audyt repozytorium:
```bash
bash scripts/package_release.sh
```

Po zakończeniu znajdziesz:
- `dist/RLdC-Trading-bot-<timestamp>.zip`
- raporty audytu w `reports/`

## Co dalej na laptopie
1. Rozpakuj paczkę:
   ```bash
   unzip RLdC-Trading-bot-<timestamp>.zip -d RLdC-Trading-bot
   cd RLdC-Trading-bot
   ```
2. Uruchom audyt spójności:
   ```bash
   python3 scripts/audit_repo.py
   ```
3. Uzupełnij konfiguracje (np. `config.json`) według wyników raportu w `reports/`.

## Wskazówki
- Skrypt nie dołącza `.git`, `dist/`, `node_modules/` i środowisk wirtualnych.
- Upewnij się, że `python3` i `zip` są dostępne w systemie.
