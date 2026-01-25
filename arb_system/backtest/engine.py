from data.loader import load_price_data
from data.feeds import generate_feeds

def run_engine():
    prices = load_price_data("btc.csv")
    feeds = generate_feeds(prices)
    return feeds
