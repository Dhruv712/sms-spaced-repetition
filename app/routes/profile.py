from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models import User
from app.services.auth import get_current_active_user

router = APIRouter()

# Pydantic schema for profile input/output
class UserProfile(BaseModel):
    name: str
    study_mode: str  # 'batch' or 'distributed'
    preferred_start_hour: int
    preferred_end_hour: int
    timezone: str

@router.get("/profile", response_model=UserProfile)
def get_user_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    return UserProfile(
        name=current_user.name,
        study_mode=current_user.study_mode,
        preferred_start_hour=current_user.preferred_start_hour,
        preferred_end_hour=current_user.preferred_end_hour,
        timezone=current_user.timezone
    )

@router.put("/profile", response_model=UserProfile)
def update_user_profile(
    profile: UserProfile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    current_user.name = profile.name
    current_user.study_mode = profile.study_mode
    current_user.preferred_start_hour = profile.preferred_start_hour
    current_user.preferred_end_hour = profile.preferred_end_hour
    current_user.timezone = profile.timezone

    db.commit()
    db.refresh(current_user)

    return profile
