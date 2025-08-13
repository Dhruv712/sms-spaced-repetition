#!/usr/bin/env python3
"""
Test LoopMessageService initialization
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_loop_service_init():
    """Test LoopMessageService initialization"""
    
    print("🔧 Testing LoopMessageService initialization...")
    
    # Check environment variables
    print("🔍 Checking environment variables...")
    auth_key = os.getenv("LOOPMESSAGE_AUTH_KEY")
    secret_key = os.getenv("LOOPMESSAGE_SECRET_KEY")
    sender_name = os.getenv("LOOPMESSAGE_SENDER_NAME")
    
    print(f"   - LOOPMESSAGE_AUTH_KEY: {'✅ Set' if auth_key else '❌ Missing'}")
    print(f"   - LOOPMESSAGE_SECRET_KEY: {'✅ Set' if secret_key else '❌ Missing'}")
    print(f"   - LOOPMESSAGE_SENDER_NAME: {'✅ Set' if sender_name else '❌ Missing'}")
    
    if not all([auth_key, secret_key, sender_name]):
        print("❌ Missing required environment variables!")
        return
    
    # Try to import and initialize the service
    try:
        print("🔧 Importing LoopMessageService...")
        from app.services.loop_message_service import LoopMessageService
        print("✅ Import successful")
        
        print("🔧 Initializing LoopMessageService...")
        service = LoopMessageService()
        print("✅ LoopMessageService initialized successfully!")
        
        # Test a simple method
        print("🔧 Testing service methods...")
        print(f"   - Service URL: {service.base_url}")
        print(f"   - Sender name: {service.sender_name}")
        
    except Exception as e:
        print(f"❌ Error initializing LoopMessageService: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_loop_service_init() 