#!/usr/bin/env python3
"""
Test the complete flow: send flashcard, then test response
"""

import requests
import json
import time

def test_complete_flow():
    """Test the complete flashcard flow"""
    
    print("🧪 Testing complete flashcard flow...")
    
    # Step 1: Send a flashcard to trigger conversation state
    print("\n📤 Step 1: Sending flashcard to set conversation state...")
    
    # First, trigger a "Yes" response to start a session
    webhook_url = "https://sms-spaced-repetition-production.up.railway.app/loop-webhook/webhook"
    
    start_payload = {
        "alert_type": "message_inbound",
        "recipient": "+18054901242",
        "text": "Yes",
        "message_id": "start-session-test"
    }
    
    try:
        response = requests.post(
            webhook_url,
            json=start_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Start session response: {response.text}")
        
        # Wait a moment for the flashcard to be sent
        print("⏳ Waiting 5 seconds for flashcard to be sent...")
        time.sleep(5)
        
        # Step 2: Now test responding to the flashcard (without passthrough)
        print("\n📥 Step 2: Testing response to flashcard (without passthrough)...")
        
        response_payload = {
            "alert_type": "message_inbound",
            "recipient": "+18054901242",
            "text": "DNA is a molecule that carries genetic information",
            "message_id": "response-test"
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
    test_complete_flow()
