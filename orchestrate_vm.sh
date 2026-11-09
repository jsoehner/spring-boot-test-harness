#!/usr/bin/env bash
# orchestrate_vm.sh - Manage Application & Sandbox Lifecycle and Test Execution
# Supports multiple platforms (macOS, Linux, WSL), isolation modes, and external target applications.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

# Defaults
MODE="auto"
APP_PORT=8080
VM_NAME="harness-target-app"
FIRECRACKER_BIN="${FIRECRACKER_BIN:-/usr/bin/firecracker}"
SOCK_PATH="${SOCK_PATH:-/tmp/firecracker.sock}"
CONFIG_PATH="${SCRIPT_DIR}/config.json"
ROOTFS_PATH="${ROOTFS_PATH:-/usr/local/bin/rootfs.img}"
KERNEL_PATH="${KERNEL_PATH:-/usr/local/bin/kernel.img}"
APP_JAR="${APP_JAR:-${SCRIPT_DIR}/target_app/target/target-app-0.0.1-SNAPSHOT.jar}"
HEALTH_PATH="${HEALTH_PATH:-/actuator/health}"
CUSTOM_TESTS="${CUSTOM_TESTS:-}"
SKIP_BUILD=false
KEEP_RUNNING=false

log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

usage() {
    cat <<EOF
Usage: ./orchestrate_vm.sh [OPTIONS]

Options:
  --mode [auto|direct|firecracker|mock]
                      Execution mode:
                        - direct: Run Spring Boot application directly on host (macOS / Linux / Windows)
                        - firecracker: Run in Firecracker microVM (requires Linux with /dev/kvm)
                        - mock: Run Python lightweight mock server
                        - auto: Auto-detect based on host capabilities (default)
  --jar PATH          Path to target application JAR (defaults to internal target_app)
  --health-path PATH  HTTP path for application readiness check (default: /actuator/health)
  --custom-tests PATH Path to external pytest directory or test script from target repo
  --port PORT         Application port (default: 8080)
  --skip-build        Skip building the target JAR if already compiled
  --keep              Keep application running after tests finish
  -h, --help          Show this help message
EOF
    exit 0
}

# Parse CLI arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --mode)
            MODE="$2"
            shift 2
            ;;
        --jar)
            APP_JAR="$2"
            shift 2
            ;;
        --health-path)
            HEALTH_PATH="$2"
            shift 2
            ;;
        --custom-tests)
            CUSTOM_TESTS="$2"
            shift 2
            ;;
        --port)
            APP_PORT="$2"
            shift 2
            ;;
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        --keep)
            KEEP_RUNNING=true
            shift
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo "Unknown option: $1" >&2
            usage
            ;;
    esac
done

if ! [[ "${HEALTH_PATH}" =~ ^/ ]]; then
    HEALTH_PATH="/${HEALTH_PATH}"
fi

OS_NAME="$(uname -s)"

# Determine execution mode if auto
if [ "${MODE}" = "auto" ]; then
    if [ "${OS_NAME}" = "Darwin" ]; then
        log "macOS detected: Firecracker microVMs require Linux KVM. Selecting Direct Execution Mode."
        MODE="direct"
    elif [ "${OS_NAME}" = "Linux" ]; then
        if [ -e /dev/kvm ] && command -v "${FIRECRACKER_BIN}" >/dev/null 2>&1 && [ -f "${ROOTFS_PATH}" ]; then
            log "Linux with KVM and Firecracker detected. Selecting Firecracker microVM mode."
            MODE="firecracker"
        else
            log "Linux detected without active Firecracker/KVM rootfs. Falling back to Direct Execution Mode."
            MODE="direct"
        fi
    else
        log "Non-Linux OS detected (${OS_NAME}). Selecting Direct Execution Mode."
        MODE="direct"
    fi
fi

log "Active execution mode: ${MODE}"
log "Target application port: ${APP_PORT}"
log "Target health path: ${HEALTH_PATH}"
log "Target application JAR: ${APP_JAR}"

# Process cleanup handler
APP_PID=""
cleanup() {
    if [ "${KEEP_RUNNING}" = true ]; then
        log "Keep-running flag set. Process left running with PID: ${APP_PID}"
        return
    fi

    if [ -n "${APP_PID}" ]; then
        log "Cleaning up process (PID: ${APP_PID})..."
        kill -15 "${APP_PID}" 2>/dev/null || true
        wait "${APP_PID}" 2>/dev/null || true
        log "Process stopped."
    fi
    rm -f .app_pid .vm_pid "${SOCK_PATH}" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# Step 1: Health Check Function
wait_for_health() {
    local target_url="http://localhost:${APP_PORT}${HEALTH_PATH}"
    local max_retries=60
    local count=0

    log "Waiting for application to respond at ${target_url}..."
    while ! curl -s -f "${target_url}" >/dev/null 2>&1; do
        if [ ${count} -ge ${max_retries} ]; then
            log "Error: Application failed to respond at ${target_url} within ${max_retries}s."
            if [ -f ".app.log" ]; then
                log "--- Last 20 lines of application log ---"
                tail -n 20 .app.log
                log "----------------------------------------"
            fi
            return 1
        fi
        sleep 1
        count=$((count + 1))
    done
    log "SUCCESS: Application is UP and responding!"
    return 0
}

# Step 2: Run Harness Tests
run_tests() {
    log "Executing test harness suite..."
    HEALTH_PATH="${HEALTH_PATH}" \
    CUSTOM_TESTS="${CUSTOM_TESTS}" \
    "${SCRIPT_DIR}/run_harness.sh" "http://localhost:${APP_PORT}"
    log "SUCCESS: All harness steps completed successfully!"
}

# Step 3: Execution Modes
case "${MODE}" in
    direct)
        log "Starting application in Direct Host Mode..."
        if ! command -v java >/dev/null 2>&1; then
            echo "Error: Java Runtime Environment is required for direct mode." >&2
            exit 1
        fi

        if [ ! -f "${APP_JAR}" ]; then
            if [ "${SKIP_BUILD}" = true ]; then
                echo "Error: Target JAR not found at ${APP_JAR} and --skip-build was specified." >&2
                exit 1
            fi
            log "Application JAR not found at ${APP_JAR}. Triggering build..."
            "${SCRIPT_DIR}/build_app.sh"
        fi

        java -jar "${APP_JAR}" --server.port="${APP_PORT}" > .app.log 2>&1 &
        APP_PID=$!
        echo "${APP_PID}" > .app_pid
        log "Application started with PID: ${APP_PID} (logging to .app.log)"

        wait_for_health
        run_tests
        ;;

    mock)
        log "Starting lightweight Python mock server..."
        if command -v python3 >/dev/null 2>&1; then
            PYTHON_CMD="python3"
        elif [ -x "${SCRIPT_DIR}/.venv/bin/python" ]; then
            PYTHON_CMD="${SCRIPT_DIR}/.venv/bin/python"
        else
            PYTHON_CMD="python"
        fi

        ${PYTHON_CMD} "${SCRIPT_DIR}/mock_server.py" "${APP_PORT}" > .app.log 2>&1 &
        APP_PID=$!
        echo "${APP_PID}" > .app_pid
        log "Mock server started with PID: ${APP_PID}"

        wait_for_health
        run_tests
        ;;

    firecracker)
        log "Starting application in Firecracker microVM mode..."
        if [ ! -e /dev/kvm ]; then
            echo "Error: /dev/kvm does not exist. Firecracker requires hardware virtualization." >&2
            exit 1
        fi

        if [ ! -f "${ROOTFS_PATH}" ]; then
            echo "Error: Rootfs image not found at ${ROOTFS_PATH}. Run prepare_rootfs.sh first." >&2
            exit 1
        fi

        # Generate config.json dynamically
        log "Generating ${CONFIG_PATH}..."
        cat <<EOF > "${CONFIG_PATH}"
{
  "kernel_image_path": "${KERNEL_PATH}",
  "boot-source": {
    "kernel_image_path": "${KERNEL_PATH}",
    "boot_args": "console=ttyS0 reboot=k panic=1 pci=off noapic nommconf"
  },
  "boot_timeout_ms": 10000,
  "machine_config": {
    "vm_name": "${VM_NAME}",
    "cpu_model": "host",
    "cpu_count": 2,
    "mem_size": 4096,
    "port_mappings": [
      {
        "guest_port": ${APP_PORT},
        "host_port": ${APP_PORT},
        "host_protocol": "tcp"
      }
    ]
  },
  "drives": [
    {
      "drive_id": "root",
      "path_on_host": "${ROOTFS_PATH}",
      "is_root_device": true
    }
  ]
}
EOF

        rm -f "${SOCK_PATH}"
        "${FIRECRACKER_BIN}" --config-file "${CONFIG_PATH}" --api-sock "${SOCK_PATH}" &
        APP_PID=$!
        echo "${APP_PID}" > .vm_pid
        log "Firecracker started with PID: ${APP_PID}"

        wait_for_health
        run_tests
        ;;

    *)
        echo "Error: Unsupported mode: ${MODE}" >&2
        usage
        ;;
esac
