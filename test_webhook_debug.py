import requests
import json

def test_webhook_debug():
    """Test webhook with different scenarios to debug the issue"""
    
    railway_url = "https://sms-spaced-repetition-production.up.railway.app/loop-webhook/webhook"
    
    # Test 1: Basic webhook without passthrough
    print("🧪 Test 1: Basic webhook without passthrough")
    test_payload_1 = {
        "type": "message_inbound",
        "message": {
            "from": "+18054901242",
            "text": "Yes",
            "passthrough": "",
            "message_id": "debug-test-1"
        }
    }
    
    try:
        response = requests.post(
            railway_url,
            json=test_payload_1,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"📊 Response 1: {response.status_code}")
        print(f"📄 Response 1: {response.text}")
        
    except Exception as e:
        print(f"❌ Error 1: {e}")
    
    print("\n" + "="*50)
    
    # Test 2: Webhook with flashcard_id passthrough
    print("🧪 Test 2: Webhook with flashcard_id passthrough")
    test_payload_2 = {
        "type": "message_inbound",
        "message": {
            "from": "+18054901242",
            "text": "DNA is a molecule that carries genetic information",
            "passthrough": "flashcard_id:4",
            "message_id": "debug-test-2"
        }
    }
    
    try:
        response = requests.post(
            railway_url,
            json=test_payload_2,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"📊 Response 2: {response.status_code}")
        print(f"📄 Response 2: {response.text}")
        
    except Exception as e:
        print(f"❌ Error 2: {e}")

if __name__ == "__main__":
    test_webhook_debug() 