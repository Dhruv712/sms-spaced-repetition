from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Flashcard
from typing import List

router = APIRouter()

@router.get("/users")
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@router.get("/flashcards")
def list_flashcards(db: Session = Depends(get_db)):
    return db.query(Flashcard).all()
