from datetime import datetime

from src.utils.logger import get_logger


logger = get_logger("validator", "pipeline.log")


REQUIRED_FIELDS = (
    "symbol",
    "price",
    "quantity",
    "trade_time",
)


def validate_trade(trade):
    """
    Validate a transformed trade.
    """

    for field in REQUIRED_FIELDS:
        if trade.get(field) is None:
            logger.warning(
                "Trade rejected: missing %s",
                field
            )
            return False

    if not trade["symbol"]:
        logger.warning("Trade rejected: missing symbol")
        return False

    if not isinstance(trade["trade_time"], datetime):
        logger.warning(
            "Trade rejected: invalid trade_time for %s",
            trade["symbol"]
        )
        return False

    if trade["price"] <= 0:
        logger.warning(
            "Trade rejected: invalid price for %s",
            trade["symbol"]
        )
        return False

    if trade["quantity"] <= 0:
        logger.warning(
            "Trade rejected: invalid quantity for %s",
            trade["symbol"]
        )
        return False

    return True
