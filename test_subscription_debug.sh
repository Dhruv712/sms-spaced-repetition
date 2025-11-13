#!/bin/bash
# Test script to check subscription debug endpoint
# Usage: ./test_subscription_debug.sh YOUR_AUTH_TOKEN

TOKEN=$1

if [ -z "$TOKEN" ]; then
    echo "Usage: ./test_subscription_debug.sh YOUR_AUTH_TOKEN"
    echo ""
    echo "To get your token:"
    echo "1. Open your app in browser"
    echo "2. Open DevTools (F12)"
    echo "3. Go to Application/Storage tab"
    echo "4. Look for 'token' in localStorage"
    echo "5. Copy the token value"
    exit 1
fi

echo "🔍 Checking subscription status..."
echo ""

curl -X GET \
  "https://sms-spaced-repetition-production.up.railway.app/subscription/debug" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | python3 -m json.tool

echo ""

