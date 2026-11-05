import requests
import sys

def check_security_headers(url):
    print(f"[*] Checking security headers for {url}...")
    try:
        response = requests.get(url)
        headers = response.headers
        
        checks = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Content-Security-Policy": "default-src 'self'",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
        }
        
        issues = []
        for header, expected in checks.items():
            if header not in headers:
                issues.append(f"Missing {header}")
            elif headers[header] != expected:
                issues.append(f"Incorrect {header}: Expected {expected}, got {headers[header]}")
        
        if issues:
            print(f"[!] Found {len(issues)} security header issues:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("[+] All security headers are present and correct.")
            
    except requests.exceptions.RequestException as e:
        print(f"[!] Error connecting to {url}: {e}")

def check_info_leak(url):
    print(f"[*] Checking for information disclosure...")
    try:
        response = requests.get(url)
        server = response.headers.get("Server")
        if server:
            print(f"[!] Information disclosure: 'Server' header is present ({server})")
        else:
            print("[+] 'Server' header is hidden.")
    except requests.exceptions.RequestException as e:
        print(f"[!] Error: {e}")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"
    check_security_headers(target)
    check_info_leak(target)
