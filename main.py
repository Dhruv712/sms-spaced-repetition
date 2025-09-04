from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
from app.routes import flashcards
from app.routes.users import router as users_router
from app.routes.reviews import router as reviews_router
from app.routes.admin import router as admin_router
from app.routes.sms import router as sms_router
from app.routes.auth import router as auth_router

from app.routes.profile import router as profile_router

from app.routes.natural_flashcards import router as natural_flashcard_router
from app.routes.decks import router as decks_router
from app.routes.loop_test import router as loop_test_router
from app.routes.loop_webhook import router as loop_webhook_router

# Safe database setup - only create tables if they don't exist
try:
    from app.database import engine
    from app.models import Base
    # Only create tables if they don't exist - don't drop existing data
    Base.metadata.create_all(bind=engine)
    print("Database tables created/verified successfully")
except Exception as e:
    print(f"Database setup error: {e}")
    raise e  # Re-raise the exception to prevent startup with broken DB

app = FastAPI(redirect_slashes=False)

# Create uploads directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)

# Mount static files for uploaded images
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

"""CORS configuration

We accept a comma-separated list of origins from the ALLOWED_ORIGINS env var.
Whitespace around items is stripped to avoid subtle mismatches that would
cause CORS failures (e.g., " https://trycue.xyz").
"""
allowed_origins_raw = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,https://hopeful-adventure-production.up.railway.app,https://sms-spaced-repetition-production.up.railway.app,https://trycue.xyz",
)
allowed_origins = [origin.strip() for origin in allowed_origins_raw.split(",") if origin.strip()]

print(f"Allowed origins: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(flashcards.router, prefix="/flashcards", tags=["Flashcards"])

app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(reviews_router, prefix="/reviews", tags=["Reviews"])

app.include_router(admin_router, prefix="/admin", tags=["Admin"])
app.include_router(sms_router, prefix="/sms", tags=["SMS"])
app.include_router(auth_router, prefix="/auth", tags=["Auth"])

app.include_router(profile_router, prefix="/users", tags=["Profile"])
app.include_router(natural_flashcard_router, prefix="/natural_flashcards", tags=["Natural_Flashcards"])
app.include_router(decks_router, prefix="/decks", tags=["Decks"])
app.include_router(loop_test_router, prefix="/loop-test", tags=["Loop_Test"])
app.include_router(loop_webhook_router, prefix="/loop-webhook", tags=["Loop_Webhook"])
