from src.utils.logger import get_logger


logger = get_logger("database", "pipeline.log")


def insert_ohlcv(connection, record):
    """
    Insert a 10-second OHLCV record into PostgreSQL.
    """

    query = """
        INSERT INTO ohlcv_10s (
            symbol,
            bucket_start,
            open,
            high,
            low,
            close,
            volume,
            trade_count
        )
        VALUES (
            %(symbol)s,
            %(bucket_start)s,
            %(open)s,
            %(high)s,
            %(low)s,
            %(close)s,
            %(volume)s,
            %(trade_count)s
        )
        ON CONFLICT (symbol, bucket_start)
        DO NOTHING
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, record)

        connection.commit()

        logger.info(
            "Inserted OHLCV record: %s %s",
            record["symbol"],
            record["bucket_start"]
        )

    except Exception:
        connection.rollback()

        logger.exception(
            "Failed to insert OHLCV record: %s",
            record
        )

        raise