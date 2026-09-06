import os

import psycopg

from src.utils.logger import get_logger


logger = get_logger("database", "pipeline.log")


# Hosted providers (Neon, Supabase, Railway) hand out a single
# connection string, so that takes precedence when present.
DATABASE_URL = os.getenv("DATABASE_URL")


# Otherwise the standard PostgreSQL variables are used. The defaults
# preserve the original local setup.
DB_CONFIG = {
    "dbname": os.getenv("PGDATABASE", "crypto_pipeline"),
    "user": os.getenv("PGUSER", os.getenv("USER", "postgres")),
    "host": os.getenv("PGHOST", "localhost"),
    "port": int(os.getenv("PGPORT", "5432"))
}


_password = os.getenv("PGPASSWORD")

if _password:
    DB_CONFIG["password"] = _password


# Managed databases require TLS; local sockets usually do not.
_sslmode = os.getenv("PGSSLMODE")

if _sslmode:
    DB_CONFIG["sslmode"] = _sslmode


def describe_target():
    """
    Describe the connection target without exposing credentials.
    """

    if DATABASE_URL:
        host = DATABASE_URL.split("@")[-1].split("/")[0]
        return f"{host} (from DATABASE_URL)"

    return f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['dbname']}"


def get_connection():
    """
    Create and return a PostgreSQL database connection.
    """

    try:
        connection = (
            psycopg.connect(DATABASE_URL)
            if DATABASE_URL
            else psycopg.connect(**DB_CONFIG)
        )
        logger.debug("PostgreSQL connection established")
        return connection

    except Exception:
        logger.exception(
            "Failed to connect to PostgreSQL at %s",
            describe_target()
        )
        raise


def is_alive(connection):
    """
    Return True if the connection can still execute statements.
    """

    if connection is None or connection.closed:
        return False

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")

        return True

    except Exception:
        return False


def ensure_connection(connection):
    """
    Return a usable connection, reconnecting if the current one died.

    Long running processes otherwise keep a broken connection forever
    and silently discard everything they try to write.
    """

    if is_alive(connection):
        return connection

    logger.warning("PostgreSQL connection is dead, reconnecting")

    if connection is not None and not connection.closed:
        try:
            connection.close()
        except Exception:
            pass

    return get_connection()
