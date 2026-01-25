# main.py

from backtest.engine import run_engine

if __name__ == "__main__":
    portfolio = run_engine()

    print("\n=== BACKTEST RESULTS ===")
    print(f"Trades executed: {portfolio.trades}")
    print(f"Final cash: ${portfolio.cash:,.2f}")
    print(f"Total PnL: ${portfolio.pnl:,.2f}")
