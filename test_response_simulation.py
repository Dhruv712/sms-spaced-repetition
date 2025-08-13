#!/usr/bin/env python3
"""
Test to simulate the response webhook
"""

import requests
import json

def test_response_simulation():
    """Simulate the response webhook that failed"""
    
    print("🧪 Simulating response webhook...")
    
    webhook_url = "https://sms-spaced-repetition-production.up.railway.app/loop-webhook/webhook"
    
    # Simulate your response to flashcard ID 4
    response_payload = {
        "alert_type": "message_inbound",
        "recipient": "+18054901242",
        "text": "DNA is a molecule that carries genetic information",
        "message_id": "test-response-simulation"
        # No passthrough data - should use conversation state
    }
    
    print(f"📥 Sending webhook payload:")
    print(f"   - alert_type: {response_payload['alert_type']}")
    print(f"   - recipient: {response_payload['recipient']}")
    print(f"   - text: {response_payload['text']}")
    print(f"   - message_id: {response_payload['message_id']}")
    
    try:
        response = requests.post(
            webhook_url,
            json=response_payload,
            headers={"Content-Type": "application/json"},
            timeout=60  # Increased timeout
        )
        
        print(f"\n📊 Response Status: {response.status_code}")
        print(f"📄 Response Text: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook processed successfully!")
        else:
            print("❌ Webhook failed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_response_simulation()
