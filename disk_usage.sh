#!/bin/bash

#functions
Help() {
  echo "Usage: $0 -p <path> -s <size_in_MB> [-t <threshold_percent>] [-L <path_to_log_file>] [-v]"
  echo
  echo "Options:"
  echo "  -p    Path to directory"
  echo "  -s    Max size in MB"
  echo "  -t    Threshold in percent (default: 80)"
  echo "  -L    Path to log file (default /var/log/my_disk_usage.log)"
  echo "  -v    Verbose"
  echo "  -h    Show help"
  echo
  echo "Example:"
  echo "$0 -p target_dir/ -s 11 -t 50 -L log_dir/ -v"
}

Send_email_alert()
{
  echo "[FIRING] Directory $dir exceeded threshold ($usage% used)" \
  | mail -s "Disk usage alert" "example@example.com"
}

log_info() {
  echo "ts=$(date --utc +%FT%TZ) level=INFO $1" >> "$log_path" 
  if [ "$verbose" = true ]; then
    echo "$1" 
  fi
}
log_err() {
  echo "ts=$(date --utc +%FT%TZ) level=ERROR message=\"$1\"" >> "$log_path" 
  >&2 echo "[ERROR] $1" 
}

#Arguments
if [ $# -eq 0 ]; then
  echo "No arguments provided error."
  echo
  Help
  exit 1
fi

threshold=80
log_path=/var/log/my_disk_usage.log
verbose=false

while getopts "p:s:t:L:hv" option; do
  case $option in
    p) dir=$OPTARG ;;
    s) maxsize=$OPTARG ;;
    t) threshold=$OPTARG ;;
    L) log_path=$OPTARG ;;
    h) 
      Help
      exit;;
    v) verbose=true;;
    \?) 
      echo Invalid option, use -h to see HELP
      exit 1;;
  esac
done

#Logs
if [ ! -e "$log_path" ]; then
  log_dir=$(dirname "$log_path")
  if [ ! -d "$log_dir" ]; then
    mkdir -p "$log_dir"
  fi
fi

#Validation
if [ -z "$dir" ] || [ -z "$maxsize" ]; then
  log_err "Missing -p or -s"
  exit 1
fi

if [ ! -d "$dir" ]; then
  log_err "$dir does not exist."
  exit 1
fi

if [ "$threshold" -lt 1 ] || [ "$threshold" -gt 100 ]; then
  log_err "Threshold must be between 1-100."
  exit 1
fi

if ! [[ "$maxsize" =~ ^[0-9]+$ ]]; then
  log_err "-s must be an integer"
  exit 1
fi

if [ "$maxsize" -le 0 ]; then
  log_err "-s must be >= 1"
  exit 1
fi

#Logic
dir_size=$(du -sb "$dir" | awk '{print $1}')
dir_sizemb=$(echo "scale=2; $dir_size/1024/1024" | bc)
maxsizeb=$(( maxsize*1024*1024 ))

usage=$( echo "scale=2; $dir_size/$maxsizeb*100" | bc )
log_info "dir=$dir usage=${usage}% used=${dir_sizemb}MB limit=${maxsize}MB"

if (( $(echo "$usage >= $threshold" | bc -l) )); then
  log_info "$usage%(dir usage) >= $threshold%(threshold)"
  Send_email_alert
fi

trap 'log_err "Script interrupted"; exit 1' INT TERM
