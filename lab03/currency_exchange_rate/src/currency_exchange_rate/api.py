import datetime as dt
import requests
import logging
import json

log = logging.getLogger("app.api")


def fetch_exchange_rate_to_json(url:str,key:str,base:str,quote:str,date: dt) -> dict[str,any]:

    query = {
        "from":base,
        "to":quote,
        "date":date
    }
    payload = {"key":key}

    try:
        response = requests.post(url, params=query, data=payload, timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:
        log.error(f"API request failed {exc}")
        raise RuntimeError(f"API request failed {exc}") from exc
    
    try:
        data = response.json()
    except json.decoder.JSONDecodeError as exc:
        log.error(f"API request failed Json decode error")
        raise RuntimeError("Json decode error") from exc
    
    error_message = data.get("error")
    if error_message:
        log.error(f"Service returned an error: {error_message}")
        raise RuntimeError(f"Service returned an error: {error_message}")

    if "data" not in data:
        log.error("Service response missing 'data' field.")
        raise RuntimeError("Service response missing 'data' field.")

    return data