#!/bin/sh
set -eu

# Export environment variables saved by entrypoint
[ -f /etc/environment ] && . /etc/environment

API_KEY="${EXCHANGE_API_KEY:-${API_KEY:-}}"
BASE_URL="${EXCHANGE_API_BASE_URL:-${API_BASE_URL:-http://php-api/}}"
PYTHON_BIN="${PYTHON_BIN:-/usr/local/bin/python}"
SCRIPT="/app/currency_exchange_rate.py"

if [ -z "$API_KEY" ]; then
    echo "[run_currency_job] API key missing (set API_KEY or EXCHANGE_API_KEY)" >&2
    exit 1
fi

if [ ! -x "$PYTHON_BIN" ]; then
    echo "[run_currency_job] Python interpreter not found at $PYTHON_BIN" >&2
    exit 1
fi

if [ ! -f "$SCRIPT" ]; then
    echo "[run_currency_job] Script $SCRIPT not found" >&2
    exit 1
fi

case "${1:-}" in
  daily)
    TARGET_DATE=$($PYTHON_BIN - <<'PY'
from datetime import date, timedelta
print((date.today() - timedelta(days=1)).isoformat())
PY
)
    exec "$PYTHON_BIN" "$SCRIPT" MDL EUR "$TARGET_DATE" --api-url "$BASE_URL" --api-key "$API_KEY"
    ;;
  weekly)
    RANGE=$($PYTHON_BIN - <<'PY'
from datetime import date, timedelta

today = date.today()
start = today - timedelta(days=today.weekday() + 7)
end = start + timedelta(days=6)
print(f"{start.isoformat()} {end.isoformat()}")
PY
)
    set -- $RANGE
    exec "$PYTHON_BIN" "$SCRIPT" MDL USD --range "$1" "$2" --api-url "$BASE_URL" --api-key "$API_KEY"
    ;;
  *)
    echo "Usage: $0 daily|weekly" >&2
    exit 1
    ;;
esac
