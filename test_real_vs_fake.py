import requests
import json

def test_fake_webhook():
    """Test with fake webhook data (what we've been doing)"""
    print("🧪 Testing with FAKE webhook data...")
    
    fake_payload = {
        "type": "message_inbound",
        "message": {
            "from": "+18054901242",
            "text": "This is a FAKE test message",
            "passthrough": "",
            "message_id": "fake-test-123"
        }
    }
    
    response = requests.post(
        "http://localhost:8000/loop-webhook/webhook",
        json=fake_payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"✅ Fake webhook response: {response.status_code}")
    return response.json()

def test_real_webhook_format():
    """Show what a REAL LoopMessage webhook would look like"""
    print("\n📋 REAL LoopMessage webhook format would be:")
    
    real_payload_example = {
        "type": "message_inbound",
        "message": {
            "from": "+18054901242",
            "text": "Your actual message here",
            "passthrough": "flashcard_id:1",  # This would be set when we send flashcards
            "message_id": "real-loopmessage-id-123",
            "timestamp": "2024-01-15T10:30:00Z"
        }
    }
    
    print(json.dumps(real_payload_example, indent=2))
    print("\n💡 This is what LoopMessage will send when you:")
    print("   1. Reply to a flashcard")
    print("   2. Send 'Yes' to start a session")
    print("   3. Send any other message")

if __name__ == "__main__":
    test_fake_webhook()
    test_real_webhook_format() 