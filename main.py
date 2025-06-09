from fastapi import FastAPI
from app.routes import flashcards
from app.routes.users import router as users_router

app = FastAPI()
app.include_router(flashcards.router, prefix="/flashcards", tags=["Flashcards"])

app.include_router(users_router, prefix="/users", tags=["Users"])