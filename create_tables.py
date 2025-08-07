#!/usr/bin/env python3
"""
Script to create database tables
"""
import os
from sqlalchemy import create_engine, text
from app.models import Base

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:HKxMQCyIZjoNLhYHNuBGEtnqYUCSFFhW@postgres.railway.internal:5432/railway")

engine = create_engine(DATABASE_URL)

def recreate_database():
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
    recreate_database()