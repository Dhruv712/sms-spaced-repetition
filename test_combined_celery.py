#!/usr/bin/env python3
"""
Test the combined Celery service
"""

import requests
import json

def test_combined_celery():
    """Test the combined Celery service"""
    
    # Railway backend API URL
    base_url = "https://sms-spaced-repetition-production.up.railway.app"
    
    # Headers
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    try:
        print("🚀 Testing combined Celery service...")
        
        # Test the direct scheduling endpoint
        print("📤 Testing direct scheduling...")
        response = requests.post(f"{base_url}/admin/trigger-scheduled-flashcards-direct", headers=headers)
        
        print(f"📡 Response status: {response.status_code}")
        print(f"📡 Response text: {response.text}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ Direct scheduling result: {result}")
            except json.JSONDecodeError:
                print(f"⚠️ Response is not JSON: {response.text}")
        else:
            print(f"❌ Direct scheduling failed: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_combined_celery()
