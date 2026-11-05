import requests
import random
import string
import sys

def generate_fuzz_payload(length=20):
    return ''.join(random.choices(string.ascii_letters + string.digits + string.punctuation, k=length))

def fuzz_endpoint(url, path):
    print(f"[*] Fuzzing {url}{path}...")
    for _ in range(10):
        payload = generate_fuzz_payload()
        try:
            response = requests.get(f"{url}{path}", params={"input": payload})
            if response.status_code >= 500:
                print(f" [!] CRITICAL: 500 Internal Server Error with payload: {payload}")
            elif response.status_code == 200:
                pass # Success
        except requests.exceptions.RequestException as e:
            print(f" [!] Connection error during fuzzing: {e}")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"
    endpoints = ["/hello", "/actuator/env"]
    
    for endpoint in endpoints:
        fuzz_endpoint(target, endpoint)
