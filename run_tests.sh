#!/bin/bash
# run_tests.sh - Execute host-side tests against the running sandbox app

set -e

echo "Installing test dependencies..."
pip install -r requirements.txt

echo "Running host-side tests..."
pytest tests/test_app_health.py

echo "Tests completed successfully!"
