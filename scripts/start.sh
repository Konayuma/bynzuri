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
  if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 is required to create the virtual environment." >&2
    exit 1
  fi
  echo "Creating Python virtual environment..."
  python3 -m venv "$ROOT_DIR/.venv"
fi
if ! command -v npm >/dev/null 2>&1; then
  echo "Node.js and npm are required to install frontend dependencies." >&2
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
install_pid=""
cleanup() {
  trap - EXIT INT TERM
  [[ -z "$install_pid" ]] || kill "$install_pid" 2>/dev/null || true
  [[ -z "$backend_pid" ]] || kill "$backend_pid" 2>/dev/null || true
  [[ -z "$frontend_pid" ]] || kill "$frontend_pid" 2>/dev/null || true
  wait 2>/dev/null || true
  rm -f "$RUNTIME_DIR/start.pid"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM

if ! "$PYTHON" -m pip --version >/dev/null 2>&1; then
  echo "Installing pip in the virtual environment..."
  "$PYTHON" -m ensurepip --upgrade 9>&-
fi
# Only contact package registries when the installed packages need updating.
if "$PYTHON" - "$BACKEND_DIR/requirements.txt" <<'PY'
import importlib.metadata as metadata
import sys

for line in open(sys.argv[1], encoding="utf-8"):
    line = line.strip()
    if not line or line.startswith("#"):
        continue
    try:
        name, version = line.split("==", 1)
        if metadata.version(name) != version:
            raise ValueError(line)
    except (ValueError, metadata.PackageNotFoundError):
        sys.exit(1)
PY
then
  echo "Backend dependencies are already installed."
else
  echo "Installing backend dependencies..."
  "$PYTHON" -m pip install --timeout 15 --retries 2 -r "$BACKEND_DIR/requirements.txt" 9>&- &
  install_pid=$!
  wait "$install_pid"
  install_pid=""
fi
if npm ls --prefix "$FRONTEND_DIR" --depth=0 9>&- >/dev/null 2>&1; then
  echo "Frontend dependencies are already installed."
else
  echo "Installing frontend dependencies..."
  npm install --prefix "$FRONTEND_DIR" --no-save --package-lock=false --no-audit --no-fund --loglevel=info --fetch-retries=2 --fetch-retry-mintimeout=1000 --fetch-retry-maxtimeout=5000 --fetch-timeout=30000 9>&- &
  install_pid=$!
  wait "$install_pid"
  install_pid=""
fi

cd "$BACKEND_DIR"
echo "Applying database migrations..."
"$PYTHON" manage.py migrate --noinput 9>&-

echo "Starting API at http://127.0.0.1:8001"
"$PYTHON" manage.py runserver 127.0.0.1:8001 --noreload 9>&- &
backend_pid=$!
cd "$FRONTEND_DIR"
echo "Starting frontend (Vite will print its URL). Press Ctrl+C to stop both servers."
./node_modules/.bin/vite 9>&- &
frontend_pid=$!

set +e
wait -n "$backend_pid" "$frontend_pid"
status=$?
set -e
echo "A server stopped; shutting down the other."
exit "$status"
