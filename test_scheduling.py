#!/usr/bin/env python3
"""
Test the automated scheduling system
"""

import requests
import json

def test_scheduling():
    """Test the automated scheduling system"""
    
    # Railway backend API URL
    base_url = "https://sms-spaced-repetition-production.up.railway.app"
    
    # Headers
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    try:
        print("🚀 Testing automated scheduling system...")
        
        # Trigger the scheduled flashcard task
        print("📤 Triggering scheduled flashcard task...")
        response = requests.post(f"{base_url}/admin/trigger-scheduled-flashcards", headers=headers)
        
        print(f"📡 Response status: {response.status_code}")
        print(f"📡 Response text: {response.text}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ Scheduling result: {result}")
            except json.JSONDecodeError:
                print(f"⚠️ Response is not JSON: {response.text}")
        else:
            print(f"❌ Scheduling failed: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_scheduling()
