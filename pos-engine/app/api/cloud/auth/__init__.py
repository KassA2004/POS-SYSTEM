from fastapi import APIRouter
from app.api.cloud.auth.registration import router as registration_router
from app.api.cloud.auth.login import router as login_router
from app.api.cloud.auth.session import router as session_router

router = APIRouter(prefix="/auth", tags=["Authentication"])
router.include_router(registration_router)
router.include_router(login_router)
router.include_router(session_router)
