#!/bin/bash
# Prepare the rootfs image for the Firecracker VM
# Usage: ./prepare_rootfs.sh

set -e

ROOTFS_PATH="/usr/local/bin/rootfs.img"
JAR_PATH="/mnt/c/Users/jsoehner/harness_project/target_app/target/target-app-0.0.1-SNAPSHOT.jar"
EXTRACT_PATH="/tmp/rootfs_extracted"
NEW_ROOTFS_PATH="/usr/local/bin/rootfs.img.new"

echo "Extracting rootfs image..."
rm -rf "$EXTRACT_PATH"
mkdir -p "$EXTRACT_PATH"
unsquashfs -d "$EXTRACT_PATH" "$ROOTFS_PATH"

echo "Injecting JAR..."
mkdir -p "$EXTRACT_PATH/app"
cp "$JAR_PATH" "$EXTRACT_PATH/app/target-app.jar"

echo "Re-packing rootfs image..."
rm -f "$ROOTFS_PATH"
mksquashfs "$EXTRACT_PATH" "$NEW_ROOTFS_PATH" -comp gzip

echo "Finalizing rootfs image..."
mv "$NEW_ROOTFS_PATH" "$ROOTFS_PATH"

echo "Rootfs preparation complete."
