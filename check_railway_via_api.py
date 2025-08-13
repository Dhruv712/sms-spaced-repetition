#!/usr/bin/env python3
"""
Check Railway users via API endpoints
"""

import requests
import json

def check_railway_via_api():
    """Check Railway users via API endpoints"""
    
    # Railway backend API URL
    base_url = "https://sms-spaced-repetition-production.up.railway.app"
    
    # Headers to ensure we get JSON responses
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    try:
        # Get user stats for user ID 1 (your account)
        print("🔍 Checking user stats via Railway API...")
        response = requests.get(f"{base_url}/admin/user-stats/1", headers=headers)
        
        print(f"📡 Response status: {response.status_code}")
        print(f"📡 Response headers: {dict(response.headers)}")
        print(f"📡 Response text: {response.text[:200]}...")  # Truncate for readability
        
        if response.status_code == 200:
            try:
                stats = response.json()
                print(f"✅ User stats retrieved:")
                print(f"   - Total flashcards: {stats.get('total_flashcards', 'N/A')}")
                print(f"   - Due flashcards: {stats.get('due_flashcards', 'N/A')}")
                print(f"   - Recently reviewed: {stats.get('recently_reviewed', 'N/A')}")
            except json.JSONDecodeError:
                print(f"⚠️ Response is not JSON: {response.text[:200]}...")
        else:
            print(f"❌ Failed to get user stats: {response.status_code}")
        
        # Try to get user stats for user ID 2 (in case there are multiple users)
        print("\n🔍 Checking user stats for user ID 2...")
        response = requests.get(f"{base_url}/admin/user-stats/2", headers=headers)
        
        print(f"📡 Response status: {response.status_code}")
        print(f"📡 Response text: {response.text[:200]}...")
        
        if response.status_code == 200:
            try:
                stats = response.json()
                print(f"✅ User 2 stats retrieved:")
                print(f"   - Total flashcards: {stats.get('total_flashcards', 'N/A')}")
                print(f"   - Due flashcards: {stats.get('due_flashcards', 'N/A')}")
                print(f"   - Recently reviewed: {stats.get('recently_reviewed', 'N/A')}")
            except json.JSONDecodeError:
                print(f"⚠️ Response is not JSON: {response.text[:200]}...")
        else:
            print(f"❌ No user 2 found: {response.status_code}")
        
        # Try to send a due flashcard to user 1
        print("\n🚀 Testing sending due flashcards to user 1...")
        response = requests.post(f"{base_url}/admin/send-to-user/1", headers=headers)
        
        print(f"📡 Response status: {response.status_code}")
        print(f"📡 Response text: {response.text[:200]}...")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ Send result: {result}")
            except json.JSONDecodeError:
                print(f"⚠️ Response is not JSON: {response.text[:200]}...")
        else:
            print(f"❌ Failed to send: {response.status_code}")
        
        # Try the loop-test endpoint
        print("\n🧪 Testing loop-test endpoint...")
        response = requests.post(f"{base_url}/loop-test/send-test-flashcard", headers=headers)
        
        print(f"📡 Response status: {response.status_code}")
        print(f"📡 Response text: {response.text[:200]}...")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ Loop test result: {result}")
            except json.JSONDecodeError:
                print(f"⚠️ Response is not JSON: {response.text[:200]}...")
        else:
            print(f"❌ Failed loop test: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_railway_via_api()
