# 0. Record Architecture Decisions

- **Status**: Accepted
- **Date**: 2026-11-05
- **Security Classification**: Internal
- **Decision Makers**: Architecture Review Board & Security Team

## Context
We need to record architecturally significant decisions, security controls, cryptographic choices, and compliance exception rationale.

## Decision
We will use Architectural Decision Records (ADRs) and Security ADRs stored directly in docs/adr/. All significant design choices affecting security, data boundaries, or system architecture must be documented here.

## Consequences
- Architectural rationale and security decisions are preserved in git.
- Pull requests modifying security-sensitive architecture are checked for corresponding ADRs.
- Superseded decisions will be linked bidirectionally.
