feat(harness): add AI-generated abuse case suite and multi-project test sync

Expand the Spring Boot Test Harness testing profile with an 8-category
AI-generated adversarial abuse case battery, multi-unit concurrency
verification, and a cross-repository test synchronization utility.

What changed:
- Add `tests/test_ai_abuse_cases.py` covering OWASP API Security Top 10 and
  CWE abuse vectors:
  - ABUSE-01 (CWE-20 / API8): Negative/zero reservation quantity & stock
    inflation blocking
  - ABUSE-02 (CWE-190 / CWE-1284): 128-bit integer overflow, hex literal
    bypass (`0x10`, `#10`), float, NaN/Infinity, and type confusion
  - ABUSE-03 (CWE-74 / CWE-917): SQLi, XSS, SSTI, Log4Shell/JNDI, SpEL,
    Path Traversal, and empty-string default coercion battery
  - ABUSE-04 (CWE-400 / API4): Unbounded memory allocation / phantom SKU
    cache pollution DoS prevention
  - ABUSE-05 (CWE-436 / CWE-650): HTTP Parameter Pollution (HPP) and
    disallowed HTTP verb tampering (`405 METHOD_NOT_ALLOWED`)
  - ABUSE-06 (CWE-158 / CWE-400): Null bytes, CRLF header splitting, ANSI
    escapes, and 4 KB / 8 KB URI flood boundary checks
  - ABUSE-07 (CWE-200 / CWE-209): Error-path security header persistence and
    stack trace leak suppression across 400/404/405/409 responses
  - ABUSE-08 (CWE-362 / CWE-367): 20-thread mixed legitimate + adversarial
    concurrency burst verifying strict inventory conservation invariants
- Add `tests/test_inventory_concurrency.py`, `tests/conftest.py`, and
  `tests/pytest.ini` for single-unit/multi-unit race condition checks and
  scorecard telemetry reporting.
- Add `scripts/sync_harness_tests.sh` and update `run_harness.sh` so any
  new or existing Spring Boot project automatically executes or syncs the
  expanded test suite.
- Harden internal `TargetApplication.java`, `application.properties`, and
  `mock_server.py` to enforce security headers, parameter validation, and
  error-path hygiene across both `--mode direct` and `--mode mock`.

Why it changed:
- Strengthen the centralized testing profile beyond basic health and header
  checks so all connected Spring Boot microservices are continuously audited
  against realistic AI-synthesized business logic and protocol abuse cases.
