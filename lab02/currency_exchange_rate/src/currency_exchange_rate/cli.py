import logging
import argparse
import datetime as dt

from . import logger_setup
from . import api
from . import utils

logger_setup.init_logger()
log = logging.getLogger("app.cli")

def check_currency(currency: str) -> str:
    allowed_currencies = ["USD","EUR","RUB","RON","UAH"]
    if not (currency in allowed_currencies):
        log.error(f"Bad currency: {currency}")
        raise argparse.ArgumentTypeError("Bad currency")
    return currency

def iso_date(date_str: str) -> dt.date:
    try:
        return dt.datetime.strptime(date_str, "%Y-%m-%d").date()
    except:
        log.error("Bad date")
        raise argparse.ArgumentTypeError("Bad date")

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("base", type=check_currency, help="Base currency")
    parser.add_argument("quote", type=check_currency, help="Quote currency")
    parser.add_argument("date",nargs="?",type=iso_date,metavar="DATE", help="Date in format YYYY-MM-DD")

    group = parser.add_mutually_exclusive_group()
    group.add_argument("--range", nargs=2, metavar=("START","END"), type=iso_date, help="Date range in format YYYY-MM-DD YYYY-MM-DD")

    parser.add_argument("--api-url", required=True, default="https://api.exchangerate.host", help="Exchange rate API URL")
    parser.add_argument("--api-key", required=True, default=None, help="Exchange rate API key")
    
    return parser

def validate_args(args: argparse.Namespace):
    if args.date is None and args.range is None:
        log.error("date and date range is none")
        raise SystemExit("date and date range is none")
    elif args.date is not None and args.range is not None:
        log.error("date and date range are given both")
        raise SystemExit("date and date range are given both")
    
    if args.range is not None:
        start, end = args.range
        if start >= end:
            log.error(f"starting date {start} is bigger or equal to end date {end}")
            raise SystemExit(f"starting date {start} is bigger or equal to end date {end}")
        
def date_range(start: dt.date, end: dt.date):
    cur = start
    one = dt.timedelta(days=1)
    while cur <= end:
        yield cur
        cur += one
        
def main() -> int:
    args = build_parser().parse_args()
    validate_args(args)
    if args.range is not None:
        responses = []
        start, end = args.range
        for date_i in date_range(start, end):
            responses.append(
                api.fetch_exchange_rate_to_json(
                args.api_url, 
                args.api_key, 
                args.base, 
                args.quote, 
                date_i.isoformat()
                )
            ) 
        utils.save_multiple_responses_in_file(responses,args)
    else:
        utils.save_response_in_file(
            api.fetch_exchange_rate_to_json(
                args.api_url, 
                args.api_key, 
                args.base, 
                args.quote, 
                args.date.isoformat()
            ),
            args
        )


    return 0

if __name__ == "__main__":
    raise SystemExit(main())
