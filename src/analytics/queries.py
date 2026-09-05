def get_latest_prices(connection):
    """
    Return the latest OHLCV candle for each symbol.
    """

    query = """
        SELECT DISTINCT ON (symbol)
            symbol,
            bucket_start,
            close AS latest_price
        FROM ohlcv_10s
        ORDER BY symbol, bucket_start DESC;
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def get_volume_by_symbol(connection):
    """
    Return total and average trading volume for each symbol.
    """

    query = """
        SELECT
            symbol,
            SUM(volume) AS total_volume,
            AVG(volume) AS avg_volume_per_candle
        FROM ohlcv_10s
        GROUP BY symbol
        ORDER BY total_volume DESC;
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def get_price_change(connection):
    """
    Return price change between the first and latest candle
    for each symbol.
    """

    query = """
        WITH price_data AS (
            SELECT
                symbol,
                FIRST_VALUE(close) OVER (
                    PARTITION BY symbol
                    ORDER BY bucket_start
                ) AS first_price,
                FIRST_VALUE(close) OVER (
                    PARTITION BY symbol
                    ORDER BY bucket_start DESC
                ) AS latest_price
            FROM ohlcv_10s
        )

        SELECT DISTINCT
            symbol,
            first_price,
            latest_price,
            latest_price - first_price AS price_change,
            ROUND(
                ((latest_price - first_price) / first_price) * 100,
                2
            ) AS price_change_percent
        FROM price_data
        ORDER BY price_change_percent DESC;
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def get_trading_activity(connection):
    """
    Return trading activity metrics for each symbol.
    """

    query = """
        SELECT
            symbol,
            SUM(trade_count) AS total_trades,
            ROUND(AVG(trade_count), 2) AS avg_trades_per_candle
        FROM ohlcv_10s
        GROUP BY symbol
        ORDER BY total_trades DESC;
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def get_volatility(connection):
    """
    Return price range and percentage range for each symbol.
    """

    query = """
        SELECT
            symbol,
            MAX(high) - MIN(low) AS price_range,
            ROUND(
                ((MAX(high) - MIN(low)) / MIN(low)) * 100,
                2
            ) AS price_range_percent
        FROM ohlcv_10s
        GROUP BY symbol
        ORDER BY price_range_percent DESC;
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def get_price_history(connection, symbol, limit=60):
    """
    Return recent 10-second OHLCV data for a symbol.
    """

    query = """
        SELECT
            bucket_start,
            open,
            high,
            low,
            close,
            volume
        FROM (
            SELECT
                bucket_start,
                open,
                high,
                low,
                close,
                volume
            FROM ohlcv_10s
            WHERE symbol = %s
            ORDER BY bucket_start DESC
            LIMIT %s
        ) recent_data
        ORDER BY bucket_start ASC;
    """

    with connection.cursor() as cursor:
        cursor.execute(query, (symbol, limit))
        return cursor.fetchall()


def get_total_candles(connection):
    """
    Return the total number of OHLCV candles stored in PostgreSQL.
    """

    query = """
        SELECT COUNT(*)
        FROM ohlcv_10s;
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchone()[0]


def get_price_change_by_symbol(connection):
    """
    Return price change percentage for each symbol.
    """

    query = """
        SELECT
            symbol,
            ROUND(
                ((MAX(close) - MIN(open)) / MIN(open)) * 100,
                2
            ) AS price_change_percent
        FROM ohlcv_10s
        GROUP BY symbol
        ORDER BY price_change_percent DESC;
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()


def get_hourly_volume(connection):
    """
    Return total trading volume by hour.
    """

    query = """
        SELECT
            DATE_TRUNC('hour', bucket_start) AS hour,
            SUM(volume) AS total_volume
        FROM ohlcv_10s
        GROUP BY hour
        ORDER BY hour;
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchall()