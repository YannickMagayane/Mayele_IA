#!/usr/bin/env bash
# ==============================================================================
# Script: bin/test.sh
# Description: Isolated unit test runner for Congo Intelligence Hub.
# ==============================================================================

set -e

echo "=== Running Isolated Unit Tests ==="

if [ -f "./venv/bin/python" ]; then
    ./venv/bin/python manage.py test authentication analyzer data_pipeline
else
    python manage.py test authentication analyzer data_pipeline
fi
