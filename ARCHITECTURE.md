# Architecture Documentation: Spring Boot Test Harness

## Executive Summary
The Spring Boot Test Harness is a high-fidelity, isolated execution environment designed to identify logic flaws, race conditions, and security vulnerabilities in enterprise Spring Boot applications. By utilizing Firecracker microVMs, the harness provides a production-like environment with minimal overhead, ensuring that security tests and performance benchmarks are both accurate and safe.

## Architecture Overview
The system follows a "Sandbox-as-a-Service" model. The host machine orchestrates the lifecycle of a Firecracker VM, which hosts a pre-configured rootfs containing the target Spring Boot application. The harness then interacts with the VM via exposed network ports to perform various testing modalities.

### Key Components
- **Orchestrator (`orchestrate_vm.sh`)**: The central controller. It handles VM creation, network mapping, application deployment, and health checks.
- **Rootfs Manager (`prepare_rootfs.sh`)**: Responsible for preparing the squashfs image, injecting the application JAR, and ensuring the environment is consistent.
- **Test Runner (`run_harness.sh`)**: Executes the test suite, including security scans, fuzzers, and concurrency tests.
- **Security Scanner**: Analyzes HTTP responses for header compliance and information leaks.
- **Fuzzer**: Generates and injects semi-random payloads to probe for 500-series errors and crashes.
- **Concurrency Suite**: Specialized tests to detect race conditions in stateful business logic.
- **Knowledge Capture**: Integrated system for capturing and retrieving architectural decisions and bug fixes.

## Design Decisions
- **Isolation Mechanism**: Firecracker was chosen over Docker/Kata for its significantly smaller footprint and faster startup times, which are critical for rapid CI/CD feedback loops.
- **PQC Readiness**: The harness is designed to support applications using ML-KEM-768 for quantum-resilient key exchange, ensuring compatibility with future-proof security standards.
- **State Management**: The `memory_system` uses an OKF (Knowledge Framework) and ChromaDB to capture and retrieve engineering lessons learned during the testing process.

## Data Flow
1. **Initialization**: Orchestrator triggers `prepare_rootfs.sh` -> VM is started.
2. **Deployment**: Target JAR is injected into the VM; Spring Boot starts on port 8080.
3. **Verification**: Orchestrator performs a health check.
4. **Execution**: `run_harness.sh` triggers the Scanner, Fuzzer, and Concurrency tests.
5. **Capture**: Results and findings are captured into the `memory_system`.

## Security Model
- **Network Isolation**: The VM is isolated from the host network except for the specific ports exposed for testing.
- **Zero-Persistence**: Each test run uses a fresh VM instance to prevent cross-test contamination.
- **Least Privilege**: The application runs as a non-root user inside the VM.

## Performance Characteristics
- **Startup Time**: < 2 seconds for VM boot and app readiness.
- **Throughput**: The fuzzer is designed to run parallel requests to maximize coverage per test run.

## Troubleshooting
- **Port Conflict**: Ensure port 8080 is not occupied on the host.
- **VM Fail to Start**: Check `config.json` for correct memory and CPU allocations.
- **Health Check Failure**: Verify that `build_app.sh` correctly generated the JAR and it is present in `/app`.
