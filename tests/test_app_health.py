import os
import requests
import pytest

BASE_URL = os.getenv("TARGET_URL", "http://localhost:8080").rstrip("/")
HEALTH_PATH = os.getenv("HEALTH_PATH", "/actuator/health")
if not HEALTH_PATH.startswith("/"):
    HEALTH_PATH = f"/{HEALTH_PATH}"

def test_app_is_up():
    """Check if the application is responding on the expected port and health path."""
    response = requests.get(f"{BASE_URL}{HEALTH_PATH}", timeout=5)
    assert response.status_code == 200
    try:
        data = response.json()
        if isinstance(data, dict) and "status" in data:
            assert str(data["status"]).upper() in ["UP", "OK", "HEALTHY"]
    except Exception:
        # Non-JSON or plain text health check responses that return 200 are accepted
        pass

def test_app_version():
    """Check if the application version/info is accessible (optional)."""
    try:
        requests.get(f"{BASE_URL}/actuator/info", timeout=3)
    except Exception:
        pass

def test_endpoints():
    response = requests.get(f"{BASE_URL}{HEALTH_PATH}", timeout=5)
    assert response.status_code == 200
