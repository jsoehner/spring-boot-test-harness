#!/bin/bash

# Setup script for Local Security Harness Sandbox
# Run this inside the WSL Fedora instance

echo "Updating system..."
sudo dnf update -y

echo "Installing Firecracker..."
# Install Firecracker (assuming standard repo or manual binary download)
# Note: Firecracker requires nested virtualization to be enabled in WSL2.
sudo dnf install -y firecracker

echo "Installing Kata Containers..."
sudo dnf install -y kata-runtime

echo "Installing build dependencies..."
sudo dnf install -y maven git java-17-openjdk-devel

echo "Sandbox environment preparation complete."
