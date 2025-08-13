#!/usr/bin/env python3
"""
Script to send a flashcard via LoopMessage API and test the response
"""

import os
import requests
import json
import time
from dotenv import load_dotenv

load_dotenv()

def send_flashcard_via_api():
    """Send a flashcard via LoopMessage API"""
    
    print("📤 Sending flashcard via LoopMessage API...")
    
    # Check environment variables
    auth_key = os.getenv("LOOPMESSAGE_AUTH_KEY")
    secret_key = os.getenv("LOOPMESSAGE_SECRET_KEY")
    sender_name = os.getenv("LOOPMESSAGE_SENDER_NAME")
    
    if not all([auth_key, secret_key, sender_name]):
        print("❌ Missing required environment variables!")
        return None
    
    # API endpoint
    url = "https://server.loopmessage.com/api/v1/message/send/"
    
    # Headers
    headers = {
        "Authorization": auth_key,
        "Loop-Secret-Key": secret_key,
        "Content-Type": "application/json"
    }
    
    # Payload with passthrough data
    payload = {
        "recipient": "+18054901242",
        "text": "What is DNA?",
        "sender_name": sender_name,
        "passthrough": "flashcard_id:4"  # Use flashcard ID 4 which exists
    }
    
    print(f"📤 Sending flashcard with passthrough: {payload['passthrough']}")
    print(f"📱 Recipient: {payload['recipient']}")
    print(f"📝 Message: {payload['text']}")
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Flashcard sent successfully!")
                print(f"Message ID: {result.get('message_id')}")
                return result.get('message_id')
            else:
                print("❌ Failed to send flashcard")
                print(f"Error: {result.get('message')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return None

def test_response_after_flashcard():
    """Test responding to the flashcard after it's sent"""
    
    print("\n⏳ Waiting 10 seconds for flashcard to be delivered...")
    time.sleep(10)
    
    print("📥 Testing response to flashcard (without passthrough)...")
    
    webhook_url = "https://sms-spaced-repetition-production.up.railway.app/loop-webhook/webhook"
    
    # Test response without passthrough data (should use conversation state)
    response_payload = {
        "alert_type": "message_inbound",
        "recipient": "+18054901242",
        "text": "DNA is a molecule that carries genetic information",
        "message_id": "response-after-flashcard"
        # No passthrough data - should use conversation state
    }
    
    try:
        response = requests.post(
            webhook_url,
            json=response_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main function to test the complete flow"""
    
    print("🧪 Testing complete flashcard flow...")
    print("=" * 50)
    
    # Step 1: Send flashcard
    message_id = send_flashcard_via_api()
    
    if message_id:
        print(f"\n✅ Flashcard sent with ID: {message_id}")
        print("📱 Check your phone for the flashcard message")
        
        # Step 2: Test response
        test_response_after_flashcard()
        
        print("\n" + "=" * 50)
        print("🎯 Test complete! Check if you received feedback on your phone.")
    else:
        print("❌ Failed to send flashcard")

if __name__ == "__main__":
    main()
