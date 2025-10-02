from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple

import requests


DEFAULT_BASE_URL = "http://localhost:8080/"
DATE_FORMAT = "%Y-%m-%d"
TIMEOUT_SECONDS = 10


def project_root() -> Path:
    return Path(__file__).resolve().parent


ROOT_DIR = project_root()
DATA_DIR = ROOT_DIR / "data"
LOG_FILE = ROOT_DIR / "error.log"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch currency exchange rates by calling the lab02 support service "
            "and save the responses to disk."
        )
    )
    parser.add_argument("from_currency", help="Three-letter currency code to convert from")
    parser.add_argument("to_currency", help="Three-letter currency code to convert to")
    parser.add_argument(
        "date",
        help=f"Date or start of range in {DATE_FORMAT} format",
    )
    parser.add_argument(
        "--end-date",
        dest="end_date",
        help=f"Optional end date for range in {DATE_FORMAT} format (inclusive)",
    )
    parser.add_argument(
        "--api-key",
        dest="api_key",
        default=os.getenv("EXCHANGE_API_KEY"),
        help="API key for the service (defaults to EXCHANGE_API_KEY env variable)",
    )
    parser.add_argument(
        "--base-url",
        dest="base_url",
        default=os.getenv("EXCHANGE_API_BASE_URL", DEFAULT_BASE_URL),
        help="Base URL for the service (override for custom setups)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=TIMEOUT_SECONDS,
        help="HTTP request timeout in seconds (default: %(default)s)",
    )
    return parser.parse_args(argv)


def validate_inputs(args: argparse.Namespace) -> dict[str, Any]:
    from_currency = args.from_currency.strip().upper()
    to_currency = args.to_currency.strip().upper()

    try:
        start_date = datetime.strptime(args.date, DATE_FORMAT).date()
    except ValueError as exc:
        raise ValueError(f"Invalid date '{args.date}'. Expected format {DATE_FORMAT}.") from exc

    if args.end_date:
        try:
            end_date = datetime.strptime(args.end_date, DATE_FORMAT).date()
        except ValueError as exc:
            raise ValueError(
                f"Invalid end date '{args.end_date}'. Expected format {DATE_FORMAT}."
            ) from exc
    else:
        end_date = start_date

    if end_date < start_date:
        raise ValueError("End date must be on or after the start date.")

    if args.api_key is None or not args.api_key.strip():
        raise ValueError("API key is required. Provide via --api-key or EXCHANGE_API_KEY env variable.")

    base_url = args.base_url.strip()
    if not base_url:
        raise ValueError("Base URL must not be empty.")

    date_range = _build_date_range(start_date, end_date)

    return {
        "from_currency": from_currency,
        "to_currency": to_currency,
        "dates": date_range,
        "api_key": args.api_key.strip(),
        "base_url": base_url,
        "timeout": float(args.timeout),
    }


def _build_date_range(start_date: date, end_date: date) -> list[str]:
    current = start_date
    dates: list[str] = []
    while current <= end_date:
        dates.append(current.strftime(DATE_FORMAT))
        current += timedelta(days=1)
    return dates


def ensure_directories() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def log_error(message: str) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as fh:
        fh.write(f"{datetime.utcnow().isoformat()}Z - {message}\n")


def fetch_exchange_rate(params: dict[str, Any], date_value: str) -> Dict[str, Any]:
    url = params["base_url"].rstrip("/") + "/"
    query = {
        "from": params["from_currency"],
        "to": params["to_currency"],
        "date": date_value,
    }
    payload = {"key": params["api_key"]}

    try:
        response = requests.post(url, params=query, data=payload, timeout=params["timeout"])
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(f"HTTP request failed for {date_value}: {exc}") from exc

    try:
        data = response.json()
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Service returned invalid JSON response for {date_value}.") from exc

    error_message = data.get("error")
    if error_message:
        raise RuntimeError(f"Service returned an error for {date_value}: {error_message}")

    if "data" not in data:
        raise RuntimeError(f"Service response missing 'data' field for {date_value}.")

    return data


def save_response(params: dict[str, Any], date_value: str, data: Dict[str, Any]) -> Path:
    ensure_directories()
    filename = f"{params['from_currency']}_{params['to_currency']}_{date_value}.json"
    destination = DATA_DIR / filename
    with destination.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
    return destination


def print_summary(results: Iterable[Tuple[str, Path, Any]]) -> None:
    for date_value, output_file, rate in results:
        rate_fragment = f" (rate: {rate})" if rate is not None else ""
        print(
            "Saved exchange rate",
            date_value,
            "to",
            output_file,
            rate_fragment,
        )


def main(argv: list[str]) -> int:
    try:
        args = parse_args(argv)
        params = validate_inputs(args)
        results: list[Tuple[str, Path, Any]] = []

        for date_value in params["dates"]:
            response_data = fetch_exchange_rate(params, date_value)
            output_file = save_response(params, date_value, response_data)
            rate = response_data.get("data", {}).get("rate")
            results.append((date_value, output_file, rate))

        print_summary(results)
        return 0
    except Exception as exc:
        message = str(exc)
        print(f"Error: {message}", file=sys.stderr)
        log_error(message)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
