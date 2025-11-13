import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any
from dotenv import load_dotenv

load_dotenv()

def send_contact_email(user_email: str, subject: str, message: str) -> Dict[str, Any]:
    """
    Send a contact form email to the admin
    
    Args:
        user_email: Email of the user sending the message
        subject: Subject of the message
        message: Message content
        
    Returns:
        Dict with success status
    """
    try:
        # Get email configuration from environment variables
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        smtp_username = os.getenv('SMTP_USERNAME')
        smtp_password = os.getenv('SMTP_PASSWORD')
        admin_email = os.getenv('ADMIN_EMAIL', 'dhruv.sumathi@gmail.com')
        
        if not smtp_username or not smtp_password:
            print("⚠️ SMTP credentials not configured. Email sending disabled.")
            return {
                "success": False,
                "error": "Email service not configured"
            }
        
        # Create email message
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = admin_email
        msg['Subject'] = f"Cue App Contact Form: {subject}"
        msg['Reply-To'] = user_email
        
        # Create email body
        body = f"""
New contact form submission from Cue app:

From: {user_email}
Subject: {subject}

Message:
{message}

---
This email was sent from the Cue spaced repetition app contact form.
"""
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        print(f"✅ Contact email sent successfully from {user_email} to {admin_email}")
        return {
            "success": True,
            "message": "Email sent successfully"
        }
        
    except Exception as e:
        print(f"❌ Error sending contact email: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }

