#!/usr/bin/env bash
# run_harness.sh - Execute the full test harness
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

export TARGET_URL="${1:-${TARGET_URL:-http://localhost:8080}}"
export HEALTH_PATH="${HEALTH_PATH:-/actuator/health}"
CUSTOM_TESTS="${CUSTOM_TESTS:-}"

# Locate Python 3 interpreter
if [ -n "${VIRTUAL_ENV:-}" ] && [ -x "${VIRTUAL_ENV}/bin/python" ]; then
    PYTHON="${VIRTUAL_ENV}/bin/python"
elif [ -x "${SCRIPT_DIR}/.venv/bin/python" ]; then
    PYTHON="${SCRIPT_DIR}/.venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
    PYTHON="$(command -v python)"
else
    echo "Error: Python 3 is not installed or not found in PATH." >&2
    exit 1
fi

# Ensure test dependencies (pytest, requests) are installed
if ! "${PYTHON}" -c "import pytest, requests" >/dev/null 2>&1; then
    echo "Required dependencies missing. Setting up virtual environment..."
    if [ ! -d "${SCRIPT_DIR}/.venv" ]; then
        "${PYTHON}" -m venv "${SCRIPT_DIR}/.venv"
    fi
    PYTHON="${SCRIPT_DIR}/.venv/bin/python"
    PIP="${SCRIPT_DIR}/.venv/bin/pip"
    "${PIP}" install -q -r "${SCRIPT_DIR}/requirements.txt"
fi

echo "=== Starting Test Harness against ${TARGET_URL} ==="
echo "Health Check Endpoint: ${HEALTH_PATH}"

echo "--- Step 1: Health Check ---"
"${PYTHON}" -m pytest tests/test_app_health.py

echo "--- Step 2: Security Scan ---"
"${PYTHON}" harness/security_scanner.py "${TARGET_URL}"

echo "--- Step 3: Fuzzing ---"
"${PYTHON}" harness/fuzzer.py "${TARGET_URL}"

# If internal test app is running, run default race condition test
if [ -z "${CUSTOM_TESTS}" ]; then
    echo "--- Step 4: Concurrency/Race Condition Tests ---"
    "${PYTHON}" tests/test_race_condition.py "${TARGET_URL}"
else
    echo "--- Step 4: Custom Target Repository Tests (${CUSTOM_TESTS}) ---"
    if [ -f "${CUSTOM_TESTS}" ]; then
        if [[ "${CUSTOM_TESTS}" == *.py ]]; then
            "${PYTHON}" "${CUSTOM_TESTS}" "${TARGET_URL}"
        else
            bash "${CUSTOM_TESTS}" "${TARGET_URL}"
        fi
    elif [ -d "${CUSTOM_TESTS}" ]; then
        "${PYTHON}" -m pytest "${CUSTOM_TESTS}"
    else
        echo "Notice: Custom test path '${CUSTOM_TESTS}' not found, skipping custom tests."
    fi
fi

echo "=== Test Harness Completed Successfully ==="
