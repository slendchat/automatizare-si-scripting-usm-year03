import logging
import argparse
import datetime as dt

from . import logger_setup
from . import api

def check_currency(currency: str) -> str:

    return currency

def iso_date(date_str: str) -> dt.date:
    return dt.datetime.strptime(date_str, "%Y-%m-%d").date()

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("base", type=check_currency, help="Base currency")
    parser.add_argument("quote", type=check_currency, help="Quote currency")
    parser.add_argument("date",nargs="?",type=iso_date,metavar="DATE", help="Date in format YYYY-MM-DD")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--range", nargs=2, metavar=("START","END"), type=iso_date, help="Date range in format YYYY-MM-DD YYYY-MM-DD")

    parser.add_argument("--api-url", default="https://api.exchangerate.host", help="Exchange rate API URL")
    parser.add_argument("--api-key", default=None, help="Exchange rate API key")
    
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
