#!/usr/bin/env python3
"""
Manually trigger daily summary right now
"""

import requests
import json

# Railway backend URL
app_url = "https://sms-spaced-repetition-production.up.railway.app"

def trigger_daily_summary():
    """Trigger the daily summary endpoint"""
    
    print("🚀 Triggering daily summary right now...")
    print("=" * 50)
    
    try:
        response = requests.post(f"{app_url}/admin/cron/daily-summary")
        
        print(f"📡 Response status: {response.status_code}")
        print(f"📡 Response body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Daily summary triggered successfully!")
            print(f"📊 Results: {data.get('message', 'No message')}")
            
            if 'results' in data:
                for result in data['results']:
                    print(f"  📱 {result.get('phone', 'Unknown')}: {'✅' if result.get('success') else '❌'}")
                    if result.get('success') and 'summary' in result:
                        summary = result['summary']
                        print(f"     📊 {summary.get('total_reviews', 0)} cards reviewed, {summary.get('percent_correct', 0)}% correct")
        else:
            print(f"❌ Daily summary failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error triggering daily summary: {e}")

if __name__ == "__main__":
    trigger_daily_summary()
