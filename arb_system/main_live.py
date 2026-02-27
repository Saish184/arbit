import random

from live.engine import LiveEngine


def generate_random_updates(num_ticks: int = 500, start_price: float = 100_000.0):
    """
    Emit alternating quote updates for two exchanges with pure random noise.
    """
    exchanges = ("binance", "coinbase")
    mid_prices = {
        "binance": start_price,
        "coinbase": start_price,
    }

    for i in range(num_ticks):
        exchange = exchanges[i % 2]

        # Random walk on mid price.
        mid_prices[exchange] += random.gauss(0.0, 10.0)
        mid = max(100.0, mid_prices[exchange])

        # Random positive micro-spread around the mid.
        half_spread = random.uniform(0.5, 3.0)
        bid = mid - half_spread
        ask = mid + half_spread

        yield {
            "exchange": exchange,
            "bid": bid,
            "ask": ask,
            "bid_size": random.uniform(0.1, 2.0),
            "ask_size": random.uniform(0.1, 2.0),
        }


def run_live_session(num_ticks: int = 500):
    engine = LiveEngine(
        exchanges=("binance", "coinbase"),
        min_spread_pct=0.001,
        total_cost_pct=0.0,
        safety_pct=0.0,
    )

    for update in generate_random_updates(num_ticks=num_ticks):
        signal = engine.process_quote_update(
            exchange=update["exchange"],
            bid=update["bid"],
            ask=update["ask"],
            bid_size=update["bid_size"],
            ask_size=update["ask_size"],
        )
        if signal:
            print(
                f"[SIGNAL] {signal.direction} "
                f"buy={signal.buy_exchange}@{signal.buy_price:.2f} "
                f"sell={signal.sell_exchange}@{signal.sell_price:.2f} "
                f"spread={signal.spread_pct * 100:.4f}% "
                f"threshold={signal.threshold_pct * 100:.4f}%"
            )

    print("\n=== LIVE SESSION SUMMARY ===")
    print(f"Ticks processed: {engine.ticks_processed}")
    print(f"Opportunities seen: {engine.opportunities_seen}")
    if engine.signal_history:
        avg_spread = sum(s.spread_pct for s in engine.signal_history) / len(
            engine.signal_history
        )
        print(f"Average detected spread: {avg_spread * 100:.4f}%")
    else:
        print("Average detected spread: n/a")


if __name__ == "__main__":
    run_live_session(num_ticks=500)
