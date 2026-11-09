#!/usr/bin/env python3
"""
Mock server for the Spring Boot target application.
Provides simulated endpoints for health checks, fuzzer targets, and order billing.
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import re
import threading

order_db = {
    "101": {"status": "PENDING", "ownerId": "user1"},
    "102": {"status": "PENDING", "ownerId": "user2"}
}
order_lock = threading.Lock()

class SimpleHandler(BaseHTTPRequestHandler):
    def _send_json(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('Content-Security-Policy', "default-src 'self'")
        self.send_header('Strict-Transport-Security', 'max-age=31536000; includeSubDomains')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode('utf-8'))

    def _send_text(self, status_code, text):
        self.send_response(status_code)
        self.send_header('Content-Type', 'text/plain;charset=UTF-8')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('X-Frame-Options', 'DENY')
        self.send_header('Content-Security-Policy', "default-src 'self'")
        self.send_header('Strict-Transport-Security', 'max-age=31536000; includeSubDomains')
        self.end_headers()
        self.wfile.write(text.encode('utf-8'))

    def do_GET(self):
        path = self.path.split('?')[0]
        if path == '/actuator/health':
            self._send_json(200, {"status": "UP"})
        elif path == '/hello':
            self._send_text(200, "Hello World")
        elif path == '/actuator/env':
            self._send_json(200, {"activeProfiles": ["mock"]})
        else:
            self._send_text(404, "Not Found")

    def do_POST(self):
        path = self.path.split('?')[0]
        match_bill = re.match(r"^/api/orders/bill/([^/]+)$", path)
        if match_bill:
            order_id = match_bill.group(1)
            api_key = self.headers.get("X-API-KEY")
            user_id = self.headers.get("X-USER-ID")

            if api_key != "secure-secret-key":
                self._send_text(401, "Error: Invalid API Key")
                return
            if not user_id:
                self._send_text(401, "Error: User ID required")
                return
            if not order_id.isdigit():
                self._send_text(400, "Error: Invalid Order ID format. Must be numeric.")
                return

            with order_lock:
                order = order_db.get(order_id)
                if not order:
                    self._send_text(400, "Request failed")
                    return
                if order["ownerId"] != user_id:
                    self._send_text(400, "Request failed")
                    return
                if order["status"] == "PENDING":
                    order["status"] = "BILLED"
                    self._send_text(200, f"Order {order_id} billed successfully")
                    return
                else:
                    self._send_text(400, "Request failed")
                    return

        self._send_text(404, "Not Found")

    def log_message(self, format, *args):
        # Quiet standard HTTP access logs
        pass

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    server = HTTPServer(('0.0.0.0', port), SimpleHandler)
    print(f"Mock server running on port {port}...")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down mock server.")
        server.server_close()
