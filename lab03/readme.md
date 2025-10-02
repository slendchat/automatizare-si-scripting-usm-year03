# Lab 03 – Cron Automation

This setup packages the currency rate fetcher together with the PHP reference API in Docker containers. Cron runs inside the Python container and triggers helper scripts that query the PHP service.

## Requirements
- Docker and Docker Compose

## Configuration
1. Copy or edit `.env` in `lab03/` if you need a different API key or service URL.
2. The default values assume the PHP container is reachable as `php-api` on the internal Docker network.

## Build and Run
1. From `lab03/`, start the stack: `docker compose up --build -d`
2. Check service health: `docker compose ps`

## Verifying Cron Jobs
- Inspect recent cron output: `docker compose exec cron-runner tail -n 20 /var/log/cron.log`
- View downloaded exchange rates: `docker compose exec cron-runner ls /app/data`
- Check the shared API logs through Docker: `docker compose logs php-api`

## Project Layout
- `Dockerfile` – builds the Python cron runner image
- `docker-compose.yml` – wires PHP API and cron runner containers
- `alternative_currency_exchange_rate.py` – enhanced script with date range support
- `run_daily.sh` / `run_weekly.sh` – cron targets for daily and weekly data collection
- `entrypoint.sh` – configures cron and tails logs inside the container
- `cronjob` – schedule definition written into the container crontab
- `currency_exchange_rate/` – Python package copied from lab02 (API client utilities)
- `lab02prep/` – PHP API source copied from lab02
- `data/` – mounted output directory for JSON responses
- `error.log` – shared log file for Python script errors
