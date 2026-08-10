from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.database import create_db_pool, close_db_pool 
from app.api.cloud import auth, tenants, branches, employees, roles, branch_employees, warehouse_items, products, reports

from app.api.pos import inventory_warehouse, shifts, orders as pos_orders
from app.api.pos import auth as pos_auth
from app.api.pos import cash as pos_cash


@asynccontextmanager
async def lifespan(app: FastAPI):
    print('Starting connection to db')
    await create_db_pool()
    

    yield
    await close_db_pool()

    print("shutting down the server")

app = FastAPI(title="POS enterprise API", lifespan=lifespan)
app.include_router(auth.router)
app.include_router(tenants.router)
app.include_router(branches.router)
app.include_router(employees.router)
app.include_router(roles.router)
app.include_router(branch_employees.router)
app.include_router(warehouse_items.router)
app.include_router(products.router)
app.include_router(inventory_warehouse.router)
app.include_router(shifts.router)
app.include_router(pos_auth.router)
app.include_router(pos_cash.router)
app.include_router(pos_orders.router)
app.include_router(reports.router)



@app.get("/")
async def root():
    return {"message": "POS system is now running"}