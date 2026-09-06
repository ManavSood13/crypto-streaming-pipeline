"""
SQL analytics over the 10-second OHLCV table.

Every aggregate is restricted to a trailing time window. Without one the
dashboard re-scans the entire table on each refresh, so its cost grows
with the age of the pipeline rather than with the data being displayed.
"""

# Trailing window used by the dashboard aggregates, in hours.
DEFAULT_WINDOW_HOURS = 24


def _window_clause(column="bucket_start"):
    return f"{column} >= now() - make_interval(hours => %(hours)s)"


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


def get_volume_by_symbol(connection, window_hours=DEFAULT_WINDOW_HOURS):
    """
    Return total and average trading volume for each symbol.
    """

    query = f"""
        SELECT
            symbol,
            SUM(volume) AS total_volume,
            AVG(volume) AS avg_volume_per_candle
        FROM ohlcv_10s
        WHERE {_window_clause()}
        GROUP BY symbol
        ORDER BY total_volume DESC;
    """

    with connection.cursor() as cursor:
        cursor.execute(query, {"hours": window_hours})
        return cursor.fetchall()


def get_price_change(connection, window_hours=DEFAULT_WINDOW_HOURS):
    """
    Return the price change across the trailing window for each symbol.

    The original version compared the first and last candle in the whole
    table, which meant the figure silently became an all-time change and
    cost a full scan plus two sorts on every dashboard refresh.
    """

    query = f"""
        WITH first_last AS (
            SELECT
                symbol,
                (array_agg(close ORDER BY bucket_start ASC))[1]
                    AS first_price,
                (array_agg(close ORDER BY bucket_start DESC))[1]
                    AS latest_price
            FROM ohlcv_10s
            WHERE {_window_clause()}
            GROUP BY symbol
        )

        SELECT
            symbol,
            first_price,
            latest_price,
            latest_price - first_price AS price_change,
            CASE
                WHEN first_price IS NULL OR first_price = 0 THEN NULL
                ELSE ROUND(
                    ((latest_price - first_price) / first_price) * 100,
                    2
                )
            END AS price_change_percent
        FROM first_last
        ORDER BY price_change_percent DESC NULLS LAST;
    """

    with connection.cursor() as cursor:
        cursor.execute(query, {"hours": window_hours})
        return cursor.fetchall()


def get_trading_activity(connection, window_hours=DEFAULT_WINDOW_HOURS):
    """
    Return trading activity metrics for each symbol.
    """

    query = f"""
        SELECT
            symbol,
            SUM(trade_count) AS total_trades,
            ROUND(AVG(trade_count), 2) AS avg_trades_per_candle
        FROM ohlcv_10s
        WHERE {_window_clause()}
        GROUP BY symbol
        ORDER BY total_trades DESC;
    """

    with connection.cursor() as cursor:
        cursor.execute(query, {"hours": window_hours})
        return cursor.fetchall()


def get_volatility(connection, window_hours=DEFAULT_WINDOW_HOURS):
    """
    Return price range and percentage range for each symbol.
    """

    query = f"""
        SELECT
            symbol,
            MAX(high) - MIN(low) AS price_range,
            CASE
                WHEN MIN(low) IS NULL OR MIN(low) = 0 THEN NULL
                ELSE ROUND(
                    ((MAX(high) - MIN(low)) / MIN(low)) * 100,
                    2
                )
            END AS price_range_percent
        FROM ohlcv_10s
        WHERE {_window_clause()}
        GROUP BY symbol
        ORDER BY price_range_percent DESC NULLS LAST;
    """

    with connection.cursor() as cursor:
        cursor.execute(query, {"hours": window_hours})
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


def get_volume_over_time(connection, window_hours=DEFAULT_WINDOW_HOURS):
    """
    Return total trading volume bucketed over the trailing window.

    The bucket width adapts to how much history actually exists. Fixed
    hourly buckets collapsed a freshly started pipeline into a single
    point, which a line chart cannot draw.
    """

    query = f"""
        WITH bounds AS (
            SELECT
                MIN(bucket_start) AS first_seen,
                MAX(bucket_start) AS last_seen
            FROM ohlcv_10s
            WHERE {_window_clause()}
        ),

        step AS (
            SELECT
                first_seen,
                CASE
                    WHEN last_seen - first_seen <= interval '30 minutes'
                        THEN interval '1 minute'
                    WHEN last_seen - first_seen <= interval '3 hours'
                        THEN interval '5 minutes'
                    WHEN last_seen - first_seen <= interval '12 hours'
                        THEN interval '15 minutes'
                    ELSE interval '1 hour'
                END AS width
            FROM bounds
            WHERE first_seen IS NOT NULL
        )

        SELECT
            date_bin(
                step.width,
                ohlcv_10s.bucket_start,
                step.first_seen
            ) AS bucket_time,
            SUM(ohlcv_10s.volume) AS total_volume
        FROM ohlcv_10s, step
        WHERE {_window_clause("ohlcv_10s.bucket_start")}
        GROUP BY bucket_time
        ORDER BY bucket_time;
    """

    with connection.cursor() as cursor:
        cursor.execute(query, {"hours": window_hours})
        return cursor.fetchall()


def get_pipeline_health(connection):
    """
    Return (latest_bucket, candles_last_minute) for the status panel.

    Used to report whether data is actually arriving rather than showing
    a hard coded "active" indicator.
    """

    query = """
        SELECT
            MAX(bucket_start) AS latest_bucket,
            COUNT(*) FILTER (
                WHERE bucket_start >= now() - interval '1 minute'
            ) AS candles_last_minute
        FROM ohlcv_10s;
    """

    with connection.cursor() as cursor:
        cursor.execute(query)
        return cursor.fetchone()
