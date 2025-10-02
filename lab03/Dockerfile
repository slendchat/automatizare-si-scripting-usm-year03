FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends cron \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY currency_exchange_rate ./currency_exchange_rate
COPY currency_exchange_rate.py ./
COPY cronjob ./
COPY entrypoint.sh ./

RUN pip install --no-cache-dir ./currency_exchange_rate
RUN chmod +x /app/entrypoint.sh
RUN crontab /app/cronjob

ENTRYPOINT ["/app/entrypoint.sh"]
