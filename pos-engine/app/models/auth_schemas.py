from pydantic import BaseModel, EmailStr, Field

class TenantRegistrationRequest(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=255, description="Name of THE business")
    email: EmailStr = Field(..., description="email of the tenant owner")
    password: str = Field(..., min_length=8, description="raw password to be hashed")

class TenantRegistrationResponse(BaseModel):
    tenant_id: int
    company_name: str
    schema_name: str
    message: str

        