#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
PYTHON="$BACKEND_DIR/.venv/bin/python"

if [[ ! -x "$PYTHON" ]]; then
  PYTHON="$ROOT_DIR/.venv/bin/python"
fi
if [[ ! -x "$PYTHON" ]]; then
  echo "Python virtual environment not found. Create backend/.venv and install backend/requirements.txt." >&2
  exit 1
fi
if ! "$PYTHON" -c 'import django, requests' >/dev/null 2>&1; then
  echo "Backend dependencies are missing. Run: $PYTHON -m pip install -r $BACKEND_DIR/requirements.txt" >&2
  exit 1
fi
if ! command -v npm >/dev/null 2>&1 || [[ ! -d "$FRONTEND_DIR/node_modules" ]]; then
  echo "npm or frontend dependencies missing. Install Node.js and run: cd frontend && npm install" >&2
  exit 1
fi
if [[ ! -f "$BACKEND_DIR/.env" ]]; then
  echo "Missing backend/.env. Copy backend/.env.example and configure it first." >&2
  exit 1
fi
if [[ ! -f "$FRONTEND_DIR/.env" ]]; then
  echo "Missing frontend/.env. Copy frontend/.env.example and configure it first." >&2
  exit 1
fi

RUNTIME_DIR="$ROOT_DIR/.run"
mkdir -p "$RUNTIME_DIR"
exec 9>"$RUNTIME_DIR/start.lock"
if ! flock -n 9; then
  echo "The startup script is already running. Use ./scripts/stop.sh to stop it." >&2
  exit 1
fi
printf '%s %s\n' "$$" "$(awk '{print $22}' "/proc/$$/stat")" > "$RUNTIME_DIR/start.pid"
backend_pid=""
frontend_pid=""
cleanup() {
  trap - EXIT INT TERM
  [[ -z "$backend_pid" ]] || kill "$backend_pid" 2>/dev/null || true
  [[ -z "$frontend_pid" ]] || kill "$frontend_pid" 2>/dev/null || true
  wait 2>/dev/null || true
  rm -f "$RUNTIME_DIR/start.pid"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

cd "$BACKEND_DIR"
echo "Applying database migrations..."
"$PYTHON" manage.py migrate --noinput

echo "Starting API at http://127.0.0.1:8001"
"$PYTHON" manage.py runserver 127.0.0.1:8001 --noreload &
backend_pid=$!
cd "$FRONTEND_DIR"
echo "Starting frontend (Vite will print its URL). Press Ctrl+C to stop both servers."
./node_modules/.bin/vite &
frontend_pid=$!

set +e
wait -n "$backend_pid" "$frontend_pid"
status=$?
set -e
echo "A server stopped; shutting down the other."
exit "$status"
