import logging

logger = logging.getLogger("app.api")


def testing_api() -> None:
    logger.error("logger test from api")
