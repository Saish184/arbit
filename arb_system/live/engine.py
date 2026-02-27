from dataclasses import dataclass
from datetime import datetime
from math import sqrt
from typing import Dict, Iterable, List, Optional, Sequence

from live.signals import ArbitrageSignal, detect_arbitrage
from live.state import ExchangeState


@dataclass(frozen=True)
class SpreadObservation:
    observed_at: datetime
    spread_a_to_b_pct: float
    spread_b_to_a_pct: float


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
        self.spread_history: List[SpreadObservation] = []

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

        spread_a_to_b_pct = (quote_b.bid - quote_a.ask) / quote_a.ask
        spread_b_to_a_pct = (quote_a.bid - quote_b.ask) / quote_b.ask
        self.spread_history.append(
            SpreadObservation(
                observed_at=max(quote_a.timestamp, quote_b.timestamp),
                spread_a_to_b_pct=spread_a_to_b_pct,
                spread_b_to_a_pct=spread_b_to_a_pct,
            )
        )

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

    @staticmethod
    def _percentile(values: List[float], percentile: float) -> float:
        if not values:
            return 0.0
        if len(values) == 1:
            return values[0]
        sorted_values = sorted(values)
        rank = (len(sorted_values) - 1) * percentile
        lower = int(rank)
        upper = min(lower + 1, len(sorted_values) - 1)
        if lower == upper:
            return sorted_values[lower]
        weight = rank - lower
        return sorted_values[lower] * (1 - weight) + sorted_values[upper] * weight

    @staticmethod
    def _stddev(values: List[float]) -> float:
        if not values:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((v - mean) ** 2 for v in values) / len(values)
        return sqrt(variance)

    def _compute_persistence_stats(
        self,
        values: List[float],
        timestamps: List[datetime],
        threshold_pct: float,
    ) -> Dict[str, float]:
        runs_ticks: List[int] = []
        runs_seconds: List[float] = []

        in_run = False
        run_start_idx = 0
        run_tick_count = 0

        for idx, spread in enumerate(values):
            if spread > threshold_pct:
                if not in_run:
                    in_run = True
                    run_start_idx = idx
                    run_tick_count = 1
                else:
                    run_tick_count += 1
            elif in_run:
                runs_ticks.append(run_tick_count)
                start_ts = timestamps[run_start_idx]
                end_ts = timestamps[idx - 1]
                runs_seconds.append((end_ts - start_ts).total_seconds())
                in_run = False
                run_tick_count = 0

        if in_run:
            runs_ticks.append(run_tick_count)
            start_ts = timestamps[run_start_idx]
            end_ts = timestamps[len(values) - 1]
            runs_seconds.append((end_ts - start_ts).total_seconds())

        if not runs_ticks:
            return {
                "runs": 0.0,
                "avg_ticks": 0.0,
                "max_ticks": 0.0,
                "avg_seconds": 0.0,
                "max_seconds": 0.0,
            }

        return {
            "runs": float(len(runs_ticks)),
            "avg_ticks": sum(runs_ticks) / len(runs_ticks),
            "max_ticks": float(max(runs_ticks)),
            "avg_seconds": sum(runs_seconds) / len(runs_seconds),
            "max_seconds": max(runs_seconds),
        }

    def get_spread_stats(self, threshold_pct: Optional[float] = None) -> Dict[str, Dict[str, float]]:
        """
        Quantifies cross-exchange spread behavior for both directions.
        """
        threshold = self.min_spread_pct if threshold_pct is None else threshold_pct
        if not self.spread_history:
            empty = {
                "count": 0.0,
                "mean": 0.0,
                "max": 0.0,
                "p95": 0.0,
                "p99": 0.0,
                "volatility": 0.0,
                "pct_above_threshold": 0.0,
                "threshold_pct": threshold,
                "persistence_runs": 0.0,
                "persistence_avg_ticks": 0.0,
                "persistence_max_ticks": 0.0,
                "persistence_avg_seconds": 0.0,
                "persistence_max_seconds": 0.0,
            }
            return {
                "a_to_b": empty,
                "b_to_a": empty,
            }

        timestamps = [s.observed_at for s in self.spread_history]
        a_to_b_values = [s.spread_a_to_b_pct for s in self.spread_history]
        b_to_a_values = [s.spread_b_to_a_pct for s in self.spread_history]

        def _one_direction(values: List[float]) -> Dict[str, float]:
            count = len(values)
            above = [v for v in values if v > threshold]
            persistence = self._compute_persistence_stats(values, timestamps, threshold)
            return {
                "count": float(count),
                "mean": sum(values) / count,
                "max": max(values),
                "p95": self._percentile(values, 0.95),
                "p99": self._percentile(values, 0.99),
                "volatility": self._stddev(values),
                "pct_above_threshold": (len(above) / count) * 100.0,
                "threshold_pct": threshold,
                "persistence_runs": persistence["runs"],
                "persistence_avg_ticks": persistence["avg_ticks"],
                "persistence_max_ticks": persistence["max_ticks"],
                "persistence_avg_seconds": persistence["avg_seconds"],
                "persistence_max_seconds": persistence["max_seconds"],
            }

        return {
            "a_to_b": _one_direction(a_to_b_values),
            "b_to_a": _one_direction(b_to_a_values),
        }
