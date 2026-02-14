import requests
import time
import json

BASE_URL = "http://127.0.0.1:8000"

def wait_for_api():
    print("Waiting for API to start...")
    for _ in range(10):
        try:
            resp = requests.get(f"{BASE_URL}/")
            if resp.status_code == 200:
                print("API is ready!")
                return True
        except:
            time.sleep(2)
    return False

def test_onboard():
    print("\nTesting Onboarding (Protected)...")
    payload = {
        "name": "API Test Vendor",
        "location": "Cloud City",
        "category": "Electronics",
        "contact": "test@api.com",
        "structured_data": {"product": "Quantum Chip", "price": "500"}
    }
    
    # 1. Test without Key (Should Fail)
    print("  -> Attempting without Admin Key...")
    resp_fail = requests.post(f"{BASE_URL}/v1/vendor/onboard", json=payload)
    if resp_fail.status_code == 403:
        print(f"  [OK] Blocked correctly (403 Forbidden)")
    else:
        print(f"  [FAIL] Security Bypass! Status: {resp_fail.status_code}")

    # 2. Test with Key (Should Succeed)
    print("  -> Attempting with Admin Key...")
    headers = {"X-Admin-Key": "secret-admin-key-123"} # Default key
    resp = requests.post(f"{BASE_URL}/v1/vendor/onboard", json=payload, headers=headers)
    print(f"  Status: {resp.status_code}")
    print(f"  Response: {resp.json()}")

def test_search():
    print("\nTesting Search...")
    payload = {"query": "Quantum Chip"}
    resp = requests.post(f"{BASE_URL}/v1/search", json=payload)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"AI Summary: {data['ai_summary'][:100]}...")
        print(f"Found {len(data['vendors'])} vendors.")
    else:
        print(f"Error: {resp.text}")

def test_beckn():
    print("\nTesting ONDC Beckn /search...")
    import datetime
    
    # Standard ONDC Request Body
    payload = {
        "context": {
            "domain": "ONDC:RET10",
            "country": "IND",
            "city": "std:080",
            "action": "search",
            "core_version": "1.2.0",
            "bap_id": "test-buyer-app",
            "bap_uri": "http://localhost:9000",
            "transaction_id": "tx-123",
            "message_id": "msg-456",
            "timestamp": datetime.datetime.now().isoformat()
        },
        "message": {
            "intent": {
                "item": {"descriptor": {"name": "Bamboo"}}
            }
        }
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/v1/beckn/search", json=payload)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.json()}")
        if resp.status_code == 200 and "ack" in resp.json().get("message", {}):
            print("[OK] Received ACK (Async request accepted)")
        else:
            print("[FAIL] Start Failed")
    except Exception as e:
        print(f"Error: {e}")


def test_whatsapp():
    print("\nTesting WhatsApp Logic...")
    
    # 1. Test Onboarding
    print("  -> Testing Onboarding Intent...")
    msg_onboard = "I want to register my shop called 'Super Electronics' in Indiranagar. We sell gadgets."
    resp = requests.post(f"{BASE_URL}/v1/whatsapp/test", params={"message": msg_onboard, "sender": "whatsapp:+919988776655"})
    print(f"  Response: {resp.json().get('reply')[:100]}...")

    # 2. Test Search
    print("  -> Testing Search Intent...")
    msg_search = "Find me an electronics shop in Indiranagar"
    resp = requests.post(f"{BASE_URL}/v1/whatsapp/test", params={"message": msg_search, "sender": "whatsapp:+919988776655"})
    print(f"  Response: {resp.json().get('reply')[:100]}...")
    
    # 3. Test Unknown/Ambiguous
    print("  -> Testing Ambiguous Intent...")
    msg_unknown = "Hello there"
    resp = requests.post(f"{BASE_URL}/v1/whatsapp/test", params={"message": msg_unknown, "sender": "whatsapp:+919988776655"})
    print(f"  Response: {resp.json().get('reply')[:100]}...")

if __name__ == "__main__":
    if wait_for_api():
        test_onboard()
        test_search()
        test_beckn()
        test_whatsapp()
    else:
        print("API failed to start.")
