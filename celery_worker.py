#!/usr/bin/env python3
"""
Celery worker for Railway deployment
"""

import os
import sys
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

load_dotenv()

if __name__ == "__main__":
    from app.utils.celery_app import celery_app
    
    # Start the Celery worker
    celery_app.worker_main(['worker', '--loglevel=info'])
