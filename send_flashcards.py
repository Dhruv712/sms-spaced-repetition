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
        admin_secret = os.getenv('ADMIN_SECRET_KEY')
        
        if not admin_secret:
            print(f"❌ {datetime.now()}: ADMIN_SECRET_KEY not set!")
            return False
        
        print(f"📤 {datetime.now()}: Sending due flashcards...")
        
        headers = {
            'X-Admin-Secret': admin_secret
        }
        
        response = requests.post(f"{app_url}/admin/cron/send-flashcards", headers=headers)
        
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
        admin_secret = os.getenv('ADMIN_SECRET_KEY')
        
        if not admin_secret:
            print(f"❌ {datetime.now()}: ADMIN_SECRET_KEY not set!")
            return False
        
        print(f"📊 {datetime.now()}: Sending daily summaries...")
        
        headers = {
            'X-Admin-Secret': admin_secret
        }
        
        response = requests.post(f"{app_url}/admin/cron/daily-summary", headers=headers)
        
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

def send_streak_reminders():
    """Send streak reminders"""
    try:
        app_url = os.getenv('APP_URL', 'https://sms-spaced-repetition-production.up.railway.app')
        admin_secret = os.getenv('ADMIN_SECRET_KEY')
        
        if not admin_secret:
            print(f"❌ {datetime.now()}: ADMIN_SECRET_KEY not set!")
            return False
        
        print(f"🔥 {datetime.now()}: Checking streak reminders...")
        
        headers = {
            'X-Admin-Secret': admin_secret
        }
        
        response = requests.post(f"{app_url}/admin/cron/streak-reminders", headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {datetime.now()}: Streak reminders sent successfully - {result}")
            return True
        else:
            print(f"❌ {datetime.now()}: Failed to send streak reminders - {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ {datetime.now()}: Error sending streak reminders - {e}")
        return False

def main():
    """Main function - send flashcards, daily summaries, and streak reminders"""
    current_time = datetime.now(timezone.utc)
    
    print(f"🕐 {current_time}: Running scheduled tasks...")
    
    # Send flashcards (checks user timezones internally)
    print(f"📚 {current_time}: Sending flashcards...")
    flashcard_success = send_flashcards()
    
    # Send daily summaries (checks user timezones internally - only sends at 9-10 PM user time)
    print(f"📊 {current_time}: Checking daily summaries...")
    summary_success = send_daily_summary()
    
    # Send streak reminders (checks user timezones internally - only sends at 6-8 PM user time)
    print(f"🔥 {current_time}: Checking streak reminders...")
    reminder_success = send_streak_reminders()
    
    if flashcard_success and summary_success and reminder_success:
        print(f"✅ {current_time}: Tasks completed successfully")
    else:
        print(f"⚠️ {current_time}: Some tasks may have failed")

if __name__ == "__main__":
    main()
