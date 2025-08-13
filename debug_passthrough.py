#!/usr/bin/env python3
"""
Debug script to test passthrough functionality
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

load_dotenv()

def test_send_flashcard_with_passthrough():
    """Test sending a flashcard with passthrough data"""
    
    print("🧪 Testing flashcard sending with passthrough...")
    
    # Check environment variables
    auth_key = os.getenv("LOOPMESSAGE_AUTH_KEY")
    secret_key = os.getenv("LOOPMESSAGE_SECRET_KEY")
    sender_name = os.getenv("LOOPMESSAGE_SENDER_NAME")
    
    if not all([auth_key, secret_key, sender_name]):
        print("❌ Missing required environment variables!")
        return
    
    # Test payload
    url = "https://server.loopmessage.com/api/v1/message/send/"
    headers = {
        "Authorization": auth_key,
        "Loop-Secret-Key": secret_key,
        "Content-Type": "application/json"
    }
    
    payload = {
        "recipient": "+18054901242",
        "text": "What is DNA?",
        "sender_name": sender_name,
        "passthrough": "flashcard_id:123"
    }
    
    print(f"📤 Sending test message with passthrough...")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Message sent successfully!")
                print(f"Message ID: {result.get('message_id')}")
                return result.get('message_id')
            else:
                print("❌ Message failed to send")
                print(f"Error: {result.get('message')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

def test_webhook_simulation():
    """Simulate a webhook with passthrough data"""
    
    print("\n🧪 Testing webhook simulation...")
    
    # Simulate the webhook payload that should come back
    webhook_payload = {
        "alert_type": "message_inbound",
        "recipient": "+18054901242",
        "text": "DNA is a molecule that carries genetic information",
        "passthrough": "flashcard_id:123",
        "message_id": "test-message-id"
    }
    
    print(f"📥 Simulating webhook payload:")
    print(f"Payload: {json.dumps(webhook_payload, indent=2)}")
    
    # Send to your webhook endpoint
    webhook_url = "https://sms-spaced-repetition-production.up.railway.app/loop-webhook/webhook"
    
    try:
        response = requests.post(
            webhook_url,
            json=webhook_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Webhook Response Status: {response.status_code}")
        print(f"Webhook Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Webhook test error: {e}")

def main():
    """Main test function"""
    
    print("🔧 Starting passthrough debug tests...")
    print("=" * 50)
    
    # Test 1: Send message with passthrough
    message_id = test_send_flashcard_with_passthrough()
    
    if message_id:
        print(f"\n✅ Message sent with ID: {message_id}")
        print("📱 Check your phone for the message with passthrough data")
        
        # Wait a bit for the message to be delivered
        input("\n⏳ Press Enter after you receive the message to continue...")
        
        # Test 2: Simulate webhook response
        test_webhook_simulation()
    else:
        print("❌ Failed to send test message")

if __name__ == "__main__":
    main()
