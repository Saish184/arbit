import json
import time
from typing import Dict, Generator, Optional

from websocket import WebSocketConnectionClosedException, WebSocketTimeoutException, create_connection


class CoinbaseTickerClient:
    """
    Streams best bid/ask from Coinbase Advanced Trade feed (ticker channel).
    """

    WS_URL = "wss://ws-feed.exchange.coinbase.com"

    def __init__(
        self,
        product_id: str = "BTC-USD",
        reconnect_delay_sec: float = 2.0,
        recv_timeout_sec: float = 5.0,
    ) -> None:
        self.product_id = product_id.upper()
        self.reconnect_delay_sec = reconnect_delay_sec
        self.recv_timeout_sec = recv_timeout_sec
        self._stop = False

    def stop(self) -> None:
        self._stop = True

    def stream_quotes(self) -> Generator[Dict[str, float], None, None]:
        """
        Yields normalized quote updates:
        {
            "exchange": "coinbase",
            "bid": float,
            "ask": float,
            "bid_size": float,
            "ask_size": float
        }
        """
        subscribe_message = {
            "type": "subscribe",
            "channels": [{"name": "ticker", "product_ids": [self.product_id]}],
        }

        while not self._stop:
            ws = None
            try:
                ws = create_connection(self.WS_URL, timeout=self.recv_timeout_sec)
                ws.send(json.dumps(subscribe_message))

                while not self._stop:
                    raw = ws.recv()
                    payload = json.loads(raw)
                    quote = self._parse_ticker(payload)
                    if quote is not None:
                        yield quote
            except (WebSocketTimeoutException, WebSocketConnectionClosedException, OSError):
                time.sleep(self.reconnect_delay_sec)
            finally:
                if ws is not None:
                    try:
                        ws.close()
                    except OSError:
                        pass

    def _parse_ticker(self, payload: Dict[str, str]) -> Optional[Dict[str, float]]:
        if payload.get("type") != "ticker":
            return None
        if payload.get("product_id") != self.product_id:
            return None
        if "best_bid" not in payload or "best_ask" not in payload:
            return None

        return {
            "exchange": "coinbase",
            "bid": float(payload["best_bid"]),
            "ask": float(payload["best_ask"]),
            "bid_size": 0.0,
            "ask_size": 0.0,
        }
