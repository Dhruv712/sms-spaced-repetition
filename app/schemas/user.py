from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    phone_number: Optional[str] = None
    name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=72, description="Password must be between 8 and 72 characters")
    sms_opt_in: Optional[bool] = False
    
    @field_validator('password')
    @classmethod
    def validate_password_length(cls, v: str) -> str:
        if len(v.encode('utf-8')) > 72:
            raise ValueError("Password cannot exceed 72 bytes. Please use a shorter password.")
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(UserBase):
    id: int
    is_active: bool
    study_mode: str
    preferred_start_hour: int
    preferred_end_hour: int
    timezone: str
    sms_opt_in: bool

    class Config:
        from_attributes = True