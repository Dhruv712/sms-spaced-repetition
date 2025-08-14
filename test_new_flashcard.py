#!/usr/bin/env python3
"""
Test script to simulate NEW flashcard creation flow
"""

import requests
import json
import time

# Railway backend URL
app_url = "https://sms-spaced-repetition-production.up.railway.app"

def simulate_new_flashcard_webhook():
    """Simulate sending a NEW flashcard creation webhook"""
    
    # Webhook payload for NEW command
    webhook_data = {
        "alert_type": "message_inbound",
        "delivery_type": "imessage", 
        "language": {"code": "en", "name": "English"},
        "message_id": "test-new-flashcard-123",
        "message_type": "text",
        "recipient": "+18054901242",  # Your phone number
        "sandbox": True,
        "sender_name": "sandbox.loopmessage.com@imsg.im",
        "text": "NEW Create a flashcard about photosynthesis",
        "webhook_id": "test-webhook-123"
    }
    
    print("🚀 Sending NEW flashcard webhook...")
    print(f"📝 Message: {webhook_data['text']}")
    
    try:
        response = requests.post(
            f"{app_url}/loop-webhook/webhook",
            json=webhook_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📡 Response status: {response.status_code}")
        print(f"📡 Response body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Webhook sent successfully!")
        else:
            print(f"❌ Webhook failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error sending webhook: {e}")

def simulate_confirmation_webhook():
    """Simulate confirming the flashcard creation"""
    
    # Wait a bit for the first webhook to process
    print("⏳ Waiting 3 seconds before sending confirmation...")
    time.sleep(3)
    
    webhook_data = {
        "alert_type": "message_inbound",
        "delivery_type": "imessage",
        "language": {"code": "en", "name": "English"},
        "message_id": "test-confirm-flashcard-456",
        "message_type": "text", 
        "recipient": "+18054901242",
        "sandbox": True,
        "sender_name": "sandbox.loopmessage.com@imsg.im",
        "text": "SAVE",
        "webhook_id": "test-webhook-456"
    }
    
    print("🚀 Sending confirmation webhook...")
    print(f"📝 Message: {webhook_data['text']}")
    
    try:
        response = requests.post(
            f"{app_url}/loop-webhook/webhook",
            json=webhook_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📡 Response status: {response.status_code}")
        print(f"📡 Response body: {response.text}")
        
        if response.status_code == 200:
            print("✅ Confirmation webhook sent successfully!")
        else:
            print(f"❌ Confirmation webhook failed with status {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error sending confirmation webhook: {e}")

if __name__ == "__main__":
    print("🧪 Testing NEW flashcard creation flow...")
    print("=" * 50)
    
    # Step 1: Send NEW command
    simulate_new_flashcard_webhook()
    
    print("\n" + "=" * 50)
    
    # Step 2: Send confirmation
    simulate_confirmation_webhook()
    
    print("\n" + "=" * 50)
    print("🏁 Test complete! Check the Railway logs for detailed output.")
