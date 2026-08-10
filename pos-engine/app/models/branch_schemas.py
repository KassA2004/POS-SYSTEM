from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class BranchCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Name of the branch")
    address: str = Field(..., min_length=1, description="Physical address of the branch")
    is_active: bool = Field(True, description="Whether the branch is active")

class BranchUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Name of the branch")
    address: Optional[str] = Field(None, min_length=1, description="Physical address of the branch")
    is_active: Optional[bool] = Field(None, description="Whether the branch is active")


class BranchResponse(BaseModel):
    id: int
    name: str
    address: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class BranchDeleteResponse(BaseModel):
    message: str
    branch_id: int
