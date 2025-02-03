import gym
import numpy as np
import pandas as pd
import ta
import os
from stable_baselines3 import PPO

class TradingEnv(gym.Env):
    """Środowisko Reinforcement Learning dla tradingu"""
    
    def __init__(self, data_file="market_data_BTCUSDT.csv", initial_balance=1000):
        super(TradingEnv, self).__init__()
        
        if not os.path.exists(data_file):
            raise FileNotFoundError(f"🚨 Brak danych rynkowych: {data_file}")

        self.df = pd.read_csv(data_file)
        self.df["EMA_9"] = ta.trend.EMAIndicator(self.df["close"], window=9).ema_indicator()
        self.df["EMA_21"] = ta.trend.EMAIndicator(self.df["close"], window=21).ema_indicator()
        self.df["MACD"] = ta.trend.MACD(self.df["close"]).macd()
        self.df["RSI"] = ta.momentum.RSIIndicator(self.df["close"]).rsi()

        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.position = 0
        self.current_step = 0

        self.action_space = gym.spaces.Discrete(3)  # 0 = NIC, 1 = KUP, 2 = SPRZEDAJ
        self.observation_space = gym.spaces.Box(low=-np.inf, high=np.inf, shape=(4,), dtype=np.float32)

    def reset(self):
        self.balance = self.initial_balance
        self.position = 0
        self.current_step = 0
        return self._get_observation()

    def step(self, action):
        price = self.df["close"].iloc[self.current_step]

        if action == 1 and self.position == 0:  # KUP
            self.position = self.balance / price
            self.balance -= self.position * price
        elif action == 2 and self.position > 0:  # SPRZEDAJ
            self.balance += self.position * price
            self.position = 0

        self.current_step += 1
        done = self.current_step >= len(self.df) - 1
        reward = self.balance + (self.position * price) - self.initial_balance

        return self._get_observation(), reward, done, {}

    def _get_observation(self):
        return np.array([
            self.df["EMA_9"].iloc[self.current_step],
            self.df["EMA_21"].iloc[self.current_step],
            self.df["MACD"].iloc[self.current_step],
            self.df["RSI"].iloc[self.current_step]
        ])

if __name__ == "__main__":
    env = TradingEnv()
    model = PPO("MlpPolicy", env, verbose=1)
    model.learn(total_timesteps=100000)
    model.save("deep_rl_trading_model")
    print("✅ Model AI Reinforcement Learning został wytrenowany!")
