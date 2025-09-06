#!/usr/bin/env python3
"""
Script to manually add Google OAuth columns to the database
This is a one-time fix for the Railway database
"""
import os
from sqlalchemy import create_engine, text
from app.utils.config import settings

def add_google_columns():
    """Add Google OAuth columns to the users table"""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Start a transaction
        trans = conn.begin()
        try:
            # Add google_id column if it doesn't exist
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS google_id VARCHAR(255)
            """))
            
            # Make password_hash nullable if it isn't already
            conn.execute(text("""
                ALTER TABLE users 
                ALTER COLUMN password_hash DROP NOT NULL
            """))
            
            # Make phone_number nullable if it isn't already
            conn.execute(text("""
                ALTER TABLE users 
                ALTER COLUMN phone_number DROP NOT NULL
            """))
            
            # Create index on google_id if it doesn't exist
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_users_google_id 
                ON users (google_id)
            """))
            
            # Commit the transaction
            trans.commit()
            print("✅ Successfully added Google OAuth columns to database")
            
        except Exception as e:
            # Rollback on error
            trans.rollback()
            print(f"❌ Error adding columns: {e}")
            raise

if __name__ == "__main__":
    add_google_columns()
