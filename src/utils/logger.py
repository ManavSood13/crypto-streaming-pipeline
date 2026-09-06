import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


LOG_DIR = Path(__file__).resolve().parents[2] / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)


LOG_FORMAT = (
    "%(asctime)s - %(levelname)s - "
    "[%(name)s:%(lineno)d] - %(message)s"
)


LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Rotate so a long running pipeline cannot fill the disk.
MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", 5 * 1024 * 1024))
BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 3))


def get_logger(name, log_file):
    logger = logging.getLogger(name)

    if logger.handlers:
        return logger

    logger.setLevel(
        getattr(logging, LOG_LEVEL, logging.INFO)
    )

    formatter = logging.Formatter(LOG_FORMAT)

    file_handler = RotatingFileHandler(
        LOG_DIR / log_file,
        maxBytes=MAX_BYTES,
        backupCount=BACKUP_COUNT,
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.propagate = False

    return logger
