-- Schema for the crypto streaming pipeline.
-- Apply with:  psql -d crypto_pipeline -f sql/schema.sql

CREATE TABLE IF NOT EXISTS ohlcv_10s (
    symbol VARCHAR(20) NOT NULL,
    bucket_start TIMESTAMPTZ NOT NULL,
    open NUMERIC NOT NULL,
    high NUMERIC NOT NULL,
    low NUMERIC NOT NULL,
    close NUMERIC NOT NULL,
    volume NUMERIC NOT NULL,
    trade_count INTEGER NOT NULL,
    PRIMARY KEY (symbol, bucket_start)
);

-- Supports the time-windowed dashboard aggregates.
CREATE INDEX IF NOT EXISTS ohlcv_10s_bucket_start_idx
    ON ohlcv_10s (bucket_start DESC);
