#!/usr/bin/env python3
"""
Delete user via admin endpoint
"""

import requests
import json

def delete_user_remote():
    """Delete user with ID 2"""
    
    # Railway backend API URL
    base_url = "https://sms-spaced-repetition-production.up.railway.app"
    
    try:
        print("🗑️ Deleting user ID 2 (waterfire712@gmail.com)...")
        
        # Call the public delete endpoint
        response = requests.delete(f"{base_url}/admin/delete-user-2-public")
        
        print(f"📡 Response status: {response.status_code}")
        print(f"📡 Response text: {response.text}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ User deleted successfully: {result}")
            except json.JSONDecodeError:
                print(f"⚠️ Response is not JSON: {response.text}")
        else:
            print(f"❌ Failed to delete user: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    delete_user_remote()
