#!/bin/bash

echo "🚀 Kompilacja RLdC Trading Bot zgodnie z KODALL.txt"
echo "================================="

# Sprawdzenie i instalacja zależności
echo "🔍 Sprawdzanie wymaganych pakietów..."
pip install flask pandas ta binance telepot tweepy gym stable-baselines3 openai requests matplotlib scipy numpy opencv-python

# Pobranie listy plików do kompilacji z KODALL.txt
echo "🔄 Odczytywanie plików do kompilacji z KODALL.txt..."
mapfile -t FILES < <(grep -oP '(?<=🔹 ).*' KODALL.txt)

# Uruchamianie każdego modułu znalezionego w KODALL.txt
echo "🚀 Uruchamianie modułów..."
for file in "${FILES[@]}"; do
    if [[ -f "$file" ]]; then
        echo "▶️ Uruchamianie: $file"
        python "$file" &
        sleep 2
    else
        echo "⚠️ Plik nie znaleziony: $file"
    fi
done

echo "✅ RLdC Trading Bot działa!"
