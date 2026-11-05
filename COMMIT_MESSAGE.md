# Initial Setup of Test Harness and Core Fixes

## Summary
This commit establishes the core infrastructure for the Spring Boot Test Harness, enabling automated security scanning, fuzzing, and concurrency testing within a Firecracker VM environment. It also includes critical logic fixes for the target application.

## Changes
### Harness Infrastructure
- Added Firecracker VM orchestration scripts (`orchestrate_vm.sh`, `prepare_rootfs.sh`).
- Implemented host-side test suite (`run_harness.sh`) including:
    - Security scanner for header compliance and info disclosure.
    - Fuzzer for endpoint resilience.
    - Concurrency tests for race condition detection.
- Configured `memory_system` for capturing engineering lessons and architectural decisions.

### Target Application Fixes
- **Race Condition**: Resolved atomicity issues in `WorkOrderService` by implementing synchronized state transitions.
- **Input Validation**: Enforced strict numeric validation for order IDs in `OrderController`.

### Documentation
- Added `README.md` and `ARCHITECTURE.md` to document the harness's design and usage.

## Impact
- Enables rapid, safe identification of security and logic flaws.
- Provides a repeatable environment for regression testing and fuzzing.
- Standardizes the knowledge capture process for the project.
