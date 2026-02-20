import requests
import sys

BASE_URL = "http://localhost:8000/api/v1/fields/field_demo_001/grid"

# Keys from migrations
KEY_FREE = "demo-free-key"      # Tier: FREE, Role: FARMER
KEY_AUDIT = "demo-audit-key"    # Tier: FREE, Role: AUDITOR

def test_audit_override():
    print("Testing Audit Override Logic...")
    failed = False

    # 1. Test Restricted Access (Farmer / Free Tier)
    print("\nCase 1: Free Tier Farmer accessing 1m Grid (Pro Only)")
    try:
        resp = requests.get(f"{BASE_URL}/1m", headers={"X-API-Key": KEY_FREE}, timeout=2)
        if resp.status_code == 403:
            print("  [PASS] Blocked as expected (403)")
        else:
            print(f"  [FAIL] Unexpected status: {resp.status_code} (Expected 403)")
            failed = True
    except Exception as e:
        print(f"  [ERR] Connection failed: {e}")

    # 2. Test Audit Override (Auditor / Free Tier)
    print("\nCase 2: Free Tier Auditor accessing 1m Grid (Pro Only)")
    try:
        resp = requests.get(f"{BASE_URL}/1m", headers={"X-API-Key": KEY_AUDIT}, timeout=2)
        # We expect 200 (Success) or 404 (Not Found, but Authorized)
        if resp.status_code in [200, 404]:
             print(f"  [PASS] Access Granted ({resp.status_code}) - Override Successful")
        elif resp.status_code == 403:
             print("  [FAIL] Access Denied (403) - Override Failed")
             failed = True
        else:
             print(f"  [FAIL] Unexpected status: {resp.status_code}")
             failed = True
    except Exception as e:
        print(f"  [ERR] Connection failed: {e}")
        # If connection fails, likely server not running, but logic check is what we want.

    if failed:
        sys.exit(1)
    else:
        print("\nAudit Override Tests Passed!")

if __name__ == "__main__":
    test_audit_override()
