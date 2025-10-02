#!/bin/sh
set -eu

APP_DIR=$(cd "$(dirname "$0")" && pwd)
PYTHON_BIN=${PYTHON_BIN:-python}

range_output=$("${PYTHON_BIN}" - <<'PY'
import datetime as dt

today = dt.date.today()
start = today - dt.timedelta(days=today.weekday() + 7)
end = start + dt.timedelta(days=6)
print(start.isoformat(), end.isoformat())
PY
)

set -- ${range_output}
start_date=$1
end_date=$2

exec "${PYTHON_BIN}" "${APP_DIR}/alternative_currency_exchange_rate.py" \
    MDL USD "${start_date}" --end-date "${end_date}"
