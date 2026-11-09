#!/usr/bin/env python3
"""
Mock server for the Spring Boot target application.
Provides simulated endpoints for health checks, fuzzer targets, inventory reservations, and order billing.
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs, unquote
import json
import re
import time
import threading

order_db = {
    "101": {"status": "PENDING", "ownerId": "user1"},
    "102": {"status": "PENDING", "ownerId": "user2"},
}
order_lock = threading.Lock()

inventory_db = {
    "SKU-ITEM-001": 1,
    "SKU-ITEM-002": 5,
}
inventory_lock = threading.Lock()

VALID_SKU_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")
STRICT_INT_RE = re.compile(r"^-?[0-9]+$")
INT32_MIN = -2147483648
INT32_MAX = 2147483647
MAX_RESERVE_QTY = 1000
MAX_RESET_QTY = 10000
MAX_TRACKED_SKUS = 100


def _has_control_chars(val: str) -> bool:
    return any(ord(c) < 0x20 or ord(c) == 0x7F for c in val)


class SimpleHandler(BaseHTTPRequestHandler):
    def send_response(self, code, message=None):
        """Override to suppress 'Server' header disclosure."""
        self.log_request(code)
        self.send_response_only(code, message)
        self.send_header("Date", self.date_time_string())

    def _send_security_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Content-Security-Policy", "default-src 'self'")
        self.send_header("Strict-Transport-Security", "max-age=31536000; includeSubDomains")

    def _send_json(self, status_code, data):
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self._send_security_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def _send_text(self, status_code, text):
        self.send_response(status_code)
        self.send_header("Content-Type", "text/plain;charset=UTF-8")
        self._send_security_headers()
        self.end_headers()
        self.wfile.write(text.encode("utf-8"))

    def _has_duplicate_params(self, qs):
        return any(len(vals) > 1 for vals in qs.values())

    def do_GET(self):
        if len(self.path) > 8000:
            self._send_text(400, "Bad Request")
            return

        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query, keep_blank_values=True)

        if path in ("/api/inventory/reserve", "/api/inventory/reset"):
            self._send_json(
                405,
                {
                    "error": "METHOD_NOT_ALLOWED",
                    "method": "GET",
                    "message": "HTTP method is not supported for this endpoint",
                },
            )
            return

        if path == "/actuator/health":
            self._send_json(200, {"status": "UP"})
        elif path == "/actuator/info":
            self._send_json(200, {"app": "mock-harness-service"})
        elif path == "/actuator/env":
            self._send_json(200, {"activeProfiles": ["mock"]})
        elif path == "/hello":
            if self._has_duplicate_params(qs):
                self._send_json(
                    400,
                    {
                        "error": "PARAMETER_POLLUTION",
                        "message": "Duplicate query parameters are not permitted",
                    },
                )
                return
            raw_input = qs.get("input", ["world"])[0]
            if len(raw_input) > 256 or _has_control_chars(raw_input):
                self._send_json(
                    400,
                    {
                        "error": "INVALID_INPUT",
                        "message": "Input exceeds maximum length or contains control characters",
                    },
                )
                return
            self._send_json(
                200,
                {
                    "message": "Hello from Sample Spring Boot Service!",
                    "input": raw_input,
                },
            )
        elif path.startswith("/api/inventory/status/"):
            sku = unquote(path[len("/api/inventory/status/") :])
            if not VALID_SKU_RE.match(sku):
                self._send_json(400, {"error": "INVALID_SKU", "message": "SKU format is invalid"})
                return
            with inventory_lock:
                if sku not in inventory_db:
                    self._send_json(404, {"error": "NOT_FOUND"})
                    return
                self._send_json(200, {"sku": sku, "available": inventory_db[sku]})
        else:
            self._send_json(404, {"error": "NOT_FOUND"})

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query, keep_blank_values=True)

        if path == "/api/inventory/reserve":
            if self._has_duplicate_params(qs):
                self._send_json(
                    400,
                    {
                        "error": "PARAMETER_POLLUTION",
                        "message": "Duplicate query parameters are not permitted",
                    },
                )
                return
            sku = qs.get("sku", ["SKU-ITEM-001"])[0]
            if not VALID_SKU_RE.match(sku):
                self._send_json(
                    400,
                    {
                        "error": "INVALID_SKU",
                        "message": "SKU must be 1-64 alphanumeric, dash, or underscore characters",
                    },
                )
                return
            raw_qty = qs.get("quantity", ["1"])[0]
            if not STRICT_INT_RE.match(raw_qty):
                self._send_json(
                    400,
                    {
                        "error": "TYPE_MISMATCH",
                        "parameter": "quantity",
                        "message": "Invalid parameter type or numeric overflow",
                    },
                )
                return
            qty = int(raw_qty)
            if qty < INT32_MIN or qty > INT32_MAX:
                self._send_json(
                    400,
                    {
                        "error": "TYPE_MISMATCH",
                        "parameter": "quantity",
                        "message": "Invalid parameter type or numeric overflow",
                    },
                )
                return
            if qty <= 0 or qty > MAX_RESERVE_QTY:
                self._send_json(
                    400,
                    {
                        "error": "INVALID_QUANTITY",
                        "message": f"Reservation quantity must be between 1 and {MAX_RESERVE_QTY}",
                    },
                )
                return

            with inventory_lock:
                available = inventory_db.get(sku, 0)
                if sku in inventory_db and available >= qty:
                    time.sleep(0.05)
                    inventory_db[sku] -= qty
                    self._send_json(
                        200,
                        {"sku": sku, "status": "RESERVED", "remaining": inventory_db[sku]},
                    )
                else:
                    self._send_json(
                        409,
                        {"sku": sku, "status": "OUT_OF_STOCK", "remaining": available},
                    )
            return

        if path == "/api/inventory/reset":
            if self._has_duplicate_params(qs):
                self._send_json(
                    400,
                    {
                        "error": "PARAMETER_POLLUTION",
                        "message": "Duplicate query parameters are not permitted",
                    },
                )
                return
            sku = qs.get("sku", ["SKU-ITEM-001"])[0]
            if not VALID_SKU_RE.match(sku):
                self._send_json(
                    400,
                    {
                        "error": "INVALID_SKU",
                        "message": "SKU must be 1-64 alphanumeric, dash, or underscore characters",
                    },
                )
                return
            raw_qty = qs.get("quantity", ["1"])[0]
            if not STRICT_INT_RE.match(raw_qty):
                self._send_json(
                    400,
                    {
                        "error": "TYPE_MISMATCH",
                        "parameter": "quantity",
                        "message": "Invalid parameter type or numeric overflow",
                    },
                )
                return
            qty = int(raw_qty)
            if qty < INT32_MIN or qty > INT32_MAX:
                self._send_json(
                    400,
                    {
                        "error": "TYPE_MISMATCH",
                        "parameter": "quantity",
                        "message": "Invalid parameter type or numeric overflow",
                    },
                )
                return
            if qty < 0 or qty > MAX_RESET_QTY:
                self._send_json(
                    400,
                    {
                        "error": "INVALID_QUANTITY",
                        "message": f"Reset quantity must be between 0 and {MAX_RESET_QTY}",
                    },
                )
                return

            with inventory_lock:
                if sku not in inventory_db and len(inventory_db) >= MAX_TRACKED_SKUS:
                    self._send_json(429, {"error": "SKU_CAPACITY_EXCEEDED"})
                    return
                inventory_db[sku] = qty
                self._send_json(200, {"sku": sku, "available": qty, "status": "RESET_OK"})
            return

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

        self._send_json(404, {"error": "NOT_FOUND"})

    def do_PUT(self):
        self._handle_disallowed_method("PUT")

    def do_DELETE(self):
        self._handle_disallowed_method("DELETE")

    def do_PATCH(self):
        self._handle_disallowed_method("PATCH")

    def _handle_disallowed_method(self, method):
        path = urlparse(self.path).path
        if path in ("/api/inventory/reserve", "/api/inventory/reset"):
            self._send_json(
                405,
                {
                    "error": "METHOD_NOT_ALLOWED",
                    "method": method,
                    "message": "HTTP method is not supported for this endpoint",
                },
            )
        else:
            self._send_json(404, {"error": "NOT_FOUND"})

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    import sys

    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    print(f"Mock server running on port {port}...")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down mock server.")
        server.server_close()
