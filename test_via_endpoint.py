#!/usr/bin/env python3
"""
Test using the test endpoint to send a flashcard
"""

import requests
import json
import time

def test_via_endpoint():
    """Test sending flashcard via test endpoint"""
    
    print("🧪 Testing via test endpoint...")
    
    # Step 1: Call the test endpoint to send a flashcard
    print("\n📤 Step 1: Calling test endpoint to send flashcard...")
    
    endpoint_url = "https://sms-spaced-repetition-production.up.railway.app/loop-test/send-test-flashcard"
    
    try:
        response = requests.post(endpoint_url, timeout=30)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Flashcard sent successfully!")
            print(f"Flashcard ID: {result.get('flashcard_id')}")
            print(f"Concept: {result.get('concept')}")
            
            print("\n✅ Flashcard sent successfully!")
            print("📱 Check your phone for the flashcard message")
            print("\n🎯 Now respond to the flashcard via text!")
            print("The conversation state is set up, so your response should be processed correctly.")
            
        else:
            print(f"❌ Failed to send flashcard: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_via_endpoint()
