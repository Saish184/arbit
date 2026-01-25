# main.py

from backtest.engine import run_engine

if __name__ == "__main__":
    opportunities = run_engine()

    print(f"\nTotal arbitrage opportunities detected: {len(opportunities)}\n")

    for opp in opportunities[:10]:
        print(
            f"{opp['timestamp']} | "
            f"{opp['direction']} | "
            f"spread = {opp['spread_pct'] * 100:.3f}%"
        )
