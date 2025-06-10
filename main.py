from fastapi import FastAPI
from app.routes import flashcards
from app.routes.users import router as users_router
from app.routes.reviews import router as reviews_router
from app.routes.admin import router as admin_router
from app.routes.sms import router as sms_router
from fastapi.middleware.cors import CORSMiddleware




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
