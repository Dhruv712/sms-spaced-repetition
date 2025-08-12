from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User

def list_all_users():
    """List all users in the database"""
    db = next(get_db())
    
    users = db.query(User).all()
    
    if users:
        print(f"📋 Found {len(users)} users:")
        print("-" * 50)
        for user in users:
            print(f"ID: {user.id}")
            print(f"Email: {user.email}")
            print(f"Name: {user.name}")
            print(f"Phone: {user.phone_number}")
            print(f"SMS Opt-in: {user.sms_opt_in}")
            print(f"Active: {user.is_active}")
            print("-" * 30)
    else:
        print("❌ No users found in database")

if __name__ == "__main__":
    list_all_users() 