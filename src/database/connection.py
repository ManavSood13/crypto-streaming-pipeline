import psycopg

from src.utils.logger import get_logger


logger = get_logger("database", "pipeline.log")


DB_CONFIG = {
    "dbname": "crypto_pipeline",
    "user": "manavsood",
    "host": "localhost",
    "port": 5432
}


def get_connection():
    """
    Create and return a PostgreSQL database connection.
    """

    try:
        connection = psycopg.connect(**DB_CONFIG)
        logger.info("PostgreSQL connection established 🥳")
        return connection

    except Exception:
        logger.exception("Failed to connect to PostgreSQL 😭")
        raise