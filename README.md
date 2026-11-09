# Spring Boot Test Harness

## Overview
This project provides a high-fidelity security and logic testing environment for Spring Boot applications. It leverages **Firecracker VMs** to create isolated sandboxes, allowing for safe and reproducible execution of security scans, fuzzing, and concurrency tests.

## Key Features
- **Firecracker VM Orchestration**: Automated lifecycle management of lightweight VMs.
- **Security Scanning**: Automated checks for security headers, information leakage, and known vulnerabilities.
- **Fuzzing**: Automated generation and injection of payloads to identify unhandled exceptions and crashes.
- **AI-Generated Abuse Case Battery**: Built-in adversarial test suite (`tests/test_ai_abuse_cases.py`) mapped to OWASP API Security Top 10 & CWE (negative/zero quantity manipulation, 128-bit integer overflow & hex type confusion, SQLi/XSS/SSTI/JNDI/traversal payloads, cache pollution DoS, HTTP parameter pollution, verb tampering, control-character & URI flooding, and error-path header persistence).
- **Concurrency & Conservation Testing**: Single-unit, multi-unit, and 20-thread mixed legitimate/adversarial race condition suites (`tests/test_inventory_concurrency.py`, `tests/test_race_condition.py`).
- **Multi-Project Test Syncing**: Sync the full AI abuse case and concurrency suite into any new or existing Spring Boot repository with `./scripts/sync_harness_tests.sh <target-repo>`.
- **Knowledge Capture**: Integrated system for recording architectural decisions and bug fixes.

## Tech Stack
- **Language**: Java 17+, Python 3.x
- **Frameworks**: Spring Boot 3.2.0, Apache Camel
- **Infrastructure**: Firecracker (Linux/WSL2 KVM), Direct Local Execution (macOS/Linux/Windows), Mock Server
- **Testing**: Pytest, Requests, Custom Fuzzers

## Operating System Support & Execution Modes
The test harness supports multiple operating systems through selectable and auto-detected execution modes:
- **Direct Mode (`--mode direct`)**: Runs the Spring Boot application natively via Java on host. **Recommended for macOS and Windows**, or Linux without KVM.
- **Firecracker Mode (`--mode firecracker`)**: Runs inside lightweight Firecracker microVMs. Requires Linux with KVM enabled (`/dev/kvm`, e.g., Fedora / Ubuntu on bare-metal or WSL2).
- **Mock Mode (`--mode mock`)**: Runs a lightweight mock server for fast sanity testing without building Java artifacts.
- **Auto Mode (`--mode auto`, Default)**: Automatically detects host capabilities (macOS vs Linux KVM) and chooses the appropriate mode.

## Quick Start
### Prerequisites
- **macOS**: `brew install openjdk@17 maven python`
- **Linux (Debian/Ubuntu)**: `sudo apt-get install openjdk-17-jdk maven python3 python3-pip python3-venv`
- **Linux (Fedora/WSL2)**: `sudo dnf install java-17-openjdk-devel maven python3 firecracker kata-runtime`
- **Windows**: WSL2 with Linux or native PowerShell/Java 17+.

### Setup & Run
1. Clone the repository.
2. Run environment setup (optional, automatically sets up dependencies):
   ```bash
   ./setup_sandbox.sh
   ```
3. Build and execute the full test lifecycle automatically:
   ```bash
   ./orchestrate_vm.sh
   ```
   Or explicitly choose an execution mode:
   ```bash
   ./orchestrate_vm.sh --mode direct   # Native host execution (ideal for macOS)
   ./orchestrate_vm.sh --mode mock     # Fast Python mock server execution
   ./orchestrate_vm.sh --mode firecracker # Linux microVM execution
   ```

## Syncing Tests to Any New or Existing Project
To sync the AI-Generated Abuse Case and Concurrency test suite into another Spring Boot repository:
```bash
./scripts/sync_harness_tests.sh /path/to/your-spring-boot-repo
```
Even if a target project does not define custom tests, `run_harness.sh` automatically executes the built-in `tests/test_ai_abuse_cases.py` and `tests/test_inventory_concurrency.py` suites against the target service.

## Project Structure
- `harness/`: Core testing tools (scanner, fuzzer, etc.).
- `target_app/`: The Spring Boot application being tested.
- `tests/`: Pytest-based test suites (`test_app_health.py`, `test_ai_abuse_cases.py`, `test_inventory_concurrency.py`, `test_race_condition.py`).
- `scripts/sync_harness_tests.sh`: Utility to sync harness test cases into external repositories.
- `sandbox/`: Firecracker configuration and rootfs management.
- `memory_system/`: Knowledge base for architectural decisions and bug fixes.

## Contributing
This is an internal project. Please coordinate with the platform team before making changes to the core orchestration scripts.
