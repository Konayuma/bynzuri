#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
PID_FILE="$ROOT_DIR/.run/start.pid"

if [[ ! -f "$PID_FILE" ]]; then
  echo "No startup script is running for this project."
  exit 0
fi
read -r pid start_time < "$PID_FILE" || true
if [[ ! "${pid:-}" =~ ^[0-9]+$ || ! "${start_time:-}" =~ ^[0-9]+$ ]] ||
   [[ ! -r "/proc/$pid/stat" ]] ||
   [[ "$(awk '{print $22}' "/proc/$pid/stat")" != "$start_time" ]]; then
  echo "No matching startup process found; the PID file is stale."
  exit 0
fi

kill -TERM "$pid"
echo "Stop requested. The startup script will shut down both servers."
