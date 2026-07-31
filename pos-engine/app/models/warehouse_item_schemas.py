from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal


class WarehouseItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Name of the warehouse item")
    sku: Optional[str] = Field(None, max_length=100, description="Unique SKU code")
    unit_of_measure: str = Field(..., min_length=1, max_length=50, description="Unit of measure (e.g., kg, liters, pcs)")
    minimum_stock: Decimal = Field(default=Decimal("0.000"), ge=Decimal("0.000"), description="Minimum stock threshold")


class WarehouseItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Name of the warehouse item")
    sku: Optional[str] = Field(None, max_length=100, description="Unique SKU code")
    unit_of_measure: Optional[str] = Field(None, min_length=1, max_length=50, description="Unit of measure")
    minimum_stock: Optional[Decimal] = Field(None, ge=Decimal("0.000"), description="Minimum stock threshold")


class WarehouseItemResponse(BaseModel):
    id: int
    name: str
    sku: Optional[str] = None
    unit_of_measure: str
    minimum_stock: Decimal

    class Config:
        from_attributes = True


class WarehouseItemDeleteResponse(BaseModel):
    message: str
    item_id: int
