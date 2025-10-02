#!/bin/sh
set -eu

APP_DIR=/app
CRON_LOG=/var/log/cron.log

create_log_file() {
    echo "Creating cron log at ${CRON_LOG}"
    touch "${CRON_LOG}"
    chmod 666 "${CRON_LOG}"
}

install_cron_jobs() {
    echo "Installing cron schedule from ${APP_DIR}/cronjob"
    crontab "${APP_DIR}/cronjob"
}

monitor_logs() {
    echo "=== Monitoring cron logs ==="
    tail -F "${CRON_LOG}" &
}

run_cron() {
    echo "=== Starting cron daemon ==="
    exec cron -f
}

mkdir -p "${APP_DIR}/data"
env > /etc/environment
create_log_file
install_cron_jobs
monitor_logs
run_cron
