"""Validators for the governance application."""

from logger import get_app_logger


def main() -> None:
    """Start the validators application."""
    logger = get_app_logger()
    logger.info("Hello from governance!")
