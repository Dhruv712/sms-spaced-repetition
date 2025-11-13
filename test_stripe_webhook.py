#!/usr/bin/env python3
"""
Test script to verify Stripe webhook endpoint is working
"""

import requests
import json
import hmac
import hashlib
import time

def test_stripe_webhook_endpoint():
    """Test if the Stripe webhook endpoint is accessible"""
    
    # Railway webhook URL
    webhook_url = "https://sms-spaced-repetition-production.up.railway.app/subscription/webhook"
    
    # Simulate a Stripe webhook payload (checkout.session.completed event)
    test_payload = {
        "id": "evt_test_webhook",
        "object": "event",
        "api_version": "2023-10-16",
        "created": int(time.time()),
        "data": {
            "object": {
                "id": "cs_test_123",
                "object": "checkout.session",
                "customer": "cus_test_123",
                "subscription": "sub_test_123",
                "metadata": {
                    "user_id": "1"
                },
                "mode": "subscription",
                "status": "complete"
            }
        },
        "type": "checkout.session.completed"
    }
    
    print(f"🧪 Testing Stripe webhook endpoint: {webhook_url}")
    print(f"📤 Sending test payload (checkout.session.completed event)")
    
    # Note: This test won't work without proper Stripe signature
    # For real testing, use Stripe Dashboard or Stripe CLI
    try:
        response = requests.post(
            webhook_url,
            json=test_payload,
            headers={
                "Content-Type": "application/json",
                "stripe-signature": "test_signature"  # This will fail signature verification, but tests if endpoint exists
            },
            timeout=30
        )
        
        print(f"📥 Response status: {response.status_code}")
        print(f"📥 Response text: {response.text[:500]}")
        
        if response.status_code == 400:
            # 400 is expected if signature verification fails, but means endpoint exists
            if "signature" in response.text.lower() or "webhook secret" in response.text.lower():
                print("✅ Webhook endpoint exists! (Signature verification failed as expected)")
            else:
                print(f"⚠️ Endpoint responded but with unexpected error: {response.text}")
        elif response.status_code == 500:
            if "webhook secret not configured" in response.text.lower():
                print("✅ Webhook endpoint exists! (Webhook secret not configured yet)")
            else:
                print(f"⚠️ Endpoint exists but has an error: {response.text}")
        elif response.status_code == 200:
            print("✅ Webhook endpoint is working!")
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print(f"❌ Request timed out - webhook may be hanging")
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection error - webhook endpoint may be down")
    except Exception as e:
        print(f"❌ Error testing webhook: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("Stripe Webhook Test")
    print("=" * 60)
    print("\n⚠️  Note: This is a basic connectivity test.")
    print("For full testing with proper signatures, use:")
    print("  1. Stripe Dashboard -> Webhooks -> Send test webhook")
    print("  2. Stripe CLI: stripe listen --forward-to <your-url>")
    print("=" * 60)
    print()
    test_stripe_webhook_endpoint()

