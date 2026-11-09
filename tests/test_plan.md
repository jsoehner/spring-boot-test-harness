# Test Plan for Target Application

## Overview
This plan covers the testing of the `TargetApplication` which provides an order management API.

## Scope
- `POST /api/orders/bill/{id}`
- `POST /api/orders/ship/{id}`

## Test Cases

### 1. Unit Tests (WorkOrderService)
- `testBillOrder_Success`: Bill a pending order.
- `testBillOrder_NotFound`: Bill a non-existent order.
- `testBillOrder_AlreadyBilled`: Bill an order already in BILLED state.
- `testShipOrder_Success`: Ship a billed order.
- `testShipOrder_NotFound`: Ship a non-existent order.
- `testShipOrder_NotBilled`: Ship an order that is still PENDING.
- `testShipOrder_AlreadyShipped`: Ship an order already in SHIPPED state.

### 2. Integration Tests (OrderController)
- `testBillOrder_ValidId`: Successful billing with numeric ID.
- `testBillOrder_InvalidId`: Error message for non-numeric ID.
- `testShipOrder_ValidId`: Successful shipping with numeric ID.
- `testShipOrder_InvalidId`: Error message for non-numeric ID.
- `testBillOrder_OrderNotFound`: 404/Error for non-existent ID.
- `testShipOrder_OrderNotFound`: 404/Error for non-existent ID.

### 3. Concurrency Tests
- `testConcurrentBillOrder`: Multiple threads attempting to bill the same order simultaneously.
- `testConcurrentShipOrder`: Multiple threads attempting to ship the same order simultaneously.

### 4. Functional/E2E Tests (Python/Requests)
- `test_api_flow_success`: Full flow from PENDING -> BILLED -> SHIPPED.
- `test_api_flow_invalid_id`: Verify error responses for bad inputs.
- `test_api_flow_concurrency`: Verify that only one thread succeeds in a race condition.

### 5. AI-Generated Adversarial Abuse Cases (`tests/test_ai_abuse_cases.py` & `tests/test_inventory_concurrency.py`)
- `test_abuse_01_negative_and_zero_quantity_manipulation`: Blocks negative/zero reservation quantities and stock inflation (`CWE-20` / `OWASP API8`).
- `test_abuse_02_integer_overflow_and_type_confusion`: Rejects 128-bit integer overflows, hex literals (`0x10`, `#10`), floats, `NaN`, `Infinity`, and non-numeric types (`CWE-190` / `CWE-1284`).
- `test_abuse_03_injection_vector_battery`: Blocks SQLi, XSS, SSTI, JNDI/Log4Shell, SpEL, Path Traversal, and empty-string default coercion (`CWE-74` / `CWE-917`).
- `test_abuse_04_unbounded_cache_pollution_dos`: Prevents phantom SKU reservations and oversized SKU payloads from allocating unbounded in-memory map entries (`CWE-400` / `OWASP API4`).
- `test_abuse_05_http_parameter_pollution_and_verb_tampering`: Blocks duplicate query parameters (`PARAMETER_POLLUTION`) and disallowed HTTP verbs (`405 METHOD_NOT_ALLOWED`) (`CWE-436` / `CWE-650`).
- `test_abuse_06_control_chars_and_oversized_payloads`: Rejects null bytes, CRLF header splitting, ANSI escapes, and 4 KB / 8 KB URI floods (`CWE-158` / `CWE-400`).
- `test_abuse_07_error_path_security_header_persistence`: Verifies security headers and zero stack trace leakage across `400`, `404`, `405`, and `409` responses (`CWE-200` / `CWE-209`).
- `test_abuse_08_adversarial_mixed_concurrency_invariant`: 20-thread mixed legitimate + adversarial burst verifying strict inventory conservation (`reserved + remaining == initial_stock`) (`CWE-362` / `CWE-367`).
- `test_inventory_single_item_race_condition` & `test_inventory_multi_unit_depletion_race_condition`: 10-thread single-unit and 15-thread multi-unit atomic depletion verification.
