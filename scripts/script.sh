#!/bin/sh

echo "Starting application..."

PORT_TO_USE=${PORT:-8000}

if [ "$RELOAD" = "1" ]; then
  echo "Development mode: watching for file changes..."
  exec uvicorn app.main:app --host 0.0.0.0 --port $PORT_TO_USE --reload
else
  exec uvicorn app.main:app --host 0.0.0.0 --port $PORT_TO_USE
fi