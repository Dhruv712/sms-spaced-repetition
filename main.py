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

# Run database setup on startup
try:
    from create_tables import recreate_database
    recreate_database()
    print("Database setup completed successfully")
except Exception as e:
    print(f"Database setup error: {e}")

app = FastAPI()

# Create uploads directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)

# Mount static files for uploaded images
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Get allowed origins from environment or use defaults
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,https://hopeful-adventure-production.up.railway.app").split(",")

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
