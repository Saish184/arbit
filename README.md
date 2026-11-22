# Årbit: cross-exchange crypto arbitrage research system

A Python research system for studying cross-exchange BTC arbitrage: **is there a spread between two venues, is it big enough to beat fees, and how long does it last?** It has two modes: a historical backtest and a live spread monitor that streams real order-book quotes.

> Status: research prototype. It detects and measures opportunities and simulates fills. It does **not** place real orders.

## What it does

**1. Live spread monitor** (`main_live.py`)
- Streams best bid/ask from **Binance** (`btcusdt@bookTicker`) and **Coinbase** (`BTC-USD` ticker) over websockets, one thread per venue, with auto-reconnect.
- Normalises quotes into one format and keeps the latest quote per exchange (`live/state.py`).
- Checks *executable* prices in both directions (buy on the ask, sell on the bid) against a threshold of `min_spread + costs + safety margin` (`live/signals.py`).
- On Ctrl+C, prints spread statistics per direction: mean, max, p95/p99, volatility, % of time above the threshold, and **persistence** (how many ticks and seconds an opportunity survives).

**2. Historical backtest** (`main.py`)
- Loads 1-minute BTC candles, builds two simulated venues from them, detects spreads above `MIN_SPREAD_PCT`, simulates fee-adjusted fills and tracks PnL in a portfolio (`backtest/`, `strategy/`, `execution/`, `portfolio/`).

## Architecture
```
connectors/  (binance, coinbase websocket clients)
     │  normalised quotes {exchange, bid, ask, sizes}
     ▼
live/state.py ──► live/signals.py ──► live/engine.py ──► spread stats
                  (ask→bid check,      (orchestration,
                   cost-aware)          history, metrics)

data/loader.py ─► data/feeds.py ─► strategy/arbitrage.py ─► execution/simulator.py ─► portfolio/
(1-min candles)   (2 simulated venues)  (threshold check)     (fees, fills)              (PnL)
```

## Run it
```bash
cd arb_system
pip install -r requirements.txt
python main_live.py                       # live monitor, Ctrl+C for the summary
BTC_CSV_PATH=/path/to/btcusd_1-min_data.csv python main.py   # backtest
```
The backtest expects a CSV with `Timestamp` (unix seconds) and `Close` columns, e.g. the Kaggle "Bitcoin Historical Data" 1-minute set. Data files are not committed.

## What I found (and the known limitations)
- **USD vs USDT is not arbitrage.** A 20-second live run showed a constant ~0.17% "spread", with every tick flagged as an opportunity. Binance quotes BTC in USDT and Coinbase in USD, so the engine is mostly measuring the USDT/USD rate. Next step: convert with a live USDT/USD quote, or compare the same quote currency on both venues.
- **The backtest venues are synthetic.** Both prices come from one series with a fixed 0.1% offset plus noise, so the backtest tests the plumbing (signals, fees, PnL), not whether real arbitrage exists. On the last 200k minutes it made ~99.6k trades for about $8 total PnL on 0.01 BTC per trade: the fees eat almost everything, which is the realistic lesson.
- No latency, order-book depth or partial-fill model yet; `execution/fills.py`, `backtest/metrics.py` and `portfolio/risk.py` are stubs.
- The backtest loops row by row (`iterrows`), which is slow on the full ~7M-row history. Vectorising it is an easy win.

## Roadmap
1. Quote-currency normalisation (USDT/USD) so live signals are real.
2. Depth-aware fills using bid/ask sizes, plus latency assumptions.
3. Backtest on *recorded* live quotes instead of synthetic venues.
4. Metrics: Sharpe, drawdown, hit rate, opportunity half-life.

Built with Python, pandas, NumPy and websocket-client.
