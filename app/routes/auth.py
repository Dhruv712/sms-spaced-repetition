from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas.user import UserCreate, UserOut
from app.services.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_active_user
)
from app.services.google_auth import google_auth_service
from app.utils.config import settings

router = APIRouter()

@router.post("/register", response_model=UserOut)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        password_hash=hashed_password,
        phone_number=user.phone_number,
        name=user.name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserOut)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.get("/google/debug")
async def google_debug():
    """Debug Google OAuth configuration"""
    return {
        "redirect_uri": google_auth_service.redirect_uri,
        "client_id": google_auth_service.client_id[:20] + "..." if google_auth_service.client_id else None,
        "has_client_secret": bool(google_auth_service.client_secret)
    }

@router.get("/google")
async def google_auth():
    """Initiate Google OAuth flow"""
    try:
        authorization_url = google_auth_service.get_authorization_url()
        print(f"🔗 Google OAuth redirect URI: {google_auth_service.redirect_uri}")
        print(f"🔗 Generated authorization URL: {authorization_url}")
        return RedirectResponse(url=authorization_url)
    except Exception as e:
        print(f"❌ Google OAuth error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initiate Google OAuth: {str(e)}"
        )

@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """Handle Google OAuth callback"""
    try:
        # Get the authorization code from the callback
        code = request.query_params.get("code")
        if not code:
            raise HTTPException(
                status_code=400,
                detail="Authorization code not provided"
            )
        
        # Exchange code for token using Google's token endpoint
        import requests
        
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "client_id": google_auth_service.client_id,
            "client_secret": google_auth_service.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": google_auth_service.redirect_uri
        }
        
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        token_info = token_response.json()
        
        # Get user info from Google
        user_info_url = f"https://www.googleapis.com/oauth2/v2/userinfo?access_token={token_info['access_token']}"
        user_response = requests.get(user_info_url)
        user_response.raise_for_status()
        google_user_data = user_response.json()
        
        # Create or update user
        user = google_auth_service.create_or_update_user(google_user_data, db)
        
        # Create JWT token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        # Redirect to frontend with token
        return RedirectResponse(
            url=f"https://trycue.xyz/login?google_success=true&token={access_token}"
        )
        
    except Exception as e:
        print(f"❌ Google OAuth callback error: {e}")
        return RedirectResponse(
            url=f"https://trycue.xyz/login?google_error={str(e)}"
        )

@router.post("/google/verify")
async def verify_google_token(
    request: Request,
    db: Session = Depends(get_db)
):
    """Verify Google ID token and create/login user"""
    try:
        body = await request.json()
        token = body.get("token")
        
        if not token:
            raise HTTPException(
                status_code=400,
                detail="Google token not provided"
            )
        
        # Verify the Google token
        google_user_data = google_auth_service.verify_token(token)
        if not google_user_data:
            raise HTTPException(
                status_code=401,
                detail="Invalid Google token"
            )
        
        # Create or update user
        user = google_auth_service.create_or_update_user(google_user_data, db)
        
        # Create JWT token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to verify Google token: {str(e)}"
        ) 