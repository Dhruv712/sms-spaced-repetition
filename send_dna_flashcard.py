#!/usr/bin/env python3
"""
Send the DNA flashcard for testing
"""

import requests
import json

def send_dna_flashcard():
    """Send the DNA flashcard"""
    
    print("🧪 Sending DNA flashcard...")
    
    # Call the test endpoint to send flashcard ID 4 (DNA)
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
            print("\n📱 Check your phone for the flashcard message")
            print("🎯 Now respond to the flashcard via text!")
        else:
            print(f"❌ Failed to send flashcard: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    send_dna_flashcard()
