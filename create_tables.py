#!/usr/bin/env python3
"""
Script to create database tables
"""
from app.database import engine, Base
from app.models import User, Flashcard, CardReview, StudySession, ConversationState

def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    create_tables()