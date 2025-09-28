import logging
import argparse
import datetime as dt

from . import logger_setup
from . import api

def check_currency(currency: str) -> str:
    pass

def check_date(date_str: str) -> dt.date:
    pass

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    
    return parser

def validate_args(args: argparse.Namespace) -> None:
    pass

def main() -> int:
    logger_setup.init_logger()
    log = logging.getLogger("app.cli")
    args = build_parser().parse_args()


    return 0

if __name__ == "__main__":
    raise SystemExit(main())
