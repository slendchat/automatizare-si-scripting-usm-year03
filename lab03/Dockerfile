FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends cron \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY currency_exchange_rate ./currency_exchange_rate
COPY alternative_currency_exchange_rate.py ./alternative_currency_exchange_rate.py
COPY cronjob ./cronjob
COPY entrypoint.sh ./entrypoint.sh
COPY run_daily.sh ./run_daily.sh
COPY run_weekly.sh ./run_weekly.sh

RUN pip install --no-cache-dir ./currency_exchange_rate
RUN chmod +x /app/entrypoint.sh /app/run_daily.sh /app/run_weekly.sh

ENTRYPOINT ["/app/entrypoint.sh"]
