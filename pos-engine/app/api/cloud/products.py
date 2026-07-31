from fastapi import APIRouter, Depends, status
import asyncpg
from app.db.database import get_db_connection
from app.api.cloud.auth.dependencies import require_schema_owner
from app.models.product_schemas import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
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

@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    data: ProductCreate,
    current_user: dict = Depends(require_schema_owner),
    conn: asyncpg.Connection = Depends(get_db_connection),
):
    """
    Creates a new product record in the tenant schema.
    Only accessible by schema owners (TENANT_OWNER / SUPER_ADMIN).
    """
    return await create_product_service(conn, data)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    data: ProductUpdate,
    current_user: dict = Depends(require_schema_owner),
    conn: asyncpg.Connection = Depends(get_db_connection),
):
    """
    Updates an existing product record by ID in the tenant schema.
    Only accessible by schema owners (TENANT_OWNER / SUPER_ADMIN).
    """
    return await update_product_service(conn, product_id, data)


@router.delete("/{product_id}", response_model=ProductDeleteResponse)
async def delete_product(
    product_id: int,
    current_user: dict = Depends(require_schema_owner),
    conn: asyncpg.Connection = Depends(get_db_connection),
):
    """
    Deletes a product record by ID from the tenant schema.
    Only accessible by schema owners (TENANT_OWNER / SUPER_ADMIN).
    """
    return await delete_product_service(conn, product_id)


# --- Product Recipes Endpoints ---

@router.post("/{product_id}/recipes", response_model=ProductRecipeResponse, status_code=status.HTTP_201_CREATED)
async def create_product_recipe(
    product_id: int,
    data: ProductRecipeCreate,
    current_user: dict = Depends(require_schema_owner),
    conn: asyncpg.Connection = Depends(get_db_connection),
):
    """
    Adds a recipe ingredient component to a product.
    Only accessible by schema owners (TENANT_OWNER / SUPER_ADMIN).
    """
    return await create_product_recipe_service(conn, product_id, data)


@router.put("/{product_id}/recipes/{recipe_id}", response_model=ProductRecipeResponse)
async def update_product_recipe(
    product_id: int,
    recipe_id: int,
    data: ProductRecipeUpdate,
    current_user: dict = Depends(require_schema_owner),
    conn: asyncpg.Connection = Depends(get_db_connection),
):
    """
    Updates a recipe ingredient component for a product.
    Only accessible by schema owners (TENANT_OWNER / SUPER_ADMIN).
    """
    return await update_product_recipe_service(conn, product_id, recipe_id, data)


@router.delete("/{product_id}/recipes/{recipe_id}", response_model=ProductRecipeDeleteResponse)
async def delete_product_recipe(
    product_id: int,
    recipe_id: int,
    current_user: dict = Depends(require_schema_owner),
    conn: asyncpg.Connection = Depends(get_db_connection),
):
    """
    Deletes a recipe ingredient component from a product.
    Only accessible by schema owners (TENANT_OWNER / SUPER_ADMIN).
    """
    return await delete_product_recipe_service(conn, product_id, recipe_id)
