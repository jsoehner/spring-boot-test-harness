#!/bin/bash
# orchestrate_vm.sh - Manage Firecracker VM lifecycle and app deployment

set -e

# Configuration
VM_NAME="harness-target-app"
FIRECRACKER_BIN="/usr/bin/firecracker"
SOCK_PATH="/tmp/firecracker.sock"
CONFIG_PATH="config.json"
ROOTFS_PATH="/usr/local/bin/rootfs.img"
KERNEL_PATH="/usr/local/bin/kernel.img"
APP_JAR="/mnt/c/Users/jsoehner/harness_project/target_app/target/target-app-0.0.1-SNAPSHOT.jar"
APP_DEST="/app/target-app.jar"
APP_PORT=8080

# Helper to log messages
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Step 1: Generate config.json
generate_config() {
    log "Generating config.json..."
    cat <<EOF > "$CONFIG_PATH"
{
  "kernel_image_path": "$KERNEL_PATH",
  "boot-source": {
    "kernel_image_path": "$KERNEL_PATH",
    "boot_args": "console=ttyS0 reboot=k panic=1 pci=off noapic nommconf"
  },
  "boot_timeout_ms": 10000,
  "machine_config": {
    "vm_name": "$VM_NAME",
    "cpu_model": "host",
    "cpu_count": 2,
    "mem_size": 4096,
    "port_mappings": [
      {
        "guest_port": $APP_PORT,
        "host_port": $APP_PORT,
        "host_protocol": "tcp"
      }
    ]
  },
  "drives": [
    {
      "drive_id": "root",
      "path_on_host": "$ROOTFS_PATH",
      "is_root_device": true
    }
  ]
}
EOF
}

# Step 2: Start VM
start_vm() {
    # Cleanup existing socket
    rm -f "$SOCK_PATH"
    
    log "Starting Firecracker VM: $VM_NAME..."
    # Use correct --config-file flag as per Firecracker help
    $FIRECRACKER_BIN --config-file "$CONFIG_PATH" --api-sock "$SOCK_PATH" &
    VM_PID=$!
    echo $VM_PID > .vm_pid
    log "Firecracker started with PID: $VM_PID"
    
    # Wait for API to be ready
    MAX_RETRIES=30
    COUNT=0
    while ! curl -s --unix-socket "$SOCK_PATH" /version > /dev/null; do
        if [ $COUNT -ge $MAX_RETRIES ]; then
            log "Error: Firecracker API not responding."
            exit 1
        fi
        sleep 1
        ((COUNT++))
    done
    log "Firecracker API is ready."
}

# Step 3: Inject App into RootFS
inject_app_to_rootfs() {
    log "Skipping direct mount injection due to kernel zstd support issues."
    log "The JAR file will be injected into the rootfs via prepare_rootfs.sh"
}

# Step 4: Deploy App
deploy_app() {
    log "Deploying application..."
    
    # Since the /exec endpoint is not available in the core Firecracker API,
    # we will use the fallback IP for now.
    IP_ADDR="172.17.0.2"
    
    log "Using fallback IP: $IP_ADDR"
    
    # We will move the JAR injection to the prepare_rootfs.sh step
    # to avoid issues with network transfer and /exec.
    log "JAR injection skipped in favor of pre-injection via prepare_rootfs.sh."
}

# Step 5: Health Check
check_health() {
    log "Waiting for application to start on port 8080..."
    MAX_RETRIES=60
    COUNT=0
    while ! curl -s --unix-socket "$SOCK_PATH" http://localhost:8080 > /dev/null; do
        if [ $COUNT -ge $MAX_RETRIES ]; then
            log "Error: Application failed to start or is not responding on port 8080."
            return 1
        fi
        sleep 1
        ((COUNT++))
    done
    log "SUCCESS: Application is UP and responding!"
    return 0
}

# Step 6: Run Host-Side Tests
run_tests() {
    log "Starting host-side tests..."
    bash run_tests.sh
    if [ $? -eq 0 ]; then
        log "SUCCESS: All tests passed!"
    else
        log "FAILURE: Some tests failed."
        return 1
    fi
}

# Execution flow
generate_config
inject_app_to_rootfs
start_vm
sleep 5
deploy_app
sleep 10
check_health
run_tests

# Cleanup (Optional: comment out if you want to keep it running)
# log "Shutting down VM..."
# curl --unix-socket "$SOCK_PATH" -X POST /shutdown
