#!/usr/bin/env python3
"""
Debug script to check conversation state in Railway database
"""

import requests
import json

# Railway backend URL
app_url = "https://sms-spaced-repetition-production.up.railway.app"

def check_conversation_state():
    """Check the conversation state for user ID 1"""
    
    print("🔍 Checking conversation state for user ID 1...")
    
    try:
        # Use the admin endpoint to get user stats (which might show conversation state)
        response = requests.get(f"{app_url}/admin/user-stats/1")
        
        print(f"📡 Response status: {response.status_code}")
        print(f"📡 Response body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ User stats retrieved successfully!")
            print(f"📊 User data: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Failed to get user stats: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking conversation state: {e}")

def check_flashcards():
    """Check if any flashcards exist for user ID 1"""
    
    print("\n🔍 Checking flashcards for user ID 1...")
    
    try:
        # Try to get flashcards via the flashcards endpoint
        response = requests.get(f"{app_url}/flashcards/")
        
        print(f"📡 Response status: {response.status_code}")
        print(f"📡 Response body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Flashcards retrieved successfully!")
            print(f"📊 Flashcards: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Failed to get flashcards: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error checking flashcards: {e}")

if __name__ == "__main__":
    print("🧪 Debugging conversation state and flashcards...")
    print("=" * 50)
    
    check_conversation_state()
    check_flashcards()
    
    print("\n" + "=" * 50)
    print("�� Debug complete!")
