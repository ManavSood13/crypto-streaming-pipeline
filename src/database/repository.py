from src.utils.logger import get_logger


logger = get_logger("database", "pipeline.log")


def insert_ohlcv(connection, record):
    """
    Insert a 1-minute OHLCV record into PostgreSQL.
    """

    query = """
        INSERT INTO ohlcv_1m (
            symbol,
            minute,
            open,
            high,
            low,
            close,
            volume,
            trade_count
        )
        VALUES (
            %(symbol)s,
            %(minute)s,
            %(open)s,
            %(high)s,
            %(low)s,
            %(close)s,
            %(volume)s,
            %(trade_count)s
        )
        ON CONFLICT (symbol, minute)
        DO NOTHING
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, record)

        connection.commit()

        logger.info(
            "Inserted OHLCV record: %s %s",
            record["symbol"],
            record["minute"]
        )

    except Exception:
        connection.rollback()

        logger.exception(
            "Failed to insert OHLCV record: %s",
            record
        )

        raise