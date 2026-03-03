from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.documents import router as documents_router
from app.api.forms import router as forms_router

api_router = APIRouter(prefix="/api")

api_router.include_router(auth_router)
api_router.include_router(documents_router)
api_router.include_router(forms_router)

__all__ = ["api_router"]
