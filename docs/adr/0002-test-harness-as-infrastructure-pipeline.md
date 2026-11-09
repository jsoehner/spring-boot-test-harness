# ADR 0002: Test-Harness-as-a-Service (THaaS) Infrastructure & Cross-Repository Pipeline

- **Status**: Accepted
- **Date**: 2026-11-09
- **Security Classification**: Internal
- **Decision Makers**: Platform Engineering & Security Architecture
- **Related ADRs**: [ADR 0000](0000-record-architecture-decisions.md), [ADR 0001](0001-security-threat-model.md)

---

## 1. Context & Problem Statement

The initial test harness implementation was tightly coupled to a single sample application (`target_app`) and assumed a specific Linux environment (WSL2 Fedora with Firecracker and `/dev/kvm`).

This design introduced three major operational bottlenecks:
1. **Lack of Cross-Platform Developer Support**: Developers running macOS (Darwin / Apple Silicon) could not run the harness locally because Firecracker requires Linux KVM hardware virtualization.
2. **Monolithic Repo Coupling**: Testing any new microservice required copying files or modifying the internal `target_app` directory, preventing automated CI/CD integration across separate product repositories.
3. **Fixed Endpoints & Hardcoded Assumptions**: Health checks, fuzzer routes, and concurrency tests assumed fixed paths (`/actuator/health`, `/api/orders/...`) and hardcoded Windows/WSL file paths (`/mnt/c/...`).

We need an infrastructure architecture that functions as a **centralized, reusable testing engine** capable of dynamically evaluating disparate application repositories in CI/CD and across heterogeneous developer workstations.

---

## 2. Decision

We elevate the Spring Boot Test Harness into a **Test-Harness-as-a-Service (THaaS) Infrastructure Platform** through the following architectural mechanisms:

### 2.1 Multi-Tier Runtime Isolation Layer
The infrastructure introduces dynamic runtime tiering based on host operating system and virtualization capabilities:
- **Tier 1: Direct Process Isolation (`--mode direct`)**:
  - The default for **macOS** and environments lacking hardware KVM.
  - Spawns target applications natively with isolated process IDs, health polling, port mapping, and automatic process lifecycle traps (clean termination on exit or failure).
- **Tier 2: MicroVM Hypervisor Isolation (`--mode firecracker`)**:
  - Activated on Linux bare-metal or virtualization-enabled runners with `/dev/kvm`.
  - Packages artifacts into rootfs images and launches dedicated Firecracker microVMs with sub-second boot times.
- **Tier 3: Lightweight Mock Isolation (`--mode mock`)**:
  - Runs a standalone Python server simulating endpoints and headers for rapid pipeline sanity validation without Java or compilation overhead.

### 2.2 Reusable CI/CD Pipeline Gateway
We establish a GitHub Actions Reusable Workflow (`.github/workflows/reusable-harness.yml`) using `workflow_call`. Any external repository across the organization can invoke the test harness infrastructure with declarative inputs:
- `build-command`: Builds Maven or Gradle artifacts inside the caller's context.
- `jar-path`: Explicit or auto-discovered application artifact.
- `health-endpoint`: Microservice readiness path (e.g., `/actuator/health`, `/healthz`, `/ping`).
- `port`: Configurable host and guest port binding.
- `custom-tests-path`: Executes repo-specific business logic and concurrency tests alongside universal security audits.

### 2.3 Parameterized Infrastructure Agent
The core orchestrator ([`orchestrate_vm.sh`](../../orchestrate_vm.sh)) and test runner ([`run_harness.sh`](../../run_harness.sh)) are updated to accept:
- Dynamic JAR location (`--jar PATH`)
- Configurable health probe endpoints (`--health-path PATH`)
- Custom test suites (`--custom-tests PATH`)
- Build bypass flags (`--skip-build`) for pre-compiled CI artifacts

---

## 3. Consequences

### Positive
- **Universal Portability**: Developers on macOS, Linux, and Windows/WSL can execute identical security audits and fuzzing locally before committing code.
- **Fleet-Wide Integration**: Any microservice in the GitHub organization can integrate automated security header auditing, API fuzzing, and race condition detection in under 15 lines of YAML.
- **Zero Redundant Infrastructure**: A single repository maintains security policies, scanner logic, and fuzzer implementations; downstream repos consume updates automatically.
- **Resilient Fallback**: Non-KVM environments seamlessly fall back to direct isolation without pipeline breakage.

### Trade-offs & Mitigations
- *Trade-off*: Direct mode on macOS does not provide microVM hypervisor memory boundary guarantees.
- *Mitigation*: Direct mode is primarily targeted for local development and standard GitHub-hosted runners (`ubuntu-latest`). High-assurance security compliance environments utilize Firecracker runners with KVM enabled.

---

## 4. Security & Compliance Verification

| Control | Implementation |
| :--- | :--- |
| **Authentication & IDOR Enforcement** | Security scanner verifies authentication gates and header compliance across all exposed endpoints. |
| **Zero-Persistence Execution** | All background processes, sockets, and temporary artifacts are destroyed on pipeline completion via shell traps. |
| **Input Fuzzing** | Probe payloads target both common actuator vectors and dynamic endpoints to expose unhandled 500 exceptions. |
| **Pipeline Governance** | ADR Gatekeeper validates architectural changes; Trivy and Semgrep verify dependency and static code security in CI. |
