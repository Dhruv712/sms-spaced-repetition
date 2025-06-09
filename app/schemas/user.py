from pydantic import BaseModel
from typing import Optional

class UserCreate(BaseModel):
    phone_number: str
    name: Optional[str] = None