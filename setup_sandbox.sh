#!/usr/bin/env bash
# setup_sandbox.sh - Environment preparation for Spring Boot Test Harness
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

OS_NAME="$(uname -s)"

echo "=== Spring Boot Test Harness Environment Setup ==="
echo "Detected Operating System: ${OS_NAME}"

case "${OS_NAME}" in
    Darwin)
        echo "Configuring environment for macOS..."
        if command -v brew >/dev/null 2>&1; then
            echo "Homebrew detected. Checking build dependencies..."
            command -v mvn >/dev/null 2>&1 || brew install maven
            command -v python3 >/dev/null 2>&1 || brew install python
            command -v java >/dev/null 2>&1 || brew install openjdk@17
        else
            echo "Notice: Homebrew not found. Please ensure Java 17+, Maven, and Python 3 are installed."
        fi

        echo ""
        echo "----------------------------------------------------------------------"
        echo "NOTE: Firecracker microVMs require Linux KVM (/dev/kvm) and cannot run"
        echo "natively on macOS. On macOS, this harness supports:"
        echo "  1) Direct Execution Mode: ./orchestrate_vm.sh --mode direct (Default)"
        echo "  2) Mock Server Mode:      ./orchestrate_vm.sh --mode mock"
        echo "  3) Docker Container Mode: ./orchestrate_vm.sh --mode docker (if Docker is installed)"
        echo "----------------------------------------------------------------------"
        ;;

    Linux)
        echo "Configuring environment for Linux..."
        if command -v dnf >/dev/null 2>&1; then
            echo "Fedora / RHEL environment detected."
            sudo dnf update -y
            sudo dnf install -y maven git java-17-openjdk-devel python3 python3-pip

            if [ -e /dev/kvm ]; then
                echo "KVM detected. Installing Firecracker and Kata Containers..."
                sudo dnf install -y firecracker kata-runtime || echo "Notice: Firecracker package not in default repos, manual install may be required."
            else
                echo "Notice: /dev/kvm not found. Firecracker requires hardware virtualization or WSL2 nested virtualization."
            fi
        elif command -v apt-get >/dev/null 2>&1; then
            echo "Debian / Ubuntu environment detected."
            sudo apt-get update -y
            sudo apt-get install -y maven git openjdk-17-jdk python3 python3-pip python3-venv

            if [ -e /dev/kvm ]; then
                echo "KVM detected (/dev/kvm)."
            fi
        else
            echo "Generic Linux detected. Please ensure Java 17+, Maven, Python 3, and Firecracker (if KVM is available) are installed."
        fi
        ;;

    MINGW*|MSYS*|CYGWIN*)
        echo "Windows POSIX environment detected."
        echo "For Windows, running under WSL2 with Fedora/Ubuntu is recommended for Firecracker,"
        echo "or run directly via PowerShell / Direct Execution Mode."
        ;;

    *)
        echo "Unknown operating system: ${OS_NAME}."
        ;;
esac

# Common: Set up Python virtual environment
echo ""
echo "Setting up Python virtual environment..."
if command -v python3 >/dev/null 2>&1; then
    if [ ! -d ".venv" ]; then
        python3 -m venv .venv
    fi
    .venv/bin/pip install -r requirements.txt
    echo "Python dependencies installed in .venv."
elif command -v python >/dev/null 2>&1; then
    if [ ! -d ".venv" ]; then
        python -m venv .venv
    fi
    .venv/bin/pip install -r requirements.txt
    echo "Python dependencies installed in .venv."
fi

echo ""
echo "=== Environment preparation complete! ==="
