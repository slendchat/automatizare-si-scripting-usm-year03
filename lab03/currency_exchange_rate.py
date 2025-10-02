from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import requests


DEFAULT_BASE_URL = "http://php_apache/"
DATE_FORMAT = "%Y-%m-%d"
TIMEOUT_SECONDS = 10


def project_root() -> Path:
    return Path(__file__).resolve().parent


ROOT_DIR = project_root()
DATA_DIR = ROOT_DIR / "data"
LOG_FILE = ROOT_DIR / "error.log"


def _default_api_key() -> str | None:
    return os.getenv("EXCHANGE_API_KEY") or os.getenv("API_KEY")


def _default_base_url() -> str:
    return (
        os.getenv("EXCHANGE_API_BASE_URL")
        or os.getenv("API_BASE_URL")
        or DEFAULT_BASE_URL
    )


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch a currency exchange rate by calling the lab02 support service "
            "and save the response to disk."
        )
    )
    parser.add_argument("from_currency", help="Three-letter currency code to convert from")
    parser.add_argument("to_currency", help="Three-letter currency code to convert to")
    parser.add_argument(
        "date",
        nargs="?",
        help=f"Date of the rate in {DATE_FORMAT} format",
    )
    parser.add_argument(
        "--range",
        dest="date_range",
        nargs=2,
        metavar=("START", "END"),
        help=f"Inclusive date range in {DATE_FORMAT} format",
    )
    parser.add_argument(
        "--api-key",
        dest="api_key",
        default=_default_api_key(),
        help="API key for the service (defaults to EXCHANGE_API_KEY or API_KEY env variable)",
    )
    parser.add_argument(
        "--base-url",
        dest="base_url",
        default=_default_base_url(),
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

    single_date: str | None = None
    if args.date:
        try:
            requested_date = datetime.strptime(args.date, DATE_FORMAT).date()
        except ValueError as exc:
            raise ValueError(
                f"Invalid date '{args.date}'. Expected format {DATE_FORMAT}."
            ) from exc
        single_date = requested_date.strftime(DATE_FORMAT)

    range_dates: Tuple[str, str] | None = None
    if args.date_range:
        start_raw, end_raw = args.date_range
        try:
            start_date = datetime.strptime(start_raw, DATE_FORMAT).date()
            end_date = datetime.strptime(end_raw, DATE_FORMAT).date()
        except ValueError as exc:
            raise ValueError(
                f"Invalid range '{start_raw} {end_raw}'. Expected format {DATE_FORMAT}."
            ) from exc
        if start_date > end_date:
            raise ValueError("Range START date must be earlier than or equal to END date.")
        range_dates = (
            start_date.strftime(DATE_FORMAT),
            end_date.strftime(DATE_FORMAT),
        )

    if (single_date is None and range_dates is None) or (
        single_date is not None and range_dates is not None
    ):
        raise ValueError("Provide either DATE argument or --range, but not both.")

    if args.api_key is None or not str(args.api_key).strip():
        raise ValueError(
            "API key is required. Provide via --api-key, EXCHANGE_API_KEY or API_KEY env variable."
        )

    base_url = args.base_url.strip()
    if not base_url:
        raise ValueError("Base URL must not be empty.")

    return {
        "from_currency": from_currency,
        "to_currency": to_currency,
        "date": single_date,
        "range": range_dates,
        "api_key": str(args.api_key).strip(),
        "base_url": base_url,
        "timeout": float(args.timeout),
    }


def ensure_directories() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def log_error(message: str) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOG_FILE.open("a", encoding="utf-8") as fh:
        fh.write(f"{datetime.utcnow().isoformat()}Z - {message}\n")


def fetch_exchange_rate(params: dict[str, Any], day: str) -> Dict[str, Any]:
    url = params["base_url"].rstrip("/") + "/"
    query = {
        "from": params["from_currency"],
        "to": params["to_currency"],
        "date": day,
    }
    payload = {"key": params["api_key"]}

    try:
        response = requests.post(url, params=query, data=payload, timeout=params["timeout"])
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(f"HTTP request failed: {exc}") from exc

    try:
        data = response.json()
    except json.JSONDecodeError as exc:
        raise RuntimeError("Service returned invalid JSON response.") from exc

    error_message = data.get("error")
    if error_message:
        raise RuntimeError(f"Service returned an error: {error_message}")

    if "data" not in data:
        raise RuntimeError("Service response missing 'data' field.")

    return data


def daterange(start: str, end: str) -> Iterable[str]:
    start_date = datetime.strptime(start, DATE_FORMAT).date()
    end_date = datetime.strptime(end, DATE_FORMAT).date()
    current = start_date
    step = timedelta(days=1)
    while current <= end_date:
        yield current.strftime(DATE_FORMAT)
        current += step


def save_single_response(params: dict[str, Any], day: str, data: Dict[str, Any]) -> Path:
    ensure_directories()
    filename = f"{params['from_currency']}_{params['to_currency']}_{day}.json"
    destination = DATA_DIR / filename
    with destination.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
    return destination


def save_range_responses(
    params: dict[str, Any], start: str, end: str, responses: List[Dict[str, Any]]
) -> Path:
    ensure_directories()
    filename = (
        f"{params['from_currency']}_{params['to_currency']}_{start}_to_{end}.json"
    )
    destination = DATA_DIR / filename
    with destination.open("w", encoding="utf-8") as fh:
        json.dump(responses, fh, indent=2)
    return destination


def main(argv: List[str]) -> int:
    try:
        args = parse_args(argv)
        params = validate_inputs(args)
        if params["date"]:
            response_data = fetch_exchange_rate(params, params["date"])
            output_file = save_single_response(params, params["date"], response_data)
            rate = response_data.get("data", {}).get("rate")
            print(
                "Saved exchange rate",
                params["from_currency"],
                "->",
                params["to_currency"],
                "for",
                params["date"],
                f"(rate: {rate})" if rate is not None else "",
                "to",
                output_file,
            )
        else:
            start, end = params["range"]
            responses: List[Dict[str, Any]] = []
            for day in daterange(start, end):
                response = fetch_exchange_rate(params, day)
                responses.append(response)
            output_file = save_range_responses(params, start, end, responses)
            print(
                "Saved exchange rates",
                params["from_currency"],
                "->",
                params["to_currency"],
                "for",
                f"{start} to {end}",
                "to",
                output_file,
            )
        return 0
    except Exception as exc:
        message = str(exc)
        print(f"Error: {message}", file=sys.stderr)
        log_error(message)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
