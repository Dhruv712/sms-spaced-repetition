#!/usr/bin/env python3
"""
Simple script to cleanup old conversations
Called by Railway's scheduled service
"""

import os
import sys
import requests
from datetime import datetime
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

load_dotenv()

def main():
    """Cleanup old conversations"""
    try:
        app_url = os.getenv('APP_URL', 'https://sms-spaced-repetition-production.up.railway.app')
        
        print(f"🧹 {datetime.now()}: Cleaning up old conversations...")
        
        response = requests.post(f"{app_url}/cron/cleanup")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {datetime.now()}: Cleanup completed - {result}")
        else:
            print(f"❌ {datetime.now()}: Failed to cleanup - {response.status_code}")
            
    except Exception as e:
        print(f"❌ {datetime.now()}: Error during cleanup - {e}")

if __name__ == "__main__":
    main()
