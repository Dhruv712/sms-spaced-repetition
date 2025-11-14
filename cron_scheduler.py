#!/usr/bin/env python3
"""
Cron scheduler for Railway
This service runs on a schedule and calls the flashcard endpoints
"""

import os
import sys
import requests
import time
import schedule
from datetime import datetime
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

load_dotenv()

def send_flashcards():
    """Send due flashcards to all users"""
    try:
        app_url = os.getenv('APP_URL', 'https://sms-spaced-repetition-production.up.railway.app')
        response = requests.post(f"{app_url}/cron/send-flashcards")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {datetime.now()}: Flashcards sent successfully - {result}")
        else:
            print(f"❌ {datetime.now()}: Failed to send flashcards - {response.status_code}")
            
    except Exception as e:
        print(f"❌ {datetime.now()}: Error sending flashcards - {e}")

def cleanup_conversations():
    """Clean up old conversation states"""
    try:
        app_url = os.getenv('APP_URL', 'https://sms-spaced-repetition-production.up.railway.app')
        response = requests.post(f"{app_url}/cron/cleanup")
        
        if response.status_code == 200:
            result = response.json()
            print(f"🧹 {datetime.now()}: Cleanup completed - {result}")
        else:
            print(f"❌ {datetime.now()}: Failed to cleanup - {response.status_code}")
            
    except Exception as e:
        print(f"❌ {datetime.now()}: Error during cleanup - {e}")

def main():
    """Main scheduler function"""
    print(f"⏰ Cron scheduler starting at {datetime.now()}")
    
    # Schedule flashcard sending every hour
    # The function will check each user's preferred_text_times and timezone
    schedule.every().hour.at(":00").do(send_flashcards)
    
    # Schedule cleanup every 2 hours
    schedule.every(2).hours.do(cleanup_conversations)
    
    print("📅 Scheduled tasks:")
    print("   - Send flashcards: Every hour (checks user's preferred times)")
    print("   - Cleanup conversations: Every 2 hours")
    
    # Run cleanup once on startup
    print("🧹 Running initial cleanup...")
    cleanup_conversations()
    
    # Keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    main()
