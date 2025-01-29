import pandas as pd

def calculate_ichimoku(df):
    high_9 = df['high'].rolling(window=9).max()
    low_9 = df['low'].rolling(window=9).min()
    df['tenkan_sen'] = (high_9 + low_9) / 2

    high_26 = df['high'].rolling(window=26).max()
    low_26 = df['low'].rolling(window=26).min()
    df['kijun_sen'] = (high_26 + low_26) / 2

    df['senkou_span_a'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(26)
    high_52 = df['high'].rolling(window=52).max()
    low_52 = df['low'].rolling(window=52).min()
    df['senkou_span_b'] = ((high_52 + low_52) / 2).shift(26)

    df['chikou_span'] = df['close'].shift(-26)
    return df

def calculate_bollinger_bands(df, window=20):
    df['sma'] = df['close'].rolling(window=window).mean()
    df['stddev'] = df['close'].rolling(window=window).std()
    df['upper_band'] = df['sma'] + (2 * df['stddev'])
    df['lower_band'] = df['sma'] - (2 * df['stddev'])
    return df

def calculate_vwap(df):
    df['vwap'] = (df['volume'] * (df['high'] + df['low'] + df['close']) / 3).cumsum() / df['volume'].cumsum()
    return df
