# Spring Boot Test Harness

## Overview
This project provides a high-fidelity security and logic testing environment for Spring Boot applications. It leverages **Firecracker VMs** to create isolated sandboxes, allowing for safe and reproducible execution of security scans, fuzzing, and concurrency tests.

## Key Features
- **Firecracker VM Orchestration**: Automated lifecycle management of lightweight VMs.
- **Security Scanning**: Automated checks for security headers, information leakage, and known vulnerabilities.
- **Fuzzing**: Automated generation and injection of payloads to identify unhandled exceptions and crashes.
- **Concurrency Testing**: Dedicated test suite to identify race conditions in core business logic.
- **Knowledge Capture**: Integrated system for recording architectural decisions and bug fixes.

## Tech Stack
- **Language**: Java 17, Python 3.x
- **Frameworks**: Spring Boot 3.2.0, Apache Camel
- **Infrastructure**: Firecracker, WSL2 (Fedora)
- **Testing**: Pytest, Requests, Custom Fuzzers

## Quick Start
### Prerequisites
- WSL2 with Fedora installed.
- Firecracker installed and configured.
- Maven and Java 17.

### Setup
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Build the target application:
   ```bash
   ./build_app.sh
   ```
4. Run the full test harness:
   ```bash
   ./run_harness.sh
   ```

## Project Structure
- `harness/`: Core testing tools (scanner, fuzzer, etc.).
- `target_app/`: The Spring Boot application being tested.
- `tests/`: Pytest-based test suites.
- `sandbox/`: Firecracker configuration and rootfs management.
- `memory_system/`: Knowledge base for architectural decisions and bug fixes.

## Contributing
This is an internal project. Please coordinate with the platform team before making changes to the core orchestration scripts.
