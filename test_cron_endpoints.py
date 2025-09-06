#!/usr/bin/env python3
"""
Test the cron endpoints
"""

import requests
import json

def test_cron_endpoints():
    """Test the cron endpoints"""
    
    # Railway backend API URL
    base_url = "https://sms-spaced-repetition-production.up.railway.app"
    
    # Headers
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    try:
        print("🔍 Testing cron endpoints...")
        
        # Test the cron send-flashcards endpoint
        print("📤 Testing /cron/send-flashcards...")
        response = requests.post(f"{base_url}/cron/send-flashcards", headers=headers)
        
        print(f"📡 Response status: {response.status_code}")
        print(f"📡 Response text: {response.text}")
        
        # Test the cron cleanup endpoint
        print("\n🧹 Testing /cron/cleanup...")
        response = requests.post(f"{base_url}/cron/cleanup", headers=headers)
        
        print(f"📡 Response status: {response.status_code}")
        print(f"📡 Response text: {response.text}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_cron_endpoints()
