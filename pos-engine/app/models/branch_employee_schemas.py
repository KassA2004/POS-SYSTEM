from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class BranchEmployeeAssignRequest(BaseModel):
    employee_id: int = Field(..., description="ID of the employee to assign")
    role_id: Optional[int] = Field(None, description="Optional ID of the role assigned to the employee at this branch")


class BranchEmployeeUpdateRequest(BaseModel):
    role_id: Optional[int] = Field(None, description="Updated role ID")
    branch_id: Optional[int] = Field(None, description="Updated branch ID")


class BranchEmployeeResponse(BaseModel):
    id: int
    employee_id: int
    branch_id: int
    role_id: Optional[int] = None
    assigned_at: datetime
    removed_at: Optional[datetime] = None

    employee_name: Optional[str] = None
    branch_name: Optional[str] = None
    role_name: Optional[str] = None

    class Config:
        from_attributes = True


class BranchEmployeeDeleteResponse(BaseModel):
    message: str
    id: int
    removed_at: datetime
