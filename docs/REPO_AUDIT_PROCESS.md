# Proces audytu repozytorium RLdC

## Cel
Wyłapanie braków, błędów i niespójności przed uruchomieniem na laptopie oraz
ujednolicenie konfiguracji i zależności.

## Szybki start (komendy)
1. Uruchom skaner repozytorium:
   ```bash
   python3 scripts/audit_repo.py
   ```
2. Przejrzyj raporty:
   - `reports/audit_report.md`
   - `reports/audit_report.json`

## Zakres kontroli w skrypcie
Skrypt `scripts/audit_repo.py` wykrywa:
- brakujące importy (heurystyki na podstawie użycia modułów),
- placeholdery poświadczeń (np. `GOOGLE_CLIENT_ID`, `your_email@example.com`),
- brak pliku `config.json`, gdy jest wymagany,
- wywołania w top-level (efekty uboczne przy imporcie),
- pliki wymienione w README, które nie istnieją.

## Dalszy proces usprawniania i uzupełniania braków
1. **Zbierz wymagania runtime**:
   - Wypisz wszystkie używane klucze API i pliki konfiguracyjne.
   - Ustal wartości domyślne i bezpieczne tryby offline.
2. **Ujednolić konfigurację**:
   - Zastąp w kodzie stałe placeholdery odwołaniami do env lub `config.json`.
   - Dodaj przykładowy `config.example.json`.
3. **Usunąć efekty uboczne przy imporcie**:
   - Przenieś wywołania testowe do bloków `if __name__ == "__main__":`.
4. **Spójność zależności**:
   - Zsynchronizuj `requirements.txt` z realnymi importami.
5. **Stabilność i testy**:
   - Dodaj proste testy uruchomieniowe (smoke tests) dla głównych entrypointów.
6. **Walidacja**:
   - Uruchom ponownie `scripts/audit_repo.py` i sprawdź regresje w raporcie.

## Rekomendowany przebieg uzupełniania braków
1. Wygeneruj raport z `scripts/audit_repo.py`.
2. Otwórz `reports/audit_report.md` i rozwiąż problemy w kolejności:
   1) brakujące importy/syntax errors,
   2) brak `config.json` / placeholdery,
   3) top-level call side-effects,
   4) brakujące pliki z README.
3. Ponów raport i zatwierdź zmiany.
