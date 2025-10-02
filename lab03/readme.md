# Lab 03 - Cron-Based Automation

This lab reuses the PHP API from lab02 and schedules the currency collector with cron inside a Python container. The cron jobs fetch MDL exchange rates on daily and weekly cadences and persist the JSON responses under `lab03/data`.

## Requirements
- Docker Engine and Docker Compose
- API key shared between the PHP service (`API_KEY`) and the Python cron runner

## Build and Run
1. Prepare environment variables:
   ```bash
   cd lab03
   cp .env.example .env   # set API_KEY before continuing
   ```
2. Build the images and start both services:
   ```bash
   docker compose build
   docker compose up -d
   ```
3. When finished, stop the stack:
   ```bash
   docker compose down
   ```

## Verifying Cron Jobs
- Follow container logs:
  ```bash
  docker compose logs -f cron-runner
  ```
- Tail the cron output inside the runner:
  ```bash
  docker compose exec cron-runner tail -n 50 /var/log/cron.log
  ```
- Inspect the generated snapshots (bind-mounted to the host):
  ```bash
  ls data
  ```
  Daily runs create `MDL_EUR_<date>.json`; weekly runs create `MDL_USD_<start>_to_<end>.json`.

## Project Layout
- `currency_exchange_rate.py` - CLI script invoked by cron to fetch one day or a date range.
- `cronjob` - cron schedule: daily MDL->EUR for yesterday and weekly MDL->USD for the previous week.
- `entrypoint.sh` - container entrypoint that installs the cron table, prepares logging, and starts cron.
- `Dockerfile` - builds a Python + cron image, installs dependencies, and wires everything together.
- `docker-compose.yml` - Compose stack with the PHP API (`php-api`) and cron runner (`cron-runner`).
- `data/` - bind-mounted directory where API responses are stored.
- `error.log` - bind-mounted file with error tracebacks from the currency script.
- `currency_exchange_rate/` - Python package copied from lab02 (installed into the container for dependencies).
- `lab02prep/` - PHP API assets reused from lab02.
