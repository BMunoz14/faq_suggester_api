# --- filepath: app/logging_config.py ---
import logging
from logging.config import dictConfig

def setup_logging(level: str = "DEBUG") -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "std": {
                    "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "std",
                    "level": level,
                }
            },
            "root": {"handlers": ["console"], "level": level},
        }
    )

setup_logging()
logger = logging.getLogger("app")