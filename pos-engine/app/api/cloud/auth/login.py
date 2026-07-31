from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
import asyncpg
from app.db.database import get_db_connection
from app.models.auth_schemas import Token
from app.services.auth_services import authenticate_user_service

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    conn: asyncpg.Connection = Depends(get_db_connection),
):
    """
    OAuth2 compatible token login.
    Authenticates user with username (email) and password, then returns a JWT token.
    """
    return await authenticate_user_service(
        conn=conn,
        email=form_data.username,
        password=form_data.password,
    )
