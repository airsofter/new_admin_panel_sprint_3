import logging
import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "detailed": {
            "format": "[{asctime}] {levelname} {name} ({filename}:{funcName}:{lineno}): {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "detailed",
        },
    },
    "loggers": {
        "etl": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("etl")
