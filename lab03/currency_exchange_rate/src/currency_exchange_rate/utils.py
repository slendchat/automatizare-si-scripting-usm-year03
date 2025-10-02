import logging
from pathlib import Path
import json

log = logging.getLogger("app.utils")

import logging
from pathlib import Path
import json

log = logging.getLogger("app.utils")

def ensure_data_dir_exists(data_dir: str | Path) -> Path:
    data_path = Path(data_dir).resolve()
    data_path.mkdir(parents=True, exist_ok=True)
    return data_path

def save_response_in_file(data: dict, args) -> Path:
    data_dir = ensure_data_dir_exists(args.data_dir)
    filename = f"{args.base}-{args.quote}_currency-rate_{args.date}.json"
    destination_file = data_dir / filename
    with destination_file.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
    return destination_file

def save_multiple_responses_in_file(data: list[dict], args) -> Path:
    data_dir = ensure_data_dir_exists(args.data_dir)
    start, end = args.range
    filename = f"{args.base}-{args.quote}_currency-rate_{start}_{end}.json"
    destination_file = data_dir / filename
    with destination_file.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
    return destination_file
