from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Dict, Optional


@dataclass(frozen=True)
class ExchangeQuote:
    exchange: str
    bid: float
    ask: float
    bid_size: float
    ask_size: float
    timestamp: datetime

    @property
    def is_valid(self) -> bool:
        return self.bid > 0 and self.ask > 0 and self.ask >= self.bid


class ExchangeState:
    """
    In-memory best bid/ask state keyed by exchange name.
    """

    def __init__(self) -> None:
        self._quotes: Dict[str, ExchangeQuote] = {}

    def update(
        self,
        exchange: str,
        bid: float,
        ask: float,
        bid_size: float = 0.0,
        ask_size: float = 0.0,
        timestamp: Optional[datetime] = None,
    ) -> ExchangeQuote:
        quote = ExchangeQuote(
            exchange=exchange,
            bid=bid,
            ask=ask,
            bid_size=bid_size,
            ask_size=ask_size,
            timestamp=timestamp or datetime.now(timezone.utc),
        )
        self._quotes[exchange] = quote
        return quote

    def get(self, exchange: str) -> Optional[ExchangeQuote]:
        return self._quotes.get(exchange)

    def snapshot(self) -> Dict[str, ExchangeQuote]:
        return dict(self._quotes)
