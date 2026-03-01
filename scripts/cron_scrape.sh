#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/home/master/.openclaw/workspace/X_Stock_Tracker"
VENV="$APP_DIR/.venv/bin/activate"
LOG_DIR="$APP_DIR/logs"
mkdir -p "$LOG_DIR"

# Preferred port for local app
PORT=8083

# Start server if not already running on PORT
if ! curl -fsS "http://127.0.0.1:${PORT}/api/scrape/status" >/dev/null 2>&1; then
  cd "$APP_DIR"
  source "$VENV"
  nohup uvicorn app.main:app --port "$PORT" > "$LOG_DIR/uvicorn.log" 2>&1 &
  sleep 4
fi

# Trigger scrape (12h cadence caller)
curl -fsS -X POST \
  -F 'max_tweets=120' \
  -F 'max_age_days=7' \
  "http://127.0.0.1:${PORT}/api/scrape/trigger" \
  >> "$LOG_DIR/cron-scrape.log" 2>&1
printf "\n[%s] scrape triggered\n" "$(date -Is)" >> "$LOG_DIR/cron-scrape.log"
