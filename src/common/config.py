# ruff: noqa
import logging.config


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "[%(asctime)s] %(levelname)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        # "console": {
        #     "class": "logging.StreamHandler",
        #     "formatter": "standard",
        #     "level": "DEBUG",
        # },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "standard",
            "mode": "a",
            "filename": "shell.log",
            "maxBytes": 5 * 1024 * 1024,  # 5 MB before rotating
            "backupCount": 5,
            "level": "DEBUG",
        },
    },
    "loggers": {
        "": {
            # "handlers": ["console", "file"],
            "handlers": ["file"],
            "level": "INFO",
            "propagate": True,
        }
    },
}
