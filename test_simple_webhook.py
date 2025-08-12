import requests
import json

def test_simple_webhook():
    """Test webhook with minimal processing"""
    
    railway_url = "https://sms-spaced-repetition-production.up.railway.app/loop-webhook/webhook"
    
    # Test with flashcard ID 4 (the one we know exists)
    test_payload = {
        "type": "message_inbound",
        "message": {
            "from": "+18054901242",
            "text": "DNA is a molecule that carries genetic information",
            "passthrough": "flashcard_id:4",
            "message_id": "simple-test-123"
        }
    }
    
    print("🧪 Testing simple webhook with flashcard ID 4...")
    print(f"Payload: {json.dumps(test_payload, indent=2)}")
    
    try:
        response = requests.post(
            railway_url,
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"\n📊 Response:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook processed successfully!")
        else:
            print("❌ Webhook failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_simple_webhook() 