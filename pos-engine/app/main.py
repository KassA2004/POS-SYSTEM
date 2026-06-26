from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    #everything here executes before the application starts
    print("starting pos engine...") 
    await init_db()
    yield 
    # here everything executes when system shuts down
    print("pos engine shutting down...")

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return{"message":"pos engine is running"}

