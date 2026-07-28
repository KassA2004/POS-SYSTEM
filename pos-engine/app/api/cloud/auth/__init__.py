from fastapi import APIRouter
from app.api.cloud.auth.registration import router as registration_router
from app.api.cloud.auth.login import router as login_router

router = APIRouter(prefix="/auth", tags=["Authentication"])
router.include_router(registration_router)
router.include_router(login_router)
