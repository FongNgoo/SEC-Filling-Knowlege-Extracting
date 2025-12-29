# config/logging_config.py
import logging
import os
from config.settings import OUTPUT_DIR

def setup_logger(log_level=logging.INFO):
    """
    Global logging configuration.
    Must be called ONCE at program start.
    """

    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    log_file = os.path.join(OUTPUT_DIR, "filing_fails.log")

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.FileHandler(log_file, mode="w", encoding="utf-8"),
            logging.StreamHandler()  # console log
        ]
    )

    logging.getLogger(__name__).info("Logger initialized")
