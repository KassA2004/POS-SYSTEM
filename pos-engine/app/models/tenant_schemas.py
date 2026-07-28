from pydantic import BaseModel
from datetime import datetime 

class TenantOut(BaseModel):
    id: int
    name: str
    schema_name: str    
    state: int
    created_at: datetime

    class Config:
        from_attributes = True