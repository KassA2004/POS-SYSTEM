from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from app.models.product_recipe_schemas import ProductRecipeResponse


class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Name of the product")
    price: Decimal = Field(..., ge=Decimal("0.00"), description="Product price")
    is_recipe: bool = Field(default=False, description="True if product composition uses a recipe")
    direct_warehouse_item_id: Optional[int] = Field(None, description="Linked direct warehouse item ID if not a recipe")
    is_active: bool = Field(default=True, description="Product active status")


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Name of the product")
    price: Optional[Decimal] = Field(None, ge=Decimal("0.00"), description="Product price")
    is_recipe: Optional[bool] = Field(None, description="True if product composition uses a recipe")
    direct_warehouse_item_id: Optional[int] = Field(None, description="Linked direct warehouse item ID")
    is_active: Optional[bool] = Field(None, description="Product active status")


class ProductResponse(BaseModel):
    id: int
    name: str
    price: Decimal
    is_recipe: bool
    direct_warehouse_item_id: Optional[int] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ProductDetailResponse(ProductResponse):
    recipes: List[ProductRecipeResponse] = []



class ProductDeleteResponse(BaseModel):
    message: str
    product_id: int
