from src.utils.logger import get_logger


logger = get_logger("validator", "pipeline.log")


def validate_trade(trade):
    """
    Validate a transformed trade.
    """

    if not trade["symbol"]:
        logger.warning("Trade rejected: missing symbol")
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

    if trade["trade_time"] is None:
        logger.warning(
            "Trade rejected: missing trade time for %s",
            trade["symbol"]
        )
        return False

    return True