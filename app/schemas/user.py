from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    phone_number: str
    name: Optional[str] = None

class UserCreate(UserBase):
    password: str

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

    class Config:
        from_attributes = True