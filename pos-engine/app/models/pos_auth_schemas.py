from pydantic import BaseModel, Field
from typing import Optional


class POSLoginRequest(BaseModel):
    employee_id: int = Field(..., description="Numeric employee ID")
    pin: str = Field(..., min_length=4, max_length=8, pattern=r'^\d+$', description="Numeric PIN (4-8 digits)")
    branch_id: int = Field(..., description="Branch ID where this POS terminal is located")
    schema_name: str = Field(..., description="Tenant schema name (e.g. 'tenant_1')")


class POSLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    employee_id: int
    employee_name: str
    branch_id: int
    role: Optional[str] = None


class POSLogoutResponse(BaseModel):
    message: str
