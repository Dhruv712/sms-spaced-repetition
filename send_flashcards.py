#!/usr/bin/env python3
"""
Script to send due flashcards and daily summaries
Called by Railway's scheduled service
"""

import os
import sys
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

load_dotenv()

def send_flashcards():
    """Send due flashcards"""
    try:
        app_url = os.getenv('APP_URL', 'https://sms-spaced-repetition-production.up.railway.app')
        
        print(f"📤 {datetime.now()}: Sending due flashcards...")
        
        response = requests.post(f"{app_url}/admin/cron/send-flashcards")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {datetime.now()}: Flashcards sent successfully - {result}")
            return True
        else:
            print(f"❌ {datetime.now()}: Failed to send flashcards - {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ {datetime.now()}: Error sending flashcards - {e}")
        return False

def send_daily_summary():
    """Send daily summaries"""
    try:
        app_url = os.getenv('APP_URL', 'https://sms-spaced-repetition-production.up.railway.app')
        
        print(f"📊 {datetime.now()}: Sending daily summaries...")
        
        response = requests.post(f"{app_url}/admin/cron/daily-summary")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {datetime.now()}: Daily summaries sent successfully - {result}")
            return True
        else:
            print(f"❌ {datetime.now()}: Failed to send daily summaries - {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ {datetime.now()}: Error sending daily summaries - {e}")
        return False

def main():
    """Main function - determine what to do based on current time"""
    current_hour = datetime.now(timezone.utc).hour
    current_time = datetime.now(timezone.utc)
    
    print(f"🕐 {current_time}: Current UTC hour: {current_hour}")
    
    # Schedule:
    # 12:00 UTC (12:00 PM UTC) - Send flashcards + Daily summary
    # 21:00 UTC (9:00 PM UTC) - Send flashcards
    
    if current_hour == 12:
        # 12:00 UTC - Send both flashcards and daily summary
        print(f"🌙 {current_time}: Noon time - sending flashcards and daily summary")
        flashcard_success = send_flashcards()
        summary_success = send_daily_summary()
        
        if flashcard_success and summary_success:
            print(f"✅ {current_time}: Noon time tasks completed successfully")
        else:
            print(f"⚠️ {current_time}: Some noon time tasks failed")
    elif current_hour == 21:
        # 21:00 UTC - Just send flashcards
        print(f"📚 {current_time}: Evening time - sending flashcards only")
        send_flashcards()
    else:
        # Other times - just send flashcards (for backwards compatibility)
        print(f"📚 {current_time}: Regular time - sending flashcards only")
        send_flashcards()

if __name__ == "__main__":
    main()
