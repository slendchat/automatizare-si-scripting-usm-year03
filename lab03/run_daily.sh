#!/bin/sh
set -eu

APP_DIR=$(cd "$(dirname "$0")" && pwd)
PYTHON_BIN=${PYTHON_BIN:-python}

previous_day=$("${PYTHON_BIN}" - <<'PY'
import datetime as dt
print((dt.date.today() - dt.timedelta(days=1)).isoformat())
PY
)

exec "${PYTHON_BIN}" "${APP_DIR}/alternative_currency_exchange_rate.py" \
    MDL EUR "${previous_day}"
