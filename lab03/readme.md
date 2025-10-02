# Lab 03 - Cron-Based Automation

This lab reuses the PHP API from lab02 and schedules the existing Python CLI (`currency-rate`) with cron inside a container. The cron jobs fetch MDL exchange rates on daily and weekly cadences and persist the JSON responses under `lab03/data`.

## Requirements
- Docker Engine and Docker Compose
- `.env` file with the shared API key (`API_KEY`) used by both containers

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

## Networking Notes
- Docker Compose creates an isolated network where each service is reachable by its service name.
- The cron runner talks to the API at `http://php-api/`. If you change the service name, update `.env` or `run_currency_job.sh` accordingly.
- You can verify connectivity after `docker compose up`:
  ```bash
  docker compose exec cron-runner ping -c 2 php-api
  docker compose exec cron-runner curl -s http://php-api/
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
- `cronjob` - cron schedule: daily MDL->EUR for yesterday and weekly MDL->USD for the previous week.
- `entrypoint.sh` - container entrypoint that installs the cron table, prepares logging, and starts cron.
- `run_currency_job.sh` - helper script invoked by cron; computes the target dates and calls `currency-rate` with the base URL (`http://php-api/`).
- `Dockerfile` - builds a Python + cron image, installs dependencies, and wires everything together.
- `docker-compose.yml` - Compose stack with the PHP API (`php-api`) and cron runner (`cron-runner`).
- `data/` - bind-mounted directory where API responses are stored.
- `error.log` - bind-mounted file with error tracebacks from the currency script.
- `currency_exchange_rate/` - Python package copied from lab02 (installed into the container for dependencies).
- `lab02prep/` - PHP API assets reused from lab02.
- `.env.example` - template for environment variables that must be provided.
