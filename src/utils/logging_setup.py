import logging
import os


def setup_logging():
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(filename="logs/app.log", level=logging.INFO, format="%(message)s")
    logger = logging.getLogger("voice_search")
    logger.propagate = False  # prevents log messages from being passed to the root logger (avoids duplicate logs)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.FileHandler("logs/voice_search.log")
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)
    return logger
