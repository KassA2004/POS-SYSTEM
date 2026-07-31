from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal


class ProductRecipeCreate(BaseModel):
    warehouse_item_id: int = Field(..., description="ID of the warehouse item ingredient")
    quantity_required: Decimal = Field(..., gt=Decimal("0.000"), description="Quantity required per product unit")


class ProductRecipeUpdate(BaseModel):
    warehouse_item_id: Optional[int] = Field(None, description="ID of the warehouse item ingredient")
    quantity_required: Optional[Decimal] = Field(None, gt=Decimal("0.000"), description="Quantity required per product unit")


class ProductRecipeResponse(BaseModel):
    id: int
    product_id: int
    warehouse_item_id: int
    quantity_required: Decimal

    class Config:
        from_attributes = True


class ProductRecipeDeleteResponse(BaseModel):
    message: str
    recipe_id: int
    product_id: int
