# Currency Exchange Rate Automation (lab02)

This lab adds a small CLI utility that talks to the support service shipped in `lab02/lab02prep`. The script requests a currency exchange rate for a specific day, stores the JSON response, and logs failures.

## Prerequisites

- Python 3.12 or newer
- `pip` for installing Python packages
- Docker + Docker Compose (only needed if you want to run the bundled service locally)

Install the Python dependency:

```bash
pip install --upgrade requests
```

## Start the support service (optional)

Use the project in `lab02/lab02prep` if you want to exercise the API locally.

```bash
cd lab02/lab02prep
cp sample.env .env        # edit the key if you like
export EXCHANGE_API_KEY=<value from .env>
docker-compose up --build
```

The service listens on `http://localhost:8080/` once the containers are up.

## Run the script

From the repository root:

```bash
python3 lab02/currency_exchange_rate.py USD EUR 2025-01-01 --api-key "$API_KEY"
```

Optional flags:

- `--base-url http://localhost:8080/` – override the service endpoint.
- `--timeout 5` – change the HTTP timeout (seconds).
- If `--api-key` is omitted the script falls back to the `EXCHANGE_API_KEY` environment variable.

Example batch run covering the valid data range (five evenly spaced dates):

```bash
for day in 2025-01-01 2025-03-01 2025-05-01 2025-07-01 2025-09-01; do
  python3 lab02/currency_exchange_rate.py USD EUR "$day" --api-key "${API_KEY}"
done
```

Successful calls save JSON files to `data/<FROM>_<TO>_<DATE>.json`. If the service reports an error or the request fails, the script prints the reason to the console and appends it to `error.log` in the project root.

## Script structure

- `parse_args` – handles CLI parameters, including optional overrides.
- `validate_inputs` – normalises currencies, checks the date format, resolves the base URL and API key.
- `fetch_exchange_rate` – executes the HTTP POST request (`params` in the query string, API key in the body) and validates the response payload.
- `save_response` – ensures the `data/` directory exists and stores the JSON response.
- `log_error` – records issues to `error.log` using UTC timestamps.
- `main` – orchestrates argument parsing, validation, network call, persistence, and user feedback.
