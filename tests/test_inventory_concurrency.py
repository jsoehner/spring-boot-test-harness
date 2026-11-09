#!/usr/bin/env python3
"""
Custom Concurrency & Race Condition Verification Test
Target Service: Spring Boot Inventory / Order Application
Part of the centralized Spring Boot Test Harness suite.
"""

import os
import sys
import threading
import requests


def _resolve_base_url(base_url=None):
    if not base_url:
        if len(sys.argv) > 1 and sys.argv[1].startswith("http"):
            base_url = sys.argv[1]
        else:
            base_url = os.getenv("TARGET_URL", "http://localhost:8080")
    return base_url.rstrip("/")


def run_inventory_concurrency_test(base_url=None):
    base_url = _resolve_base_url(base_url)

    sku = "SKU-ITEM-001"
    initial_stock = 1
    total_threads = 10

    print(f"\n[Custom Harness Test] Target URL: {base_url}")
    print(f"[Custom Harness Test] Resetting {sku} to stock={initial_stock}...")

    reset_resp = requests.post(
        f"{base_url}/api/inventory/reset",
        params={"sku": sku, "quantity": initial_stock},
        timeout=5,
    )
    if reset_resp.status_code != 200:
        print(f"[!] Failed to reset inventory: HTTP {reset_resp.status_code}")
        sys.exit(1)

    print(f"[Custom Harness Test] Firing {total_threads} concurrent reservation requests for {sku}...")

    results = []
    threads = []
    barrier = threading.Barrier(total_threads)

    def worker(worker_id):
        barrier.wait()
        try:
            resp = requests.post(
                f"{base_url}/api/inventory/reserve",
                params={"sku": sku, "quantity": 1},
                timeout=5,
            )
            results.append((worker_id, resp.status_code, resp.text))
        except Exception as e:
            results.append((worker_id, 0, str(e)))

    for i in range(total_threads):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    success_count = sum(1 for _, code, _ in results if code == 200)
    conflict_count = sum(1 for _, code, _ in results if code == 409)

    for worker_id, code, text in sorted(results, key=lambda x: x[0]):
        print(f"  Worker #{worker_id:02d} -> HTTP {code}: {text.strip()}")

    print(
        f"\n[Custom Test Summary] Success: {success_count}/{total_threads}, "
        f"Conflict (Blocked): {conflict_count}/{total_threads}"
    )

    if success_count == 1 and conflict_count == (total_threads - 1):
        print("[+] SUCCESS: Concurrency test PASSED! Race condition safely handled by application.")
        return True
    else:
        print(
            f"[!] FAILURE: Expected exactly 1 success and {total_threads - 1} conflicts. "
            f"Found {success_count} successes."
        )
        sys.exit(1)


def run_multi_unit_depletion_concurrency_test(base_url=None):
    base_url = _resolve_base_url(base_url)

    sku = "SKU-ITEM-002"
    initial_stock = 5
    total_threads = 15

    print(f"\n[Custom Harness Test] Multi-Unit Depletion: Resetting {sku} to stock={initial_stock}...")
    reset_resp = requests.post(
        f"{base_url}/api/inventory/reset",
        params={"sku": sku, "quantity": initial_stock},
        timeout=5,
    )
    assert reset_resp.status_code == 200

    print(f"[Custom Harness Test] Firing {total_threads} concurrent threads against {initial_stock} available units...")
    results = []
    threads = []
    barrier = threading.Barrier(total_threads)

    def worker(worker_id):
        barrier.wait()
        resp = requests.post(
            f"{base_url}/api/inventory/reserve",
            params={"sku": sku, "quantity": 1},
            timeout=5,
        )
        results.append((worker_id, resp.status_code, resp.json()))

    for i in range(total_threads):
        t = threading.Thread(target=worker, args=(i,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    success_count = sum(1 for _, code, _ in results if code == 200)
    conflict_count = sum(1 for _, code, _ in results if code == 409)

    status_resp = requests.get(f"{base_url}/api/inventory/status/{sku}", timeout=5)
    assert status_resp.status_code == 200
    remaining_stock = status_resp.json().get("available")

    print(
        f"[Multi-Unit Summary] Reserved: {success_count}/{total_threads} (Expected {initial_stock}), "
        f"Blocked (409): {conflict_count}/{total_threads}, Final Stock: {remaining_stock}"
    )

    assert success_count == initial_stock, f"Expected {initial_stock} successes, got {success_count}"
    assert conflict_count == (total_threads - initial_stock)
    assert remaining_stock == 0
    return True


def test_inventory_single_item_race_condition():
    """Pytest entrypoint: 10-thread single-unit TOCTOU race condition check"""
    assert run_inventory_concurrency_test() is True


def test_inventory_multi_unit_depletion_race_condition():
    """Pytest entrypoint: 15-thread multi-unit exact depletion check"""
    assert run_multi_unit_depletion_concurrency_test() is True


if __name__ == "__main__":
    run_inventory_concurrency_test()
    run_multi_unit_depletion_concurrency_test()
