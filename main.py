from fastapi import FastAPI
from app.routes import flashcards
from app.routes.users import router as users_router
from app.routes.reviews import router as reviews_router
from app.routes.admin import router as admin_router
from app.routes.sms import router as sms_router




app = FastAPI()
app.include_router(flashcards.router, prefix="/flashcards", tags=["Flashcards"])

app.include_router(users_router, prefix="/users", tags=["Users"])
app.include_router(reviews_router, prefix="/reviews", tags=["Reviews"])

app.include_router(admin_router, prefix="/admin", tags=["Admin"])
app.include_router(sms_router, prefix="/sms", tags=["SMS"])
