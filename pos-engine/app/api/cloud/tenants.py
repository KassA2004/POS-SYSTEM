from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.tenant_schemas import TenantOut
from app.db.database import get_db
from app.db.models.cloud_models import Tenant

router = APIRouter(prefix="/tenants", tags=["Tenant Management"])


@router.get("/", response_model=List[TenantOut])
async def get_all_tenants(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(
            select(Tenant).order_by(Tenant.id.desc())
        )
        tenants = result.scalars().all()
        return [
            TenantOut(
                id=t.id,
                name=t.name,
                schema_name=t.schema_name,
                state=t.state,
                created_at=t.created_at,
            )
            for t in tenants
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
