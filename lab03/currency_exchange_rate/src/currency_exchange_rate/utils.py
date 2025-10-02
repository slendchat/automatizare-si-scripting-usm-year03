import logging
from pathlib import Path
import json

log = logging.getLogger("app.utils")

def ensure_data_dir_exists() -> Path:
  DATA_DIR = Path(__file__).resolve().parents[2] / "data"
  DATA_DIR.mkdir(parents = True, exist_ok=True)
  return DATA_DIR

def save_response_in_file(data:str,args) -> Path:
  DATA_DIR = ensure_data_dir_exists()
  DATA_DIR.mkdir(parents = True, exist_ok=True)
  filename = f"{args.base}-{args.quote}_currency-rate_{args.date}.json"
  destination_file = DATA_DIR / filename 
  with destination_file.open("w", encoding="utf-8") as fh:
    json.dump(data, fh, indent=2)
  return destination_file

def save_multiple_responses_in_file(data:list[dict[str,any]],args) -> Path:
  DATA_DIR = ensure_data_dir_exists()
  start, end = args.range
  filename = f"{args.base}-{args.quote}_currency-rate_{start}_{end}.json"
  destination_file = DATA_DIR / filename 
  with destination_file.open("w", encoding="utf-8") as fh:
    json.dump(data, fh, indent=2)
  return destination_file