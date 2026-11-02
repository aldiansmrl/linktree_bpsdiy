#!/usr/bin/env bash
# Startup script for Linktree App
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

PORT=${PORT:-8000}

echo "Memulai server Linktree pada port $PORT..."
python3 app.py --port "$PORT"
