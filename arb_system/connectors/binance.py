import json
import time
from typing import Dict, Generator, Optional

from websocket import WebSocketConnectionClosedException, WebSocketTimeoutException, create_connection


class BinanceBookTickerClient:
    """
    Streams best bid/ask from Binance bookTicker endpoint.
    """

    WS_BASE = "wss://stream.binance.com:9443/ws"

    def __init__(
        self,
        symbol: str = "btcusdt",
        reconnect_delay_sec: float = 2.0,
        recv_timeout_sec: float = 5.0,
    ) -> None:
        self.symbol = symbol.lower()
        self.reconnect_delay_sec = reconnect_delay_sec
        self.recv_timeout_sec = recv_timeout_sec
        self._stop = False

    @property
    def ws_url(self) -> str:
        return f"{self.WS_BASE}/{self.symbol}@bookTicker"

    def stop(self) -> None:
        self._stop = True

    def stream_quotes(self) -> Generator[Dict[str, float], None, None]:
        """
        Yields normalized quote updates:
        {
            "exchange": "binance",
            "bid": float,
            "ask": float,
            "bid_size": float,
            "ask_size": float
        }
        """
        while not self._stop:
            ws = None
            try:
                ws = create_connection(self.ws_url, timeout=self.recv_timeout_sec)
                while not self._stop:
                    raw = ws.recv()
                    payload = json.loads(raw)
                    quote = self._parse_book_ticker(payload)
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

    def _parse_book_ticker(self, payload: Dict[str, str]) -> Optional[Dict[str, float]]:
        """
        Binance bookTicker payload fields:
        b=best bid, B=best bid size, a=best ask, A=best ask size.
        """
        if "b" not in payload or "a" not in payload:
            return None

        return {
            "exchange": "binance",
            "bid": float(payload["b"]),
            "ask": float(payload["a"]),
            "bid_size": float(payload.get("B", 0.0)),
            "ask_size": float(payload.get("A", 0.0)),
        }
