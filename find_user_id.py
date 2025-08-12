from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User

def find_user_by_email(email: str):
    """Find user by email and return their ID"""
    db = next(get_db())
    
    user = db.query(User).filter_by(email=email).first()
    
    if user:
        print(f"✅ Found user:")
        print(f"   ID: {user.id}")
        print(f"   Email: {user.email}")
        print(f"   Name: {user.name}")
        print(f"   Phone: {user.phone_number}")
        print(f"   SMS Opt-in: {user.sms_opt_in}")
        return user.id
    else:
        print(f"❌ No user found with email: {email}")
        return None

if __name__ == "__main__":
    email = input("Enter email to find user ID: ").strip()
    if email:
        find_user_by_email(email)
    else:
        print("❌ Email required") 