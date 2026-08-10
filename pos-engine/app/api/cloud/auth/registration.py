import os
import json
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.auth_schemas import TenantRegistrationRequest, TenantRegistrationResponse
from app.db.database import get_db
from app.services.auth_services import register_tenant_service
from app.services.tenant_service import activate_tenant_and_create_schema
from app.services.stripe_service import construct_event

router = APIRouter()


@router.post("/register", response_model=TenantRegistrationResponse)
async def register_tenant(
    request: TenantRegistrationRequest,
    db: AsyncSession = Depends(get_db),
):
    return await register_tenant_service(db, request)


@router.post("/stripe-webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature"),
    db: AsyncSession = Depends(get_db),
):
    """
    Stripe Webhook handler:
    Listens for checkout.session.completed event and activates tenant & creates schema.
    """
    payload = await request.body()
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")

    event = None
    if webhook_secret and stripe_signature:
        try:
            event = construct_event(payload, stripe_signature, webhook_secret)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Webhook signature verification failed: {e}")
    else:
        try:
            event = json.loads(payload.decode("utf-8"))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid payload format: {e}")

    event_type = event.get("type") if isinstance(event, dict) else getattr(event, "type", None)

    if event_type == "checkout.session.completed":
        session_obj = event.get("data", {}).get("object", {}) if isinstance(event, dict) else event.data.object
        session_id = session_obj.get("id") if isinstance(session_obj, dict) else getattr(session_obj, "id", None)
        client_ref_id = session_obj.get("client_reference_id") if isinstance(session_obj, dict) else getattr(session_obj, "client_reference_id", None)

        tenant_id = int(client_ref_id) if client_ref_id and client_ref_id.isdigit() else None

        try:
            res = await activate_tenant_and_create_schema(db, tenant_id=tenant_id, session_id=session_id)
            return {"status": "success", "tenant": res}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to activate tenant schema: {e}")

    return {"status": "ignored", "event_type": event_type}


@router.post("/verify-payment/{session_id}")
@router.get("/payment-success")
async def verify_payment(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Verifies payment and activates tenant / creates schema for a given Stripe session ID.
    Enables instant activation verification in test environments.
    """
    try:
        result = await activate_tenant_and_create_schema(db, session_id=session_id)
        return {
            "status": "success",
            "message": "Payment verified. Tenant schema created and state updated to active (1).",
            "tenant": result,
        }
    except ValueError as e:
        raise HTTPException(status_code=444 if "not found" in str(e).lower() else 400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process payment activation: {e}")
