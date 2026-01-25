import numpy as np
import pandas as pd

def generate_feeds(price_df: pd.DataFrame, spread: float = 0.001):
    """
    Generate two simulated exchanges from one price series.
    spread = total relative spread between exchanges

    """

    prices = price_df["close"]

    # small random noise to avoid perfect symmetry
    noise = np.random.normal(0, spread * 0.1, size=len(prices))

    exchange_a = prices * (1 - spread / 2 + noise)
    exchange_b = prices * (1 + spread / 2 + noise)

    feeds = pd.DataFrame({
        "exchange_a" : exchange_a,
        "exchange_b" : exchange_b    }
        , index = price_df.index)
    
    return feeds
