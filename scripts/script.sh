#!/bin/sh

# Run the app (--reload when RELOAD=1 for development)
echo "Starting application..."
if [ "$RELOAD" = "1" ]; then
  echo "Development mode: watching for file changes..."
  exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
else
  exec uvicorn app.main:app --host 0.0.0.0 --port 8000
fi
