#!/usr/bin/env python3
"""
Migration script to add SM-2 fields to CardReview model
"""

import os
import sys
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

load_dotenv()

def add_sm2_fields():
    """Add SM-2 fields to CardReview table"""
    
    try:
        from database import SessionLocal, engine
        from sqlalchemy import text
        
        db = SessionLocal()
        
        # Add SM-2 fields to CardReview table
        print("🔧 Adding SM-2 fields to CardReview table...")
        
        # Add repetition_count field
        db.execute(text("""
            ALTER TABLE card_reviews 
            ADD COLUMN repetition_count INTEGER DEFAULT 0
        """))
        print("✅ Added repetition_count field")
        
        # Add ease_factor field
        db.execute(text("""
            ALTER TABLE card_reviews 
            ADD COLUMN ease_factor FLOAT DEFAULT 2.5
        """))
        print("✅ Added ease_factor field")
        
        # Add interval field (in days)
        db.execute(text("""
            ALTER TABLE card_reviews 
            ADD COLUMN interval_days INTEGER DEFAULT 0
        """))
        print("✅ Added interval_days field")
        
        db.commit()
        print("✅ Migration completed successfully!")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    add_sm2_fields()
