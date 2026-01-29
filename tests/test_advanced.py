from rldc.advanced.blockchain import analyze_blockchain
from rldc.advanced.deep_rl import run_simulation
from rldc.advanced.hft import simulate_hft
from rldc.advanced.predictive import generate_prediction
from rldc.advanced.quantum_optimizer import optimize_weights
from rldc.advanced.ultimate_ai import generate_vision


def test_quantum_optimizer():
    result = optimize_weights(steps=10)
    assert result.best_score >= 0
    assert len(result.best_weights) == 4


def test_deep_rl_simulation():
    result = run_simulation(episodes=10)
    assert result.episodes == 10


def test_predictive():
    result = generate_prediction("12h")
    assert result.horizon == "12h"


def test_hft():
    result = simulate_hft(orders=100)
    assert result.orders_simulated == 100


def test_blockchain():
    result = analyze_blockchain(transactions_checked=0)
    assert result.anomalies_found == 0


def test_ultimate_ai():
    result = generate_vision()
    assert "ryzykiem" in result.disclaimer.lower()
