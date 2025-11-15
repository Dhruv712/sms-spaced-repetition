#!/usr/bin/env python3
"""
Run the admin field migration
"""

import requests
import os
import sys

def run_admin_migration():
    """Run the admin field migration"""
    
    # Railway backend API URL
    base_url = "https://sms-spaced-repetition-production.up.railway.app"
    
    # Get admin secret key from environment or command line argument
    admin_secret = os.getenv("ADMIN_SECRET_KEY")
    if not admin_secret and len(sys.argv) > 1:
        admin_secret = sys.argv[1]
    
    if not admin_secret:
        print("❌ ADMIN_SECRET_KEY not found!")
        print("   Set it as an environment variable or pass it as an argument:")
        print("   python run_admin_migration.py <your-admin-secret-key>")
        sys.exit(1)
    
    # Headers
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-Admin-Secret': admin_secret
    }
    
    try:
        print("🔧 Running admin field migration...")
        print(f"📡 Calling: {base_url}/admin/migrate-admin-field-public")
        
        response = requests.post(
            f"{base_url}/admin/migrate-admin-field-public",
            headers=headers
        )
        
        print(f"📡 Response status: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"✅ Migration completed successfully!")
                print(f"   Message: {result.get('message', 'N/A')}")
                if 'results' in result:
                    print(f"   Results:")
                    for res in result['results']:
                        print(f"     - {res}")
                return True
            except Exception as e:
                print(f"⚠️ Response is not JSON: {response.text}")
                return False
        else:
            print(f"❌ Migration failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_admin_migration()
    sys.exit(0 if success else 1)

