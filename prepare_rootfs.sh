#!/usr/bin/env bash
# Prepare the rootfs image for the Firecracker VM
# Usage: ./prepare_rootfs.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOTFS_PATH="${ROOTFS_PATH:-/usr/local/bin/rootfs.img}"
JAR_PATH="${JAR_PATH:-${SCRIPT_DIR}/target_app/target/target-app-0.0.1-SNAPSHOT.jar}"
EXTRACT_PATH="${EXTRACT_PATH:-/tmp/rootfs_extracted}"
NEW_ROOTFS_PATH="${NEW_ROOTFS_PATH:-/tmp/rootfs.img.new}"

echo "=== Firecracker RootFS Preparation ==="
echo "Target JAR: ${JAR_PATH}"
echo "Target RootFS: ${ROOTFS_PATH}"

# Check for JAR existence
if [ ! -f "${JAR_PATH}" ]; then
    echo "JAR not found at ${JAR_PATH}. Attempting to build..."
    "${SCRIPT_DIR}/build_app.sh"
fi

if [ ! -f "${JAR_PATH}" ]; then
    echo "Error: Target JAR file does not exist at ${JAR_PATH}." >&2
    exit 1
fi

# Check for squashfs tools
if ! command -v unsquashfs >/dev/null 2>&1 || ! command -v mksquashfs >/dev/null 2>&1; then
    echo "Error: 'unsquashfs' and/or 'mksquashfs' are required to manipulate squashfs images." >&2
    echo "Note: If you are running on macOS, Firecracker is not natively supported (requires Linux KVM)." >&2
    echo "Use './orchestrate_vm.sh --mode direct' to run the test harness natively on macOS." >&2
    exit 1
fi

if [ ! -f "${ROOTFS_PATH}" ]; then
    echo "Error: Base rootfs image not found at ${ROOTFS_PATH}." >&2
    echo "Please ensure the base rootfs image exists or configure ROOTFS_PATH." >&2
    exit 1
fi

echo "Extracting rootfs image..."
rm -rf "${EXTRACT_PATH}"
mkdir -p "${EXTRACT_PATH}"
unsquashfs -d "${EXTRACT_PATH}" "${ROOTFS_PATH}"

echo "Injecting JAR..."
mkdir -p "${EXTRACT_PATH}/app"
cp "${JAR_PATH}" "${EXTRACT_PATH}/app/target-app.jar"

echo "Re-packing rootfs image..."
rm -f "${NEW_ROOTFS_PATH}"
mksquashfs "${EXTRACT_PATH}" "${NEW_ROOTFS_PATH}" -comp gzip

echo "Finalizing rootfs image..."
if [ -w "$(dirname "${ROOTFS_PATH}")" ]; then
    mv "${NEW_ROOTFS_PATH}" "${ROOTFS_PATH}"
else
    echo "Warning: No write permission to $(dirname "${ROOTFS_PATH}"). Image saved at ${NEW_ROOTFS_PATH}."
    echo "Run: sudo mv ${NEW_ROOTFS_PATH} ${ROOTFS_PATH}"
fi

echo "Rootfs preparation complete."
