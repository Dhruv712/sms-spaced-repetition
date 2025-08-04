#!/usr/bin/env python3
"""
Test script to check image URLs in the database
"""
from app.database import SessionLocal
from app.models import Deck

def get_full_image_url(image_url: str | None) -> str | None:
    """Convert relative image URL to full URL if needed"""
    if not image_url:
        return None
    
    # If it's already a full URL, return as is
    if image_url.startswith('http'):
        return image_url
    
    # Convert relative URL to full URL
    return f"http://localhost:8000{image_url}"

def check_deck_image_urls():
    db = SessionLocal()
    try:
        decks = db.query(Deck).all()
        print("Current decks in database:")
        for deck in decks:
            print(f"Deck {deck.id}: {deck.name}")
            print(f"  Original Image URL: {deck.image_url}")
            print(f"  Full Image URL: {get_full_image_url(deck.image_url)}")
            print(f"  User ID: {deck.user_id}")
            print("---")
    finally:
        db.close()

if __name__ == "__main__":
    check_deck_image_urls() 