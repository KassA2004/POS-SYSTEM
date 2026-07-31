from pydantic import BaseModel, Field
from typing import List, Optional


class PermissionOut(BaseModel):
    id: int
    code: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class RoleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Role name")
    permission_ids: List[int] = Field(..., min_length=1, description="List of permission IDs (at least 1 required)")


class RoleUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="Role name")
    permission_ids: Optional[List[int]] = Field(None, min_length=1, description="List of permission IDs (at least 1 required if provided)")


class RoleResponse(BaseModel):
    id: int
    name: str
    permissions: List[PermissionOut]

    class Config:
        from_attributes = True


class RoleDeleteResponse(BaseModel):
    message: str
    role_id: int
