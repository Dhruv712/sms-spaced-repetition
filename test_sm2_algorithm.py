#!/usr/bin/env python3
"""
Test the SuperMemo 2 algorithm implementation
"""

import requests
import json
import time

def test_sm2_algorithm():
    """Test the SM-2 algorithm with different scenarios"""
    
    print("🧪 Testing SuperMemo 2 algorithm...")
    
    # Step 1: Send a flashcard
    print("\n📤 Step 1: Sending flashcard...")
    
    endpoint_url = "https://sms-spaced-repetition-production.up.railway.app/loop-test/send-test-flashcard"
    
    try:
        response = requests.post(endpoint_url, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Flashcard sent: {result.get('concept')} (ID: {result.get('flashcard_id')})")
            
            # Step 2: Test correct response
            print("\n📥 Step 2: Testing correct response...")
            time.sleep(3)
            
            webhook_url = "https://sms-spaced-repetition-production.up.railway.app/loop-webhook/webhook"
            
            correct_payload = {
                "alert_type": "message_inbound",
                "recipient": "+18054901242",
                "text": "A molecule that carries genetic information",
                "message_id": "test-correct-response"
            }
            
            response = requests.post(
                webhook_url,
                json=correct_payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            print(f"Correct response result: {response.text}")
            
            # Step 3: Wait and test incorrect response
            print("\n⏳ Waiting 5 seconds...")
            time.sleep(5)
            
            print("📥 Step 3: Testing incorrect response...")
            
            incorrect_payload = {
                "alert_type": "message_inbound",
                "recipient": "+18054901242",
                "text": "Wrong answer",
                "message_id": "test-incorrect-response"
            }
            
            response = requests.post(
                webhook_url,
                json=incorrect_payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            print(f"Incorrect response result: {response.text}")
            
        else:
            print(f"❌ Failed to send flashcard: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_sm2_algorithm()
