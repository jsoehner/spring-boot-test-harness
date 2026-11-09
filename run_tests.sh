#!/usr/bin/env bash
# run_tests.sh - Execute host-side tests against the running sandbox/application
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

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

TEST_TARGET="${1:-tests/test_app_health.py}"
echo "Running host-side tests with ${PYTHON}: ${TEST_TARGET}..."
"${PYTHON}" -m pytest "${TEST_TARGET}"

echo "Tests completed successfully!"
