#!/usr/bin/env python3
"""
Combined Celery worker and beat scheduler for Railway
"""

import os
import sys
import subprocess
import threading
import time
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

load_dotenv()

def run_worker():
    """Run the Celery worker"""
    from app.utils.celery_app import celery_app
    print("🚀 Starting Celery worker...")
    # Use fewer processes to reduce memory usage
    celery_app.worker_main(['worker', '--loglevel=info', '--concurrency=1'])

def run_beat():
    """Run the Celery beat scheduler"""
    from app.utils.celery_app import celery_app
    print("⏰ Starting Celery beat scheduler...")
    celery_app.start(['beat', '--loglevel=info'])

if __name__ == "__main__":
    print("🔧 Starting combined Celery worker and beat scheduler...")
    
    # Print Redis URL for debugging
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    print(f"🔗 Using Redis URL: {redis_url}")
    
    # Start beat scheduler in a separate thread
    beat_thread = threading.Thread(target=run_beat, daemon=True)
    beat_thread.start()
    
    # Give beat a moment to start
    time.sleep(2)
    
    # Start worker in main thread
    run_worker()
