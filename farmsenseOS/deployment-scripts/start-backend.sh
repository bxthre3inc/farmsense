#!/bin/bash
# Backend startup script for Zo service

export DATABASE_URL="postgresql://farmsense_user:changeme@localhost:5432/farmsense"
export TIMESCALE_URL="postgresql://farmsense_user:changeme@localhost:5432/farmsense_timeseries"
export PORT=${PORT:-8000}

cd /home/workspace/farmsenseOS/farmsense-code/backend
exec uvicorn app.api.main:app --host 0.0.0.0 --port $PORT
