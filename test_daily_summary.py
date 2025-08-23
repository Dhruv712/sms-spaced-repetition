#!/usr/bin/env python3
"""
Test script for daily summary feature
"""

import requests
import json

# Railway backend URL
app_url = "https://sms-spaced-repetition-production.up.railway.app"

def test_daily_summary():
    """Test the daily summary endpoint"""
    
    print("🧪 Testing daily summary feature...")
    print("=" * 50)
    
    # Test the daily summary cron endpoint
    print("🚀 Testing daily summary cron endpoint...")
    
    try:
        response = requests.post(f"{app_url}/admin/cron/daily-summary")
        
        print(f"📡 Response status: {response.status_code}")
        print(f"📡 Response body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Daily summary endpoint working!")
            print(f"📊 Results: {data.get('message', 'No message')}")
            
            if 'results' in data:
                for result in data['results']:
                    print(f"  📱 {result.get('phone', 'Unknown')}: {'✅' if result.get('success') else '❌'}")
        else:
            print(f"❌ Daily summary endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing daily summary: {e}")

def test_user_summary():
    """Test getting summary for a specific user"""
    
    print("\n🧪 Testing user-specific summary...")
    print("=" * 50)
    
    # Test getting summary for user ID 1
    print("🚀 Testing user summary for user ID 1...")
    
    try:
        response = requests.get(f"{app_url}/admin/daily-summary/1")
        
        print(f"📡 Response status: {response.status_code}")
        print(f"📡 Response body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ User summary endpoint working!")
            if 'summary' in data:
                summary = data['summary']
                print(f"📊 Summary for {summary.get('date', 'Unknown date')}:")
                print(f"  • Total reviews: {summary.get('total_reviews', 0)}")
                print(f"  • Percent correct: {summary.get('percent_correct', 0)}%")
                print(f"  • Streak days: {summary.get('streak_days', 0)}")
                print(f"  • Next due cards: {summary.get('next_due_cards', 0)}")
        else:
            print(f"❌ User summary endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing user summary: {e}")

if __name__ == "__main__":
    print("🧪 Testing Daily Summary Feature")
    print("=" * 50)
    
    test_daily_summary()
    test_user_summary()
    
    print("\n" + "=" * 50)
    print("🏁 Test complete!")
    print("\n💡 To set up daily summaries:")
    print("1. Add a Railway cron job to call: POST /admin/cron/daily-summary")
    print("2. Set it to run daily at your preferred time (e.g., 8pm PST = 4am UTC)")
    print("3. Users will receive personalized daily summaries via SMS!")
