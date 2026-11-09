#!/usr/bin/env bash
# sync_harness_tests.sh
# Syncs the centralized AI-Generated Abuse Case & Concurrency test suite from
# spring-boot-test-harness into any new or existing Spring Boot repository.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

if [ $# -lt 1 ]; then
    cat <<EOF
Usage: ./scripts/sync_harness_tests.sh <TARGET_REPO_PATH>

Syncs the Spring Boot Test Harness AI Abuse Case & Concurrency test suite
(test_ai_abuse_cases.py, test_inventory_concurrency.py, conftest.py, pytest.ini)
into <TARGET_REPO_PATH>/tests/harness_tests/.
EOF
    exit 1
fi

TARGET_REPO="$(cd "$1" && pwd)"
DEST_DIR="${TARGET_REPO}/tests/harness_tests"

echo "================================================================="
echo "  Syncing Spring Boot Test Harness Suite -> ${TARGET_REPO}"
echo "================================================================="

mkdir -p "${DEST_DIR}"

cp -f "${HARNESS_ROOT}/tests/pytest.ini" "${DEST_DIR}/pytest.ini"
cp -f "${HARNESS_ROOT}/tests/conftest.py" "${DEST_DIR}/conftest.py"
cp -f "${HARNESS_ROOT}/tests/test_ai_abuse_cases.py" "${DEST_DIR}/test_ai_abuse_cases.py"
cp -f "${HARNESS_ROOT}/tests/test_inventory_concurrency.py" "${DEST_DIR}/test_inventory_concurrency.py"
chmod +x "${DEST_DIR}/test_ai_abuse_cases.py" "${DEST_DIR}/test_inventory_concurrency.py"

echo "[+] Synced test files into ${DEST_DIR}:"
echo "    - pytest.ini"
echo "    - conftest.py"
echo "    - test_ai_abuse_cases.py"
echo "    - test_inventory_concurrency.py"
echo "================================================================="
