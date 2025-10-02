#!/bin/sh
set -eu

[ -f /etc/environment ] && . /etc/environment
# Prefer explicit overrides but fall back to compose-provisioned defaults.
API_KEY="${EXCHANGE_API_KEY:-${API_KEY:-}}"
BASE_URL="${EXCHANGE_API_BASE_URL:-${API_BASE_URL:-http://php-api/}}"

if [ -z "${API_KEY}" ]; then
    echo "[run_currency_job] API key missing (set API_KEY or EXCHANGE_API_KEY)" >&2
    exit 1
fi

CMD="/usr/local/bin/currency-rate"
if [ ! -x "${CMD}" ]; then
    echo "[run_currency_job] currency-rate CLI not installed" >&2
    exit 1
fi

case "${1:-}" in
  daily)
    TARGET_DATE=$(python - <<'PY'
from datetime import date, timedelta
print((date.today() - timedelta(days=1)).isoformat())
PY
)
    exec "$CMD" --base-url "$BASE_URL" --api-key "$API_KEY" MDL EUR "$TARGET_DATE"
    ;;
  weekly)
    RANGE=$(python - <<'PY'
from datetime import date, timedelta
# ISO week: previous full week Monday-Sunday relative to today
# Determine start/end of last week
# today.weekday(): Monday=0
 today = date.today()
 start_of_this_week = today - timedelta(days=today.weekday())
 start_of_last_week = start_of_this_week - timedelta(days=7)
 end_of_last_week = start_of_last_week + timedelta(days=6)
 print(start_of_last_week.isoformat(), end_of_last_week.isoformat())
PY
)
    set -- $RANGE
    exec "$CMD" --base-url "$BASE_URL" --api-key "$API_KEY" MDL USD --range "$1" "$2"
    ;;
  *)
    echo "Usage: $0 daily|weekly" >&2
    exit 1
    ;;
esac
