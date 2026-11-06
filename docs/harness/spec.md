# Test Harness Specification

## Overview
The test harness provides automated security and functional validation for the Spring Boot target application. It operates by deploying the application into a Firecracker VM and running a suite of tests from the host.

## Components

### 1. Security Scanner (`harness/security_scanner.py`)
- **Purpose**: Detects common security misconfigurations and information leaks.
- **Methodology**: 
    - Performs HTTP GET requests to key endpoints.
    - Inspects response headers for security best practices (e.g., `X-Content-Type-Options`, `X-Frame-Options`).
    - Scans for information disclosure in headers (e.g., `Server` header).
- **Output**: A summary of found issues with severity levels.

### 2. Fuzzer (`harness/fuzzer.py`)
- **Purpose**: Identifies unhandled exceptions and potential crashes via random input injection.
- **Methodology**:
    - Generates semi-random strings (alphanumeric, symbols, and special characters).
    - Iteratively sends these payloads to defined API endpoints (`/hello`, `/actuator/env`).
    - Monitors for 500-series Internal Server Error responses.
- **Output**: Logs every request and flags any 500-series errors with the specific payload.

### 3. Concurrency Suite (`tests/test_race_condition.py`)
- **Purpose**: Validates the fix for the race condition in `WorkOrderService`.
- **Methodology**:
    - Uses Python's `threading` module to spawn multiple concurrent requests.
    - Attempts to bill the same order ID simultaneously.
    - Verifies that the state transition remains consistent (i.e., only one request succeeds in billing).

## Integration Workflow
1. **Environment Setup**: `orchestrate_vm.sh` prepares the Firecracker VM and deploys the JAR.
2. **Health Check**: The harness verifies the app is reachable on port 8080.
3. **Execution**: `run_harness.sh` executes the Scanner, Fuzzer, and Concurrency tests in sequence.
4. **Reporting**: Results are logged to the console and can be captured into the project's knowledge base.
