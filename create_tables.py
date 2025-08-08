#!/usr/bin/env python3
"""
Script to safely create database tables without dropping existing data
"""
import os
from sqlalchemy import create_engine, text, inspect
from app.models import Base

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:HKxMQCyIZjoNLhYHNuBGEtnqYUCSFFhW@postgres.railway.internal:5432/railway")

engine = create_engine(DATABASE_URL)

def safe_create_tables():
    """Create tables only if they don't exist"""
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    
    if not existing_tables:
        print("No tables found, creating all tables...")
        Base.metadata.create_all(engine)
        print("Created all tables")
    else:
        print(f"Found existing tables: {existing_tables}")
        print("Using existing database structure")

def recreate_database():
    """DANGER: Only use this in development! Drops all data."""
    with engine.connect() as conn:
        # Drop all tables
        conn.execute(text("DROP SCHEMA public CASCADE;"))
        conn.execute(text("CREATE SCHEMA public;"))
        conn.commit()
        print("Dropped all tables")
        
        # Create all tables
        Base.metadata.create_all(engine)
        print("Created all tables")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--recreate":
        print("WARNING: This will delete all data!")
        recreate_database()
    else:
        safe_create_tables()