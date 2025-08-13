#!/usr/bin/env python3
"""
Test with conversation state simulation
"""

import requests
import json
import time

def test_with_conversation_state():
    """Test the flow with conversation state"""
    
    print("🧪 Testing with conversation state simulation...")
    
    webhook_url = "https://sms-spaced-repetition-production.up.railway.app/loop-webhook/webhook"
    
    # Step 1: Simulate starting a session (this should set conversation state)
    print("\n📤 Step 1: Starting session to set conversation state...")
    start_payload = {
        "alert_type": "message_inbound",
        "recipient": "+18054901242",
        "text": "Yes",
        "message_id": "start-session-real"
    }
    
    try:
        response = requests.post(
            webhook_url,
            json=start_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Start session response: {response.text}")
        
        # Wait for the flashcard to be sent
        print("⏳ Waiting 10 seconds for flashcard to be sent and conversation state to be set...")
        time.sleep(10)
        
        # Step 2: Now test responding to the flashcard (without passthrough)
        print("\n📥 Step 2: Testing response to flashcard (without passthrough)...")
        
        response_payload = {
            "alert_type": "message_inbound",
            "recipient": "+18054901242",
            "text": "DNA is a molecule that carries genetic information",
            "message_id": "response-real-test"
            # No passthrough data - should use conversation state
        }
        
        response = requests.post(
            webhook_url,
            json=response_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Response to flashcard: {response.text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_with_conversation_state()
