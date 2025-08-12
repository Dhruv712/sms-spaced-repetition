import requests
import json
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def send_test_message(
    phone_number: str,
    message_text: str = "Hello! This is a test message from your SMS spaced repetition app.",
    sender_name: Optional[str] = None
) -> dict:
    """
    Send a test message using LoopMessage API
    
    Args:
        phone_number: The recipient's phone number (international format)
        message_text: The message to send
        sender_name: Your dedicated sender name from LoopMessage
    
    Returns:
        dict: API response
    """
    
    # API endpoint
    url = "https://server.loopmessage.com/api/v1/message/send/"
    
    # Headers
    headers = {
        "Authorization": os.getenv("LOOPMESSAGE_AUTH_KEY"),
        "Loop-Secret-Key": os.getenv("LOOPMESSAGE_SECRET_KEY"),
        "Content-Type": "application/json"
    }
    
    # Request body
    payload = {
        "recipient": phone_number,
        "text": message_text,
        "sender_name": sender_name or os.getenv("LOOP_SENDER_NAME")
    }
    
    try:
        print(f"Sending test message to {phone_number}...")
        print(f"Message: {message_text}")
        print(f"Sender: {payload['sender_name']}")
        
        response = requests.post(url, headers=headers, json=payload)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print("✅ Message sent successfully!")
                print(f"Message ID: {result.get('message_id')}")
            else:
                print("❌ Message failed to send")
                print(f"Error: {result.get('message')}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
        return response.json()
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return {"success": False, "error": str(e)}
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON response: {e}")
        return {"success": False, "error": "Invalid JSON response"}

def main():
    """Main function to run the test"""
    
    # Check if required environment variables are set
    required_env_vars = ["LOOPMESSAGE_AUTH_KEY", "LOOPMESSAGE_SECRET_KEY", "LOOPMESSAGE_SENDER_NAME"]
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease add these variables to your .env file:")
        print("LOOPMESSAGE_AUTH_KEY=your_authorization_key")
        print("LOOPMESSAGE_SECRET_KEY=your_secret_key")
        print("LOOPMESSAGE_SENDER_NAME=your_sender_name")
        return
    
    # Get phone number from user input
    phone_number = input("Enter your phone number (international format, e.g., +1234567890): ").strip()
    
    if not phone_number:
        print("❌ Phone number is required")
        return
    
    # Normalize phone number (remove spaces, dashes, brackets)
    phone_number = phone_number.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    
    # Add + prefix if not present
    if not phone_number.startswith("+"):
        phone_number = "+" + phone_number
    
    print(f"\n📱 Testing LoopMessage API with phone number: {phone_number}")
    print("=" * 50)
    
    # Send test message
    result = send_test_message(phone_number)
    
    print("\n" + "=" * 50)
    if result.get("success"):
        print("🎉 Test completed successfully! Check your phone for the message.")
    else:
        print("💥 Test failed. Check the error messages above.")

if __name__ == "__main__":
    main() 