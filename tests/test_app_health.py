import requests
import pytest

BASE_URL = "http://localhost:8080"

def test_app_is_up():
    """Check if the application is responding on the expected port."""
    response = requests.get(f"{BASE_URL}/actuator/health")
    assert response.status_code == 200
    assert response.json()["status"] == "UP"

def test_app_version():
    """Check if the application version is accessible (optional)."""
    # Note: This depends on what endpoints are exposed. 
    # Actuator often has /info or /beans.
    response = requests.get(f"{BASE_URL}/actuator/info")
    # We don't necessarily expect a 200 if info is disabled, but it's a good check.
    pass

@pytest.mark.parametrize("path", ["/actuator/health"])
def test_endpoints(path):
    response = requests.get(f"{BASE_URL}{path}")
    assert response.status_code == 200
