# Troubleshooting the Test Harness

This guide helps resolve common issues encountered when setting up and running the Spring Boot Test Harness.

## Firecracker VM Issues

### VM Fails to Start
- **Check `config.json`**: Ensure `memory` (e.g., 2048) and `cpus` (e.g., 2) are within your host's limits.
- **Rootfs Issues**: Ensure `prepare_rootfs.sh` completed successfully and `rootfs.img` is accessible.
- **Kernel Support**: Verify that your host kernel supports KVM. Run `lsmod | grep kvm` to check.

### Network Connectivity
- **Port Conflict**: Ensure port 8080 is not being used by another process. Run `netstat -ano | findstr :8080`.
- **Firewall Rules**: Ensure the host firewall allows traffic on the mapped ports.
- **IP Mapping**: Check `orchestrate_vm.sh` to ensure the correct network interface is being used.

## Application Issues

### Health Check Fails
- **Build Status**: Verify `build_app.sh` successfully generated the JAR in `target_app/target/`.
- **Startup Logs**: Check the VM's console output (via `orchestrate_vm.sh`) to see if the Spring Boot application crashed during startup.
- **Port Mismatch**: Ensure the application is actually listening on port 8080 inside the VM.

### Test Failures
- **Fuzzer 500 Errors**: If the fuzzer reports many 500 errors, check the application logs to see if the inputs are causing unhandled exceptions.
- **Race Condition Failures**: If the concurrency test fails, check the `WorkOrderService` logic to ensure synchronization is correctly applied.
- **Dependency Issues**: Ensure `requirements.txt` is installed (`pip install -r requirements.txt`).
