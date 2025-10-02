#!/bin/sh
set -eu

create_log_file() {
    echo "Creating log file..."
    touch /var/log/cron.log
    chmod 666 /var/log/cron.log
    echo "Log file ready at /var/log/cron.log"
}

install_cron_schedule() {
    echo "Installing cron schedule..."
    crontab /app/cronjob
}

monitor_logs() {
    echo "=== Monitoring cron logs ==="
    tail -F /var/log/cron.log &
}

run_cron() {
    echo "=== Starting cron daemon ==="
    exec cron -f
}

env > /etc/environment
install_cron_schedule
create_log_file
monitor_logs
run_cron

