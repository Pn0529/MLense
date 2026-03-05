import requests

BASE_URL = "http://localhost:7860"

# Note: You'll need a valid token to test this. 
# Since I don't have one easily available here, I'll just check if the endpoint exists and returns 401.

def test_endpoints():
    endpoints = ["/pyqs/categories", "/health", "/history", "/quiz_history"]
    for ep in endpoints:
        try:
            r = requests.get(f"{BASE_URL}{ep}")
            print(f"GET {ep}: {r.status_code}")
        except Exception as e:
            print(f"GET {ep}: Failed - {e}")

if __name__ == "__main__":
    test_endpoints()
