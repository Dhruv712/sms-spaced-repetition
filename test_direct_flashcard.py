#!/usr/bin/env python3
"""
Test that directly sends a flashcard and sets up conversation state
"""

import requests
import json
import time

def test_direct_flashcard():
    """Test sending flashcard directly and then responding"""
    
    print("🧪 Testing direct flashcard with conversation state...")
    
    webhook_url = "https://sms-spaced-repetition-production.up.railway.app/loop-webhook/webhook"
    
    # Step 1: Send a flashcard with passthrough data (this should work)
    print("\n📤 Step 1: Sending flashcard with passthrough data...")
    
    # First, let's send a webhook that simulates a flashcard being sent
    # This will set up the conversation state properly
    flashcard_payload = {
        "alert_type": "message_inbound",
        "recipient": "+18054901242",
        "text": "What is DNA?",
        "passthrough": "flashcard_id:4",
        "message_id": "flashcard-sent-test"
    }
    
    try:
        response = requests.post(
            webhook_url,
            json=flashcard_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Flashcard setup response: {response.text}")
        
        # Wait a moment
        print("⏳ Waiting 3 seconds...")
        time.sleep(3)
        
        # Step 2: Now test responding to the flashcard (without passthrough)
        print("\n📥 Step 2: Testing response to flashcard (without passthrough)...")
        
        response_payload = {
            "alert_type": "message_inbound",
            "recipient": "+18054901242",
            "text": "DNA is a molecule that carries genetic information",
            "message_id": "response-test-direct"
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
    test_direct_flashcard()
