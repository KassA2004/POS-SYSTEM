from fastapi import FastAPI, HTTPException, status 
from pydantic import BaseModel
from app.database import init_db_pool, close_db_pool, get_db_pool

app = FastAPI(title="Enterprise POS Engine")

@app.on_event("startup")
async def startup():
    await init_db_pool()

@app.on_event("shutdown")
async def shutdown():
    await close_db_pool()

class CheckoutRequest(BaseModel):
    tenat_id: int
    product_id: int 
    quantity_to_buy: int


@app.post("/checkout")
async def checkout(payload: CheckoutRequest):
    async with get_db_connection() as conn:

        async with conn.transaction():

            row = await conn.fetchrow(
                """
                SELECT quanitity 
                FROM inventory_warehouse
                Where tenant_id = $1 AND product_id = $2
                FOR UPDATE;
                """
                payload.tenant_id,payload.product_id
            )

if not row:
    raise HTTPException(
        status_code=status.HTTP_444_NOT_FOUND,
        detail="product not found in warehouse inventory."

    )

    current_stock = row['quantity']
    
    if current_stock < payload.quantity_to_buy:
        raise HTTPException(
            status_code= status.HTTP_409_CONFLICT,
            detail=f"Insolvent inventory. Requested: {payload.quantity_to_buy}, Available: {current_stock}"
        )
            