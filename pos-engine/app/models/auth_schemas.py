from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class TenantRegistrationRequest(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=255, description="Name of THE business")
    email: EmailStr = Field(..., description="email of the tenant owner")
    password: str = Field(..., min_length=8, description="raw password to be hashed")

class TenantRegistrationResponse(BaseModel):
    tenant_id: int
    company_name: str
    schema_name: str
    state: int = Field(0, description="0 = pending, 1 = active")
    checkout_url: Optional[str] = Field(None, description="Stripe checkout URL")
    session_id: Optional[str] = Field(None, description="Stripe checkout session ID")
    message: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None
    tenant_id: Optional[int] = None
    schema_name: Optional[str] = None
    role: Optional[str] = None


class CurrentUserResponse(BaseModel):
    """Session bootstrap payload returned by GET /auth/me."""
    id: int
    email: str
    role: str
    tenant_id: int
    schema_name: str
    tenant_name: Optional[str] = None