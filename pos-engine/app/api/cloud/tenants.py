from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.models.tenant_schemas import TenantOut
from app.db.database import get_db_connection
import asyncpg

router = APIRouter(prefix="/tenants", tags=["Tenant Management"])

@router.get("/", response_model = List[TenantOut])
async def get_all_tenants(conn: asyncpg.Connection = Depends(get_db_connection)):
    try:
        query = """SELECT id, name, schema_name, state, created_at
        FROM tenants
        ORDER BY id DESC;
        """
        all_tenants = await conn.fetch(query)
        return [dict(tenant) for tenant in all_tenants]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
