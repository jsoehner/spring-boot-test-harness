#!/bin/bash
# run_harness.sh - Execute the full test harness

set -e

TARGET_URL="http://localhost:8080"

echo "=== Starting Test Harness ==="

echo "--- Step 1: Health Check ---"
python -m pytest tests/test_app_health.py

echo "--- Step 2: Security Scan ---"
python harness/security_scanner.py $TARGET_URL

echo "--- Step 3: Fuzzing ---"
python harness/fuzzer.py $TARGET_URL

echo "--- Step 4: Concurrency/Race Condition Tests ---"
python tests/test_race_condition.py

echo "=== Test Harness Completed ==="
