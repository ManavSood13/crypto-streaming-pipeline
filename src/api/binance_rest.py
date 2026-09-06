"""
Thin REST client for Binance spot prices.

Used for one-off price lookups; the live pipeline uses the WebSocket
stream in `src.ingestion.binance_websocket`.
"""

import requests

from src.utils.logger import get_logger


logger = get_logger("binance_rest", "pipeline.log")


PRICE_URL = "https://data-api.binance.vision/api/v3/ticker/price"

REQUEST_TIMEOUT = 10


SYMBOLS = [
    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT",
    "SOLUSDT",
    "XRPUSDT",
    "ADAUSDT",
    "DOGEUSDT",
    "AVAXUSDT",
    "LINKUSDT",
    "DOTUSDT",
]


def get_price(symbol, timeout=REQUEST_TIMEOUT):
    """
    Return the current price for a single symbol.
    """

    response = requests.get(
        PRICE_URL,
        params={"symbol": symbol},
        timeout=timeout
    )

    response.raise_for_status()

    return response.json()


def get_prices(symbols=None):
    """
    Return current prices for several symbols.

    A failed lookup is logged and skipped rather than aborting the rest.
    """

    results = {}

    for symbol in symbols or SYMBOLS:
        try:
            data = get_price(symbol)
            results[symbol] = float(data["price"])

        except Exception:
            logger.exception("Failed to fetch price for %s", symbol)

    return results


def main():
    for symbol, price in get_prices().items():
        print(f"{symbol}: ${price}")


if __name__ == "__main__":
    main()
