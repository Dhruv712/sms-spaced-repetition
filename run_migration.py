#!/usr/bin/env python3
"""
Run the migration endpoint to add SM-2 columns
"""

import requests
import json

def run_migration():
    """Run the migration endpoint"""
    
    # Railway backend API URL
    base_url = "https://sms-spaced-repetition-production.up.railway.app"
    
    # Headers
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    try:
        print("🔧 Running SM-2 columns migration...")
        response = requests.post(f"{base_url}/admin/migrate-sm2-columns-public", headers=headers)
        
        print(f"📡 Response status: {response.status_code}")
        print(f"📡 Response text: {response.text}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ Migration result: {result}")
            except json.JSONDecodeError:
                print(f"⚠️ Response is not JSON: {response.text}")
        else:
            print(f"❌ Migration failed: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_migration()
