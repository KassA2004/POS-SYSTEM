from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.db.models.tenant_models import Product, WarehouseItem, ProductRecipe
from app.models.product_schemas import (
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    ProductDetailResponse,
    ProductDeleteResponse,
)
from app.models.product_recipe_schemas import ProductRecipeResponse


async def get_products_service(
    db: AsyncSession,
) -> List[ProductResponse]:
    """
    Retrieves all products in the active tenant schema.
    """
    result = await db.execute(select(Product).order_by(Product.id.asc()))
    products = result.scalars().all()
    return [ProductResponse.model_validate(p) for p in products]


async def get_product_by_id_service(
    db: AsyncSession,
    product_id: int,
) -> ProductDetailResponse:
    """
    Retrieves a single product by ID in the active tenant schema, including recipe breakdown if applicable.
    """
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found.",
        )

    recipes = []
    if product.is_recipe:
        recipe_result = await db.execute(
            select(ProductRecipe)
            .where(ProductRecipe.product_id == product_id)
            .order_by(ProductRecipe.id.asc())
        )
        recipe_records = recipe_result.scalars().all()
        recipes = [ProductRecipeResponse.model_validate(r) for r in recipe_records]

    return ProductDetailResponse(
        id=product.id,
        name=product.name,
        price=product.price,
        is_recipe=product.is_recipe,
        direct_warehouse_item_id=product.direct_warehouse_item_id,
        is_active=product.is_active,
        created_at=product.created_at,
        recipes=recipes,
    )



async def create_product_service(
    db: AsyncSession,
    data: ProductCreate,
) -> ProductResponse:
    """
    Creates a new product record in the active tenant schema.
    """
    if data.direct_warehouse_item_id is not None:
        item_result = await db.execute(
            select(WarehouseItem.id).where(WarehouseItem.id == data.direct_warehouse_item_id)
        )
        if not item_result.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Direct warehouse item with ID {data.direct_warehouse_item_id} not found.",
            )

    new_product = Product(
        name=data.name,
        price=data.price,
        is_recipe=data.is_recipe,
        direct_warehouse_item_id=data.direct_warehouse_item_id,
        is_active=data.is_active,
    )
    db.add(new_product)

    try:
        await db.flush()
        await db.refresh(new_product)
        return ProductResponse(
            id=new_product.id,
            name=new_product.name,
            price=new_product.price,
            is_recipe=new_product.is_recipe,
            direct_warehouse_item_id=new_product.direct_warehouse_item_id,
            is_active=new_product.is_active,
            created_at=new_product.created_at,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create product: {str(e)}",
        )


async def update_product_service(
    db: AsyncSession,
    product_id: int,
    data: ProductUpdate,
) -> ProductResponse:
    """
    Updates an existing product record in the active tenant schema.
    """
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found.",
        )

    update_data = data.model_dump(exclude_unset=True)
    if not update_data:
        return ProductResponse(
            id=product.id,
            name=product.name,
            price=product.price,
            is_recipe=product.is_recipe,
            direct_warehouse_item_id=product.direct_warehouse_item_id,
            is_active=product.is_active,
            created_at=product.created_at,
        )

    if "direct_warehouse_item_id" in update_data and update_data["direct_warehouse_item_id"] is not None:
        item_result = await db.execute(
            select(WarehouseItem.id).where(WarehouseItem.id == update_data["direct_warehouse_item_id"])
        )
        if not item_result.first():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Direct warehouse item with ID {update_data['direct_warehouse_item_id']} not found.",
            )

    for field, value in update_data.items():
        setattr(product, field, value)

    try:
        await db.flush()
        await db.refresh(product)
        return ProductResponse(
            id=product.id,
            name=product.name,
            price=product.price,
            is_recipe=product.is_recipe,
            direct_warehouse_item_id=product.direct_warehouse_item_id,
            is_active=product.is_active,
            created_at=product.created_at,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update product: {str(e)}",
        )


async def delete_product_service(
    db: AsyncSession,
    product_id: int,
) -> ProductDeleteResponse:
    """
    Deletes a product record from the active tenant schema.
    """
    result = await db.execute(select(Product).where(Product.id == product_id))
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found.",
        )

    try:
        await db.delete(product)
        await db.flush()
        return ProductDeleteResponse(
            message=f"Product {product_id} deleted successfully.",
            product_id=product_id,
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete product {product_id} because active order records exist referencing this product.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete product: {str(e)}",
        )
