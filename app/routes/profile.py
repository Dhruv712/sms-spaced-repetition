from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models import User, ConversationState
from app.services.auth import get_current_active_user

router = APIRouter()

# Pydantic schema for profile input/output
class UserProfile(BaseModel):
    name: str
    phone_number: str | None
    google_id: str | None
    study_mode: str  # 'batch' or 'distributed'
    preferred_start_hour: int
    preferred_end_hour: int
    timezone: str
    sms_opt_in: bool
    has_sms_conversation: bool
    is_premium: bool = False

@router.get("/profile", response_model=UserProfile)
def get_user_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    # Check if user has SMS conversation state
    conversation_state = db.query(ConversationState).filter_by(user_id=current_user.id).first()
    has_sms_conversation = conversation_state is not None
    
    return UserProfile(
        name=current_user.name,
        phone_number=current_user.phone_number,
        google_id=current_user.google_id,
        study_mode=current_user.study_mode,
        preferred_start_hour=current_user.preferred_start_hour,
        preferred_end_hour=current_user.preferred_end_hour,
        timezone=current_user.timezone,
        sms_opt_in=current_user.sms_opt_in,
        has_sms_conversation=has_sms_conversation,
        is_premium=current_user.is_premium or False
    )

@router.put("/profile", response_model=UserProfile)
def update_user_profile(
    profile: UserProfile,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    print(f"🔍 Received profile update request for user {current_user.id}")
    print(f"🔍 Profile data: {profile}")
    print(f"🔍 Current user data: name={current_user.name}, phone={current_user.phone_number}, google_id={current_user.google_id}")
    
    current_user.name = profile.name
    current_user.phone_number = profile.phone_number
    current_user.study_mode = profile.study_mode
    current_user.preferred_start_hour = profile.preferred_start_hour
    current_user.preferred_end_hour = profile.preferred_end_hour
    current_user.timezone = profile.timezone
    current_user.sms_opt_in = profile.sms_opt_in

    db.commit()
    db.refresh(current_user)

    # Check if user has SMS conversation state
    conversation_state = db.query(ConversationState).filter_by(user_id=current_user.id).first()
    has_sms_conversation = conversation_state is not None
    
    return UserProfile(
        name=current_user.name,
        phone_number=current_user.phone_number,
        google_id=current_user.google_id,
        study_mode=current_user.study_mode,
        preferred_start_hour=current_user.preferred_start_hour,
        preferred_end_hour=current_user.preferred_end_hour,
        timezone=current_user.timezone,
        sms_opt_in=current_user.sms_opt_in,
        has_sms_conversation=has_sms_conversation,
        is_premium=current_user.is_premium or False
    )
