from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional

class InventoryWarehouseBase(BaseModel):
    quantity: Decimal = Field(default=0, max_digits=12, decimal_places=3, description="Current stock quantity")

class InventoryWarehouseCreate(InventoryWarehouseBase):
    warehouse_item_id: int

class InventoryWarehouseUpdate(BaseModel):
    quantity: Decimal = Field(..., max_digits=12, decimal_places=3, description="New stock quantity")

class InventoryWarehouseResponse(InventoryWarehouseCreate):
    class Config:
        from_attributes = True