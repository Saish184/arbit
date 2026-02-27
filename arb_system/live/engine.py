from typing import Dict, Iterable, List, Optional, Sequence

from live.signals import ArbitrageSignal, detect_arbitrage
from live.state import ExchangeState


class LiveEngine:
    """
    Real-time orchestration skeleton.
    Networking/connectors are intentionally out of scope for this layer.
    """

    def __init__(
        self,
        exchanges: Sequence[str] = ("binance", "coinbase"),
        min_spread_pct: float = 0.001,
        total_cost_pct: float = 0.0,
        safety_pct: float = 0.0,
    ) -> None:
        if len(exchanges) != 2:
            raise ValueError("LiveEngine currently supports exactly two exchanges.")

        self.exchanges = tuple(exchanges)
        self.state = ExchangeState()
        self.min_spread_pct = min_spread_pct
        self.total_cost_pct = total_cost_pct
        self.safety_pct = safety_pct

        self.ticks_processed = 0
        self.opportunities_seen = 0
        self.signal_history: List[ArbitrageSignal] = []

    def process_quote_update(
        self,
        exchange: str,
        bid: float,
        ask: float,
        bid_size: float = 0.0,
        ask_size: float = 0.0,
    ) -> Optional[ArbitrageSignal]:
        self.ticks_processed += 1
        self.state.update(
            exchange=exchange,
            bid=bid,
            ask=ask,
            bid_size=bid_size,
            ask_size=ask_size,
        )

        quote_a = self.state.get(self.exchanges[0])
        quote_b = self.state.get(self.exchanges[1])
        if quote_a is None or quote_b is None:
            return None

        signal = detect_arbitrage(
            quote_a=quote_a,
            quote_b=quote_b,
            min_spread_pct=self.min_spread_pct,
            total_cost_pct=self.total_cost_pct,
            safety_pct=self.safety_pct,
        )
        if signal:
            self.opportunities_seen += 1
            self.signal_history.append(signal)

        return signal

    def run(self, updates: Iterable[Dict[str, float]]) -> List[ArbitrageSignal]:
        """
        Consume normalized quote updates of form:
        {
            "exchange": str,
            "bid": float,
            "ask": float,
            "bid_size": float (optional),
            "ask_size": float (optional),
        }
        """

        signals: List[ArbitrageSignal] = []
        for update in updates:
            signal = self.process_quote_update(
                exchange=str(update["exchange"]),
                bid=float(update["bid"]),
                ask=float(update["ask"]),
                bid_size=float(update.get("bid_size", 0.0)),
                ask_size=float(update.get("ask_size", 0.0)),
            )
            if signal:
                signals.append(signal)

        return signals
