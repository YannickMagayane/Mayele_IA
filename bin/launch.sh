#!/usr/bin/env bash
# ==============================================================================
# Script: bin/launch.sh
# Description: Launch script for Congo Intelligence Hub platform in Docker/local mode.
# ==============================================================================

set -e

echo "=== Launching Congo Intelligence Hub ==="

if [ "$1" == "--docker" ]; then
    echo "[+] Launching services via Docker Compose & Traefik..."
    docker-compose up -d --build
    echo "[+] Platform online at http://localhost"
else
    echo "[+] Initializing SQLite database schema (without migrations)..."
    ./venv/bin/python bin/init_db.py
    echo "[+] Starting local Django server on http://127.0.0.1:8000..."
    ./venv/bin/python manage.py runserver 0.0.0.0:8000
fi
