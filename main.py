from fastapi import FastAPI
from app.routes import flashcards
from app.routes.users import router as users_router
from app.routes.reviews import router as reviews_router
from app.routes.admin import router as admin_router
from app.routes.sms import router as sms_router
from fastapi.middleware.cors import CORSMiddleware

from app.routes.profile import router as profile_router

from app.routes.natural_flashcards import router as natural_flashcard_router
from app.routes.decks import router as decks_router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Or ["*"] during dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(flashcards.router, prefix="/flashcards", tags=["Flashcards"])

app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(reviews_router, prefix="/reviews", tags=["Reviews"])

app.include_router(admin_router, prefix="/admin", tags=["Admin"])
app.include_router(sms_router, prefix="/sms", tags=["SMS"])

app.include_router(profile_router, prefix="/users", tags=["Profile"])
app.include_router(natural_flashcard_router, prefix="/natural_flashcards", tags=["Natural_Flashcards"])
app.include_router(decks_router, prefix="/decks", tags=["Decks"])
