#!/usr/bin/env python3
"""
Debug script to monitor webhook events
"""

import requests
import json

def test_webhook_events():
    """Test different webhook event types"""
    
    print("🧪 Testing different webhook event types...")
    
    webhook_url = "https://sms-spaced-repetition-production.up.railway.app/loop-webhook/webhook"
    
    # Test 1: message_sent webhook (this should NOT trigger response processing)
    print("\n📥 Test 1: message_sent webhook")
    message_sent_payload = {
        "alert_type": "message_sent",
        "recipient": "+18054901242",
        "text": "What is DNA?",
        "message_id": "test-message-sent",
        "success": True,
        "passthrough": "flashcard_id:4"
    }
    
    try:
        response = requests.post(
            webhook_url,
            json=message_sent_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*50)
    
    # Test 2: message_inbound with empty text (this might be the issue)
    print("📥 Test 2: message_inbound with empty text")
    empty_inbound_payload = {
        "alert_type": "message_inbound",
        "recipient": "+18054901242",
        "text": "",
        "message_id": "test-empty-inbound",
        "passthrough": "flashcard_id:4"
    }
    
    try:
        response = requests.post(
            webhook_url,
            json=empty_inbound_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_webhook_events()
