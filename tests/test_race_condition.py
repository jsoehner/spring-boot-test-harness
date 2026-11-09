import requests
import threading
import sys

BASE_URL = "http://localhost:8080"
AUTH_HEADERS = {
    "X-API-KEY": "secure-secret-key",
    "X-USER-ID": "user1"
}

results = []
results_lock = threading.Lock()

def bill_order_concurrently(order_id):
    try:
        response = requests.post(
            f"{BASE_URL}/api/orders/bill/{order_id}",
            headers=AUTH_HEADERS,
            timeout=5
        )
        with results_lock:
            results.append((response.status_code, response.text))
        print(f"Thread {threading.current_thread().name} - Bill {order_id}: {response.status_code} {response.text}")
    except Exception as e:
        with results_lock:
            results.append((None, str(e)))
        print(f"Thread {threading.current_thread().name} - Bill {order_id} Error: {e}")

def test_race_condition():
    """
    Attempts to trigger a race condition in the billOrder method.
    Sends concurrent requests to bill the same order and verifies that
    due to synchronization, exactly one request succeeds.
    """
    order_id = "101"
    threads = []
    
    print(f"Starting concurrent bill requests for order {order_id}...")
    for i in range(5):
        t = threading.Thread(target=bill_order_concurrently, args=(order_id,), name=f"T{i}")
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    # Check final state by sending another bill request (should fail since already billed)
    final_response = requests.post(
        f"{BASE_URL}/api/orders/bill/{order_id}",
        headers=AUTH_HEADERS,
        timeout=5
    )
    print(f"Post-test bill attempt status for {order_id}: {final_response.status_code} {final_response.text}")

    success_count = sum(1 for status, text in results if status == 200 and "billed successfully" in text)
    print(f"\n[Race Condition Test Summary] Successful bill operations: {success_count} / {len(results)}")
    if success_count == 1:
        print("[+] Concurrency test PASSED: Exactly 1 request successfully transitioned order state.")
        return True
    else:
        print(f"[-] Concurrency test FAILED: Expected 1 successful billing, got {success_count}.")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        BASE_URL = sys.argv[1].rstrip("/")
    success = test_race_condition()
    sys.exit(0 if success else 1)
