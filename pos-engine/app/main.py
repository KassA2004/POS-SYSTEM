from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.database import create_db_pool, close_db_pool 

@asynccontextmanager
async def lifespan(app: FastAPI):
    print('Starting connection to db')
    await create_db_pool()

    yield
    await close_db_pool()

    print("shutting down the server")

app = FastAPI(title="POS enterprise API", lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "POS system is now running"}