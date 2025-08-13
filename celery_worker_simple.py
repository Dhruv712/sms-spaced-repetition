#!/usr/bin/env python3
"""
Simple Celery worker for Railway
"""

import os
import sys
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

load_dotenv()

if __name__ == "__main__":
    from app.utils.celery_app import celery_app
    
    # Print Redis URL for debugging
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    print(f"🔗 Using Redis URL: {redis_url}")
    
    print("🚀 Starting Celery worker...")
    # Use single process to reduce memory usage
    celery_app.worker_main(['worker', '--loglevel=info', '--concurrency=1'])
