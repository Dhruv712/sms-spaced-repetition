#!/usr/bin/env python3
"""
Test script to verify Railway webhook endpoint is working
"""

import requests
import json

def test_webhook_endpoint():
    """Test if the webhook endpoint is accessible"""
    
    # Railway webhook URL
    webhook_url = "https://sms-spaced-repetition-production.up.railway.app/loop-webhook/webhook"
    
    # Test payload - simulate a simple message_inbound webhook
    test_payload = {
        "alert_type": "message_inbound",
        "delivery_type": "imessage",
        "recipient": "+18054901242",
        "text": "test message",
        "passthrough": "flashcard_id:4",
        "message_id": "test-123",
        "sandbox": True
    }
    
    print(f"🧪 Testing webhook endpoint: {webhook_url}")
    print(f"📤 Sending test payload: {json.dumps(test_payload, indent=2)}")
    
    try:
        # Send POST request to webhook
        response = requests.post(
            webhook_url,
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=30  # 30 second timeout
        )
        
        print(f"📥 Response status: {response.status_code}")
        print(f"📥 Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print(f"✅ Webhook endpoint is accessible!")
            try:
                response_data = response.json()
                print(f"📥 Response data: {json.dumps(response_data, indent=2)}")
            except:
                print(f"📥 Response text: {response.text}")
        else:
            print(f"❌ Webhook endpoint returned error: {response.status_code}")
            print(f"📥 Response text: {response.text}")
            
    except requests.exceptions.Timeout:
        print(f"❌ Request timed out - webhook may be hanging")
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection error - webhook endpoint may be down")
    except Exception as e:
        print(f"❌ Error testing webhook: {e}")

def test_webhook_without_passthrough():
    """Test webhook with no passthrough data (like in your logs)"""
    
    webhook_url = "https://sms-spaced-repetition-production.up.railway.app/loop-webhook/webhook"
    
    # Test payload matching your logs - no passthrough
    test_payload = {
        "alert_type": "message_inbound",
        "delivery_type": "imessage",
        "recipient": "+18054901242",
        "text": "The molecule that encodes genetic information",
        "message_id": "test-no-passthrough-123",
        "sandbox": True
    }
    
    print(f"\n🧪 Testing webhook WITHOUT passthrough data")
    print(f"📤 Sending test payload: {json.dumps(test_payload, indent=2)}")
    
    try:
        response = requests.post(
            webhook_url,
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Webhook processed without passthrough!")
            try:
                response_data = response.json()
                print(f"📥 Response data: {json.dumps(response_data, indent=2)}")
            except:
                print(f"📥 Response text: {response.text}")
        else:
            print(f"❌ Webhook failed: {response.status_code}")
            print(f"📥 Response text: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing webhook without passthrough: {e}")

def test_conversation_state_fallback():
    """Test webhook with conversation state fallback (no passthrough)"""
    
    webhook_url = "https://sms-spaced-repetition-production.up.railway.app/loop-webhook/webhook"
    
    # Test payload - user reply without passthrough, should use conversation state
    test_payload = {
        "alert_type": "message_inbound",
        "delivery_type": "imessage",
        "recipient": "+18054901242",
        "text": "DNA is the molecule that contains genetic information",
        "message_id": "test-conversation-state-123",
        "sandbox": True
    }
    
    print(f"\n🧪 Testing conversation state fallback")
    print(f"📤 Sending test payload: {json.dumps(test_payload, indent=2)}")
    
    try:
        response = requests.post(
            webhook_url,
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Webhook processed with conversation state!")
            try:
                response_data = response.json()
                print(f"📥 Response data: {json.dumps(response_data, indent=2)}")
            except:
                print(f"📥 Response text: {response.text}")
        else:
            print(f"❌ Webhook failed: {response.status_code}")
            print(f"📥 Response text: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing conversation state: {e}")

if __name__ == "__main__":
    test_webhook_endpoint()
    test_webhook_without_passthrough()
    test_conversation_state_fallback() 