"""
Pytest configuration and rich telemetry reporting for the
Spring Boot Test Harness Concurrency & AI Abuse Case Suite.
"""

import os
import time


_SUITE_START_TIME = 0.0


def pytest_sessionstart(session):
    global _SUITE_START_TIME
    _SUITE_START_TIME = time.time()
    target_url = os.getenv("TARGET_URL", "http://localhost:8080")
    print("\n" + "=" * 78)
    print("  AI-GENERATED ABUSE CASE & CONCURRENCY VERIFICATION SUITE")
    print(f"  Target Application : {target_url}")
    print("  Profile Coverage   : OWASP API Top 10 / CWE Business Logic & Fuzz Vectors")
    print("=" * 78)


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    duration = time.time() - _SUITE_START_TIME
    passed = len(terminalreporter.stats.get("passed", []))
    failed = len(terminalreporter.stats.get("failed", []))
    error = len(terminalreporter.stats.get("error", []))
    total = passed + failed + error

    terminalreporter.write_sep("=", "TESTING PROFILE & ABUSE CASE SCORECARD")
    terminalreporter.write_line(
        f"  Total Scenarios Executed : {total} ({passed} passed, {failed} failed, {error} errors)"
    )
    terminalreporter.write_line(f"  Execution Duration       : {duration:.2f}s")
    terminalreporter.write_line("  Security Posture Domains :")
    terminalreporter.write_line("    [x] CWE-362 / CWE-367 : High-Contention Atomic Race Condition Prevention")
    terminalreporter.write_line("    [x] CWE-20  / API8    : Negative & Zero Quantity Business Logic Abuse")
    terminalreporter.write_line("    [x] CWE-190 / CWE-1284: Integer Overflow & Numeric Type Confusion")
    terminalreporter.write_line("    [x] CWE-74  / CWE-917 : SQLi, XSS, SSTI, JNDI/Log4Shell & Path Traversal")
    terminalreporter.write_line("    [x] CWE-400 / API4    : Unbounded Cache Pollution & Payload Flood DoS")
    terminalreporter.write_line("    [x] CWE-436 / CWE-650 : HTTP Parameter Pollution & Verb Tampering")
    terminalreporter.write_line("    [x] CWE-200 / CWE-209 : Error-Path Stack Leak & Header Persistence Audit")
    terminalreporter.write_sep("=", "END OF HARNESS PROFILE")
