#!/usr/bin/env python3
"""
Simple test to debug conversation state issues
"""

import requests
import json
import time

# Railway backend URL
app_url = "https://sms-spaced-repetition-production.up.railway.app"

def test_conversation_state():
    """Test the conversation state flow"""
    
    # Step 1: Send NEW command
    print("🚀 Step 1: Sending NEW command...")
    webhook_data = {
        "alert_type": "message_inbound",
        "delivery_type": "imessage",
        "language": {"code": "en", "name": "English"},
        "message_id": "test-conv-1",
        "message_type": "text",
        "recipient": "+18054901242",
        "sandbox": True,
        "sender_name": "sandbox.loopmessage.com@imsg.im",
        "text": "NEW Create a flashcard about the water cycle",
        "webhook_id": "test-webhook-1"
    }
    
    response = requests.post(
        f"{app_url}/loop-webhook/webhook",
        json=webhook_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"📡 Step 1 Response: {response.status_code} - {response.text}")
    
    # Step 2: Wait and send SAVE
    print("\n⏳ Waiting 5 seconds...")
    time.sleep(5)
    
    print("🚀 Step 2: Sending SAVE command...")
    webhook_data = {
        "alert_type": "message_inbound",
        "delivery_type": "imessage",
        "language": {"code": "en", "name": "English"},
        "message_id": "test-conv-2",
        "message_type": "text",
        "recipient": "+18054901242",
        "sandbox": True,
        "sender_name": "sandbox.loopmessage.com@imsg.im",
        "text": "SAVE",
        "webhook_id": "test-webhook-2"
    }
    
    response = requests.post(
        f"{app_url}/loop-webhook/webhook",
        json=webhook_data,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"📡 Step 2 Response: {response.status_code} - {response.text}")

if __name__ == "__main__":
    print("🧪 Testing conversation state flow...")
    print("=" * 50)
    test_conversation_state()
    print("=" * 50)
    print("🏁 Test complete!")
