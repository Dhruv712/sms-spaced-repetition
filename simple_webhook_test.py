#!/usr/bin/env python3
"""
Simple webhook test without importing the full app
"""

import requests
import json

def test_webhook_with_real_data():
    """Test webhook with realistic data"""
    
    print("🧪 Testing webhook with realistic data...")
    
    # Test 1: Simulate a response to a flashcard (with passthrough)
    print("\n📥 Test 1: Webhook with passthrough data")
    webhook_payload_1 = {
        "alert_type": "message_inbound",
        "recipient": "+18054901242",
        "text": "DNA is a molecule that carries genetic information",
        "passthrough": "flashcard_id:4",  # Use a real flashcard ID
        "message_id": "test-message-id-1"
    }
    
    webhook_url = "https://sms-spaced-repetition-production.up.railway.app/loop-webhook/webhook"
    
    try:
        response = requests.post(
            webhook_url,
            json=webhook_payload_1,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*50)
    
    # Test 2: Simulate a response without passthrough (should use conversation state)
    print("📥 Test 2: Webhook without passthrough data (should use conversation state)")
    webhook_payload_2 = {
        "alert_type": "message_inbound",
        "recipient": "+18054901242",
        "text": "DNA is a molecule that carries genetic information",
        "message_id": "test-message-id-2"
        # No passthrough data
    }
    
    try:
        response = requests.post(
            webhook_url,
            json=webhook_payload_2,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*50)
    
    # Test 3: Simulate "Yes" response to start session
    print("📥 Test 3: 'Yes' response to start session")
    webhook_payload_3 = {
        "alert_type": "message_inbound",
        "recipient": "+18054901242",
        "text": "Yes",
        "message_id": "test-message-id-3"
    }
    
    try:
        response = requests.post(
            webhook_url,
            json=webhook_payload_3,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_webhook_with_real_data()
