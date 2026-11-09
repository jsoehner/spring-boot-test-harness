#!/usr/bin/env bash
# Build the target Spring Boot application
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="${SCRIPT_DIR}/target_app"

echo "=== Building Target Application ==="
echo "Target directory: ${TARGET_DIR}"

if [ ! -d "${TARGET_DIR}" ]; then
    echo "Error: target_app directory not found at ${TARGET_DIR}" >&2
    exit 1
fi

if ! command -v mvn >/dev/null 2>&1; then
    echo "Error: 'mvn' (Apache Maven) is not installed or not in PATH." >&2
    echo "  - macOS: brew install maven" >&2
    echo "  - Debian/Ubuntu: sudo apt-get install maven" >&2
    echo "  - Fedora/RHEL: sudo dnf install maven" >&2
    exit 1
fi

cd "${TARGET_DIR}"
mvn clean package -DskipTests

echo "Build complete. Artifact located in ${TARGET_DIR}/target/"
