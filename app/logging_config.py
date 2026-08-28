import logging
import logging.handlers
import os

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")


def setup_logging():
    os.makedirs(LOG_DIR, exist_ok=True)

    logger = logging.getLogger("churn_api")
    logger.setLevel(logging.INFO)

    # Prevent duplicate handlers if this gets called more than once
    # (e.g. due to --reload re-importing the module)
    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    file_handler = logging.handlers.RotatingFileHandler(
        LOG_FILE, maxBytes=1_000_000, backupCount=3
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


logger = setup_logging()
