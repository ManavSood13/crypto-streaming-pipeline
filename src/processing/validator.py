from src.utils.logger import get_logger


logger = get_logger("validator", "pipeline.log")


def validate_trade(trade):
    """
    Validate a transformed trade.
    """

    # Check required fields
    required_fields = [
        "symbol",
        "price",
        "quantity",
        "trade_time",
    ]

    for field in required_fields:
        if field not in trade or trade[field] is None:
            logger.warning(
                "Trade rejected: missing %s",
                field
            )
            return False

    # Validate symbol
    if not trade["symbol"]:
        logger.warning("Trade rejected: missing symbol")
        return False

    # Validate price
    if trade["price"] <= 0:
        logger.warning(
            "Trade rejected: invalid price for %s",
            trade["symbol"]
        )
        return False

    # Validate quantity
    if trade["quantity"] <= 0:
        logger.warning(
            "Trade rejected: invalid quantity for %s",
            trade["symbol"]
        )
        return False

    return True