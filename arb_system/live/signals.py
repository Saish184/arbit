from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from live.state import ExchangeQuote


@dataclass(frozen=True)
class ArbitrageSignal:
    direction: str
    buy_exchange: str
    sell_exchange: str
    buy_price: float
    sell_price: float
    spread_pct: float
    threshold_pct: float
    observed_at: datetime


def detect_arbitrage(
    quote_a: ExchangeQuote,
    quote_b: ExchangeQuote,
    min_spread_pct: float,
    total_cost_pct: float = 0.0,
    safety_pct: float = 0.0,
) -> Optional[ArbitrageSignal]:
    """
    Compare executable prices:
    - Buy on ask
    - Sell on bid
    """

    if not quote_a.is_valid or not quote_b.is_valid:
        return None

    threshold_pct = min_spread_pct + total_cost_pct + safety_pct

    # Direction 1: buy A, sell B
    spread_a_to_b = (quote_b.bid - quote_a.ask) / quote_a.ask
    if spread_a_to_b > threshold_pct:
        return ArbitrageSignal(
            direction="BUY_A_SELL_B",
            buy_exchange=quote_a.exchange,
            sell_exchange=quote_b.exchange,
            buy_price=quote_a.ask,
            sell_price=quote_b.bid,
            spread_pct=spread_a_to_b,
            threshold_pct=threshold_pct,
            observed_at=max(quote_a.timestamp, quote_b.timestamp),
        )

    # Direction 2: buy B, sell A
    spread_b_to_a = (quote_a.bid - quote_b.ask) / quote_b.ask
    if spread_b_to_a > threshold_pct:
        return ArbitrageSignal(
            direction="BUY_B_SELL_A",
            buy_exchange=quote_b.exchange,
            sell_exchange=quote_a.exchange,
            buy_price=quote_b.ask,
            sell_price=quote_a.bid,
            spread_pct=spread_b_to_a,
            threshold_pct=threshold_pct,
            observed_at=max(quote_a.timestamp, quote_b.timestamp),
        )

    return None
