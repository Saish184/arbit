# backtest/engine.py

from data.loader import load_price_data
from data.feeds import generate_feeds
from strategy.arbitrage import check_arbitrage
from execution.simulator import execute_arbitrage
from portfolio.portfolio import Portfolio
from config import (
    MIN_SPREAD_PCT,
    TRADE_SIZE_BTC,
    FEE_PCT,
    INITIAL_CASH,
)

def run_engine():
    prices = load_price_data("btc.csv")
    feeds = generate_feeds(prices)

    portfolio = Portfolio(INITIAL_CASH)

    for timestamp, row in feeds.iterrows():
        signal = check_arbitrage(
            row["exchange_a"],
            row["exchange_b"],
            MIN_SPREAD_PCT,
        )

        if signal:
            pnl = execute_arbitrage(signal, TRADE_SIZE_BTC, FEE_PCT)
            portfolio.apply_trade(pnl)

    return portfolio
