import os
import pandas as pd
import matplotlib.pyplot as plt
from flask import Flask, render_template

app = Flask(__name__)

def load_trade_history():
    """Ładowanie historii transakcji"""
    log_file = "strategy_log.txt"
    if not os.path.exists(log_file):
        return []

    data = []
    with open(log_file, "r") as file:
        for line in file.readlines():
            parts = line.strip().split(":")
            if len(parts) == 2:
                symbol, action = parts
                data.append({"symbol": symbol.strip(), "action": action.strip()})
    return data

@app.route("/")
def index():
    trades = load_trade_history()
    return render_template("dashboard.html", trades=trades)

@app.route("/performance")
def performance():
    """Generowanie wykresów skuteczności strategii"""
    trade_data = load_trade_history()

    if not trade_data:
        return "Brak danych do analizy!"

    df = pd.DataFrame(trade_data)
    action_counts = df["action"].value_counts()

    plt.figure(figsize=(8, 5))
    action_counts.plot(kind="bar")
    plt.xlabel("Akcja")
    plt.ylabel("Liczba transakcji")
    plt.title("Skuteczność strategii")
    plt.savefig("static/performance.png")
    return render_template("performance.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
