from typing import Any

from ._constants import LOGGER_NAME, PRINT_LEVEL


def get_logger_config() -> dict[str, Any]:
    """Get the logger configuration with handler, formatter and filter."""
    handler_name = "console"
    color_formatter_name = "color"
    filter_name = "status_filter"

    config: dict[str, Any] = {
        "version": 1,
        "loggers": {
            LOGGER_NAME: {
                "handlers": [handler_name],
                "level": PRINT_LEVEL,
                "filters": [filter_name],
            },
        },
        "handlers": {
            handler_name: {
                "class": "logging.StreamHandler",
                "formatter": color_formatter_name,
            },
        },
        "formatters": {
            color_formatter_name: {
                "()": "meta.logger.ColorFormatter",
            },
        },
        "filters": {filter_name: {"()": "meta.logger.LogStatusFilter"}},
    }

    return config
