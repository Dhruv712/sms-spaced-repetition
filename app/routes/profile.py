from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models import User

router = APIRouter()

# Pydantic schema for profile input/output
class UserProfile(BaseModel):
    name: str
    study_mode: str  # 'batch' or 'distributed'
    preferred_start_hour: int
    preferred_end_hour: int
    timezone: str

@router.get("/profile/{user_id}", response_model=UserProfile)
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserProfile(
        name=user.name,
        study_mode=user.study_mode,
        preferred_start_hour=user.preferred_start_hour,
        preferred_end_hour=user.preferred_end_hour,
        timezone=user.timezone
    )

@router.put("/profile/{user_id}", response_model=UserProfile)
def update_user_profile(user_id: int, profile: UserProfile, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.name = profile.name
    user.study_mode = profile.study_mode
    user.preferred_start_hour = profile.preferred_start_hour
    user.preferred_end_hour = profile.preferred_end_hour
    user.timezone = profile.timezone

    db.commit()
    db.refresh(user)

    return profile
