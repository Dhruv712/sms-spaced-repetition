"""
Google OAuth authentication service
"""
import os
from typing import Optional, Dict, Any
from google.auth.transport import requests
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from app.utils.config import settings
from app.models.user import User
from app.database import get_db
from sqlalchemy.orm import Session


class GoogleAuthService:
    def __init__(self):
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        # Use Railway backend URL for production, localhost for development
        if settings.ENVIRONMENT == "production":
            self.redirect_uri = "https://sms-spaced-repetition-production.up.railway.app/auth/google/callback"
        else:
            self.redirect_uri = "http://localhost:8000/auth/google/callback"
        
    def get_authorization_url(self) -> str:
        """Get Google OAuth authorization URL"""
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            },
            scopes=["openid", "email", "profile"]
        )
        flow.redirect_uri = self.redirect_uri
        
        authorization_url, _ = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )
        return authorization_url
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify Google ID token and return user info"""
        try:
            idinfo = id_token.verify_oauth2_token(
                token, 
                requests.Request(), 
                self.client_id
            )
            
            # Verify the token is for the correct audience
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            
            return {
                'google_id': idinfo['sub'],
                'email': idinfo['email'],
                'name': idinfo.get('name', ''),
                'picture': idinfo.get('picture', ''),
                'email_verified': idinfo.get('email_verified', False)
            }
        except ValueError as e:
            print(f"Token verification failed: {e}")
            return None
    
    def create_or_update_user(self, google_user_data: Dict[str, Any], db: Session) -> User:
        """Create or update user from Google OAuth data"""
        # Check if user exists by Google ID
        user = db.query(User).filter(User.google_id == google_user_data['google_id']).first()
        
        if user:
            # Update existing user
            user.email = google_user_data['email']
            user.name = google_user_data['name']
            db.commit()
            db.refresh(user)
            return user
        
        # Check if user exists by email (for existing users who want to link Google)
        user = db.query(User).filter(User.email == google_user_data['email']).first()
        
        if user:
            # Link Google account to existing user
            user.google_id = google_user_data['google_id']
            user.name = google_user_data['name'] or user.name
            db.commit()
            db.refresh(user)
            return user
        
        # Create new user
        user = User(
            email=google_user_data['email'],
            google_id=google_user_data['google_id'],
            name=google_user_data['name'],
            password_hash=None,  # Google users don't have passwords
            phone_number=None,   # Can be added later
            is_active=True
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        return user


# Global instance
google_auth_service = GoogleAuthService()
