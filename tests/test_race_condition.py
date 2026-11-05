import requests
import threading
import time

BASE_URL = "http://localhost:8080"

def bill_order_concurrently(order_id):
    try:
        response = requests.post(f"{BASE_URL}/api/orders/bill/{order_id}")
        print(f"Thread {threading.current_thread().name} - Bill {order_id}: {response.status_code} {response.text}")
    except Exception as e:
        print(f"Thread {threading.current_thread().name} - Bill {order_id} Error: {e}")

def test_race_condition():
    """
    Attempts to trigger a race condition in the billOrder method.
    We will send concurrent requests to bill the same order.
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

    # Check final state
    response = requests.get(f"{BASE_URL}/api/orders/bill/{order_id}")
    print(f"Final status for {order_id}: {response.text}")

if __name__ == "__main__":
    test_race_condition()
