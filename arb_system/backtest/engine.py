from data.loader import load_price_data
from data.feeds import generate_feeds
from strategy.arbitrage import check_arbitrage
from config import MIN_SPREAD_PCT

def run_engine():
    prices = load_price_data("btc.csv")
    feeds = generate_feeds(prices)

    opportunities = []

    for timestamp, row in feeds.iterrows():
        price_a = row["exchange_a"]
        price_b = row["exchange_b"]

        signal = check_arbitrage(price_a, price_b, MIN_SPREAD_PCT)

        if signal is not None:
            signal["timestamp"] = timestamp
            opportunities.append(signal)
    
    return opportunities

