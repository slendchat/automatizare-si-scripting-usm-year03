import logging

from . import logger_setup
from . import api

def main() -> int:
    logger_setup.init_logger()
    log = logging.getLogger("app.cli")
    log.error("logger test from cli")
    api.testing_api()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
