import requests
import json

def test_webhook_endpoint():
    """Test the webhook endpoint locally"""
    
    # Test webhook URL (assuming you're running locally on port 8000)
    webhook_url = "http://localhost:8000/loop-webhook/webhook"
    
    # Sample webhook payload for inbound message
    test_payload = {
        "type": "message_inbound",
        "message": {
            "from": "+18054901242",
            "text": "Yes",
            "passthrough": "",
            "message_id": "test-123"
        }
    }
    
    print("🧪 Testing webhook endpoint...")
    print(f"URL: {webhook_url}")
    print(f"Payload: {json.dumps(test_payload, indent=2)}")
    
    try:
        response = requests.post(
            webhook_url,
            json=test_payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\n📊 Response:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook test successful!")
        else:
            print("❌ Webhook test failed!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to webhook endpoint.")
        print("Make sure your FastAPI server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error testing webhook: {e}")

if __name__ == "__main__":
    test_webhook_endpoint() 