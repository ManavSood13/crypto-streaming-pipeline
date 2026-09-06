from src.utils.logger import get_logger


logger = get_logger("database", "pipeline.log")


INSERT_OHLCV = """
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


def insert_ohlcv_many(connection, records):
    """
    Insert several OHLCV records in one transaction.

    Returns the number of rows actually written. Rows already present
    are skipped by the ON CONFLICT clause and are not counted.
    """

    if not records:
        return 0

    try:
        written = 0

        with connection.cursor() as cursor:
            for record in records:
                cursor.execute(INSERT_OHLCV, record)
                written += cursor.rowcount

        connection.commit()

        # Per-record logging at INFO level made the log file grow
        # without bound, so the detail sits at DEBUG instead.
        for record in records:
            logger.debug(
                "Inserted OHLCV record: %s %s",
                record["symbol"],
                record["bucket_start"]
            )

        skipped = len(records) - written

        if skipped:
            logger.debug(
                "%s duplicate OHLCV record(s) skipped",
                skipped
            )

        return written

    except Exception:
        connection.rollback()

        logger.exception(
            "Failed to insert %s OHLCV record(s)",
            len(records)
        )

        raise
