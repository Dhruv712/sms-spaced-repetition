import requests
import json

def test_railway_webhook():
    """Test the webhook endpoint on Railway"""
    
    railway_url = "https://sms-spaced-repetition-production.up.railway.app/loop-webhook/webhook"
    
    # Test payload
    test_payload = {
        "type": "message_inbound",
        "message": {
            "from": "+18054901242",
            "text": "Testing Railway webhook",
            "passthrough": "",
            "message_id": "railway-test-123"
        }
    }
    
    print("🧪 Testing Railway webhook endpoint...")
    print(f"URL: {railway_url}")
    
    try:
        response = requests.post(
            railway_url,
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📊 Response:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Railway webhook is working!")
            return True
        else:
            print("❌ Railway webhook test failed!")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Railway webhook.")
        print("The app might still be deploying...")
        return False
    except requests.exceptions.Timeout:
        print("❌ Request timed out.")
        return False
    except Exception as e:
        print(f"❌ Error testing Railway webhook: {e}")
        return False

if __name__ == "__main__":
    test_railway_webhook() 