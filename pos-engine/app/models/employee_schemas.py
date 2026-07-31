from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional


class EmployeeCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Name of the employee")
    date_of_birth: Optional[date] = Field(None, description="Date of birth")
    phone: Optional[str] = Field(None, max_length=50, description="Phone number")


class EmployeeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Name of the employee")
    date_of_birth: Optional[date] = Field(None, description="Date of birth")
    phone: Optional[str] = Field(None, max_length=50, description="Phone number")


class EmployeeResponse(BaseModel):
    id: int
    name: str
    date_of_birth: Optional[date] = None
    phone: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class EmployeeDeleteResponse(BaseModel):
    message: str
    employee_id: int
