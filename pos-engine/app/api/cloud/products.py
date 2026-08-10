from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.cloud.auth.dependencies import require_schema_owner, get_scoped_db
from app.models.product_schemas import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductDetailResponse,
    ProductDeleteResponse,
)
from app.models.product_recipe_schemas import (
    ProductRecipeCreate,
    ProductRecipeUpdate,
    ProductRecipeResponse,
    ProductRecipeDeleteResponse,
)
from app.services.product_service import (
    create_product_service,
    get_products_service,
    get_product_by_id_service,
    update_product_service,
    delete_product_service,
)
from app.services.product_recipe_service import (
    create_product_recipe_service,
    update_product_recipe_service,
    delete_product_recipe_service,
)

router = APIRouter(prefix="/products", tags=["Cloud Product & Recipe Management"])


# --- Products Endpoints ---

@router.get("/", response_model=List[ProductResponse])
async def get_products(
    current_user: dict = Depends(require_schema_owner),
    db: AsyncSession = Depends(get_scoped_db),
):
    """
    Retrieves all product records from the tenant schema.
    Only accessible by schema owners (TENANT_OWNER / SUPER_ADMIN).
    """
    return await get_products_service(db)


@router.get("/{product_id}", response_model=ProductDetailResponse)
async def get_product_by_id(
    product_id: int,
    current_user: dict = Depends(require_schema_owner),
    db: AsyncSession = Depends(get_scoped_db),
):
    """
    Retrieves a single product record by ID from the tenant schema, including recipe ingredients if applicable.
    Only accessible by schema owners (TENANT_OWNER / SUPER_ADMIN).
    """
    return await get_product_by_id_service(db, product_id)


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)

async def create_product(
    data: ProductCreate,
    current_user: dict = Depends(require_schema_owner),
    db: AsyncSession = Depends(get_scoped_db),
):
    """
    Creates a new product record in the tenant schema.
    Only accessible by schema owners (TENANT_OWNER / SUPER_ADMIN).
    """
    return await create_product_service(db, data)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    data: ProductUpdate,
    current_user: dict = Depends(require_schema_owner),
    db: AsyncSession = Depends(get_scoped_db),
):
    """
    Updates an existing product record by ID in the tenant schema.
    Only accessible by schema owners (TENANT_OWNER / SUPER_ADMIN).
    """
    return await update_product_service(db, product_id, data)


@router.delete("/{product_id}", response_model=ProductDeleteResponse)
async def delete_product(
    product_id: int,
    current_user: dict = Depends(require_schema_owner),
    db: AsyncSession = Depends(get_scoped_db),
):
    """
    Deletes a product record by ID from the tenant schema.
    Only accessible by schema owners (TENANT_OWNER / SUPER_ADMIN).
    """
    return await delete_product_service(db, product_id)


# --- Product Recipes Endpoints ---

@router.post("/{product_id}/recipes", response_model=ProductRecipeResponse, status_code=status.HTTP_201_CREATED)
async def create_product_recipe(
    product_id: int,
    data: ProductRecipeCreate,
    current_user: dict = Depends(require_schema_owner),
    db: AsyncSession = Depends(get_scoped_db),
):
    """
    Adds a recipe ingredient component to a product.
    Only accessible by schema owners (TENANT_OWNER / SUPER_ADMIN).
    """
    return await create_product_recipe_service(db, product_id, data)


@router.put("/{product_id}/recipes/{recipe_id}", response_model=ProductRecipeResponse)
async def update_product_recipe(
    product_id: int,
    recipe_id: int,
    data: ProductRecipeUpdate,
    current_user: dict = Depends(require_schema_owner),
    db: AsyncSession = Depends(get_scoped_db),
):
    """
    Updates a recipe ingredient component for a product.
    Only accessible by schema owners (TENANT_OWNER / SUPER_ADMIN).
    """
    return await update_product_recipe_service(db, product_id, recipe_id, data)


@router.delete("/{product_id}/recipes/{recipe_id}", response_model=ProductRecipeDeleteResponse)
async def delete_product_recipe(
    product_id: int,
    recipe_id: int,
    current_user: dict = Depends(require_schema_owner),
    db: AsyncSession = Depends(get_scoped_db),
):
    """
    Deletes a recipe ingredient component from a product.
    Only accessible by schema owners (TENANT_OWNER / SUPER_ADMIN).
    """
    return await delete_product_recipe_service(db, product_id, recipe_id)
