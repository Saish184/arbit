from backtest.engine import run_engine

if __name__ == "__main__":
    feeds = run_engine()

    print("\n=== SIMULATED FEEDS (HEAD) ===")
    print(feeds.head())

    print("\n=== SIMULATED FEEDS (TAIL) ===")
    print(feeds.tail())
