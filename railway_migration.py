#!/usr/bin/env python3
"""
Railway migration script to add SM-2 columns
Run this on Railway to add the missing columns
"""

import os
import sys
from dotenv import load_dotenv

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def migrate_railway_db():
    """Add SM-2 columns to Railway database"""
    
    try:
        from database import engine
        
        print("🔧 Adding SM-2 columns to Railway database...")
        
        # SQL to add the SM-2 columns
        sql_commands = [
            """
            ALTER TABLE card_reviews 
            ADD COLUMN IF NOT EXISTS repetition_count INTEGER DEFAULT 0;
            """,
            """
            ALTER TABLE card_reviews 
            ADD COLUMN IF NOT EXISTS ease_factor FLOAT DEFAULT 2.5;
            """,
            """
            ALTER TABLE card_reviews 
            ADD COLUMN IF NOT EXISTS interval_days INTEGER DEFAULT 0;
            """
        ]
        
        with engine.connect() as conn:
            for i, sql in enumerate(sql_commands, 1):
                print(f"📝 Executing SQL command {i}...")
                try:
                    conn.execute(sql)
                    conn.commit()
                    print(f"✅ SQL command {i} executed successfully")
                except Exception as e:
                    print(f"⚠️ SQL command {i} result: {e}")
                    # Continue even if column already exists
        
        print("🎉 Railway database migration completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    migrate_railway_db()
