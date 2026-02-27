from queue import Empty, Queue
from threading import Thread
from typing import Dict

from connectors.binance import BinanceBookTickerClient
from connectors.coinbase import CoinbaseTickerClient
from live.engine import LiveEngine


def _stream_worker(client, updates_queue: Queue) -> None:
    for update in client.stream_quotes():
        updates_queue.put(update)


def run_live_session():
    engine = LiveEngine(
        exchanges=("binance", "coinbase"),
        min_spread_pct=0.001,
        total_cost_pct=0.0,
        safety_pct=0.0,
    )
    binance_client = BinanceBookTickerClient(symbol="btcusdt")
    coinbase_client = CoinbaseTickerClient(product_id="BTC-USD")
    updates_queue: Queue[Dict[str, float]] = Queue()

    binance_thread = Thread(
        target=_stream_worker,
        args=(binance_client, updates_queue),
        daemon=True,
    )
    coinbase_thread = Thread(
        target=_stream_worker,
        args=(coinbase_client, updates_queue),
        daemon=True,
    )
    binance_thread.start()
    coinbase_thread.start()

    print("Starting Binance + Coinbase live streams. Press Ctrl+C to stop.\n")

    try:
        while True:
            try:
                update = updates_queue.get(timeout=1.0)
            except Empty:
                continue

            signal = engine.process_quote_update(
                exchange=update["exchange"],
                bid=update["bid"],
                ask=update["ask"],
                bid_size=update["bid_size"],
                ask_size=update["ask_size"],
            )

            print(
                f"[QUOTE] {update['exchange']} "
                f"bid={update['bid']:.2f} ask={update['ask']:.2f} "
                f"bid_sz={update['bid_size']:.5f} ask_sz={update['ask_size']:.5f}"
            )

            if signal:
                print(
                    f"[SIGNAL] {signal.direction} "
                    f"buy={signal.buy_exchange}@{signal.buy_price:.2f} "
                    f"sell={signal.sell_exchange}@{signal.sell_price:.2f} "
                    f"spread={signal.spread_pct * 100:.4f}% "
                    f"threshold={signal.threshold_pct * 100:.4f}%"
                )
    except KeyboardInterrupt:
        binance_client.stop()
        coinbase_client.stop()
        print("\nInterrupted by user.")

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

    stats = engine.get_spread_stats()

    def _print_direction(label: str, direction_stats):
        print(f"\n[{label}]")
        print(f"Samples: {int(direction_stats['count'])}")
        print(f"Mean spread: {direction_stats['mean'] * 100:.5f}%")
        print(f"Max spread: {direction_stats['max'] * 100:.5f}%")
        print(f"P95 spread: {direction_stats['p95'] * 100:.5f}%")
        print(f"P99 spread: {direction_stats['p99'] * 100:.5f}%")
        print(f"Spread volatility (std): {direction_stats['volatility'] * 100:.5f}%")
        print(
            f"% time spread > {direction_stats['threshold_pct'] * 100:.4f}%: "
            f"{direction_stats['pct_above_threshold']:.2f}%"
        )
        print(
            "Persistence when above threshold: "
            f"runs={int(direction_stats['persistence_runs'])}, "
            f"avg_ticks={direction_stats['persistence_avg_ticks']:.2f}, "
            f"max_ticks={int(direction_stats['persistence_max_ticks'])}, "
            f"avg_seconds={direction_stats['persistence_avg_seconds']:.3f}, "
            f"max_seconds={direction_stats['persistence_max_seconds']:.3f}"
        )

    print("\n=== SPREAD MEASUREMENT ===")
    _print_direction("BUY_A_SELL_B (binance -> coinbase)", stats["a_to_b"])
    _print_direction("BUY_B_SELL_A (coinbase -> binance)", stats["b_to_a"])


if __name__ == "__main__":
    run_live_session()
