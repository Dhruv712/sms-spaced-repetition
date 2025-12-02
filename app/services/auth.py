from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Request as FastAPIRequest
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.utils.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login/token")

def _truncate_password_to_72_bytes(password: str) -> str:
    """
    Bcrypt has a 72-byte limit. Truncate password to 72 bytes if necessary.
    This is a safety measure - validation should catch this earlier.
    Safely handles UTF-8 multi-byte characters by truncating character by character.
    """
    password_bytes = password.encode('utf-8')
    if len(password_bytes) <= 72:
        return password
    
    # Truncate character by character to avoid breaking UTF-8 sequences
    result = ""
    for char in password:
        test_result = result + char
        if len(test_result.encode('utf-8')) > 72:
            break
        result = test_result
    return result

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Truncate password to 72 bytes before verification to match how it was hashed
    truncated_password = _truncate_password_to_72_bytes(plain_password)
    return pwd_context.verify(truncated_password, hashed_password)

def get_password_hash(password: str) -> str:
    # Truncate password to 72 bytes before hashing (bcrypt limitation)
    truncated_password = _truncate_password_to_72_bytes(password)
    return pwd_context.hash(truncated_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_user_optional(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Get current user if authenticated, otherwise return None
    Used for endpoints that work for both logged-in and non-logged-in users
    """
    # Extract token from Authorization header manually
    authorization = request.headers.get("Authorization")
    if not authorization:
        return None
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            return None
    except ValueError:
        return None
    
    if not token:
        return None
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
    except JWTError:
        return None
    
    user = db.query(User).filter(User.email == email).first()
    if user is None or not user.is_active:
        return None
    return user

async def require_admin_access(
    request: FastAPIRequest,
    db: Session = Depends(get_db)
) -> bool:
    """
    Check if request has valid admin access via either:
    1. Admin secret key in X-Admin-Secret header, OR
    2. Authenticated admin user
    Returns True if authorized, raises HTTPException if not
    """
    from app.utils.config import settings
    
    # Check for admin secret key in header (for Railway cron, etc.)
    admin_secret = request.headers.get("X-Admin-Secret")
    if admin_secret and settings.ADMIN_SECRET_KEY and admin_secret == settings.ADMIN_SECRET_KEY:
        return True
    
    # Check for authenticated admin user
    try:
        authorization = request.headers.get("Authorization")
        if authorization:
            try:
                scheme, token = authorization.split()
                if scheme.lower() == "bearer" and token:
                    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
                    email: str = payload.get("sub")
                    if email:
                        user = db.query(User).filter(User.email == email).first()
                        if user and user.is_active and user.is_admin:
                            return True
            except (JWTError, ValueError):
                pass
    except:
        pass
    
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Admin access required. Provide X-Admin-Secret header or authenticate as admin user."
    ) 