import requests
import sys

BASE_URL = "http://localhost:8000/api/v1/fields/field_demo_001/grid"

KEYS = {
    "FREE": "demo-free-key",
    "BASIC": "demo-basic-key",
    "PRO": "demo-pro-key"
}

ENDPOINTS = {
    "50m": "FREE",
    "20m": "BASIC",
    "1m": "PRO"
}

def test_access():
    print("Testing Tier Access Control...")
    failed = False

    for endpoint, min_tier in ENDPOINTS.items():
        url = f"{BASE_URL}/{endpoint}"
        print(f"\nTarget: {endpoint} (Requires {min_tier})")
        
        for user_tier, key in KEYS.items():
            headers = {"X-API-Key": key}
            try:
                # We expect 404 (Not Found) if auth passes but data missing, 
                # or 403 (Forbidden) if auth fails.
                # ConnectionError if server down.
                response = requests.get(url, headers=headers, timeout=2)
                
                status = response.status_code
                
                # Logic to determine if access should be granted
                tiers = ["FREE", "BASIC", "PRO"]
                user_level = tiers.index(user_tier)
                req_level = tiers.index(min_tier)
                should_allow = user_level >= req_level
                
                if should_allow:
                    if status in [200, 404]:
                        print(f"  [PASS] {user_tier}: Allowed ({status})")
                    else:
                        print(f"  [FAIL] {user_tier}: Blocked ({status}) - Expected Allow")
                        failed = True
                else:
                    if status == 403:
                         print(f"  [PASS] {user_tier}: Blocked (403)")
                    else:
                         print(f"  [FAIL] {user_tier}: Allowed ({status}) - Expected 403")
                         failed = True
            except Exception as e:
                print(f"  [ERR] {user_tier}: {e}")
                
    if failed:
        sys.exit(1)
    else:
        print("\nAll Access Control Tests Passed!")

if __name__ == "__main__":
    test_access()
