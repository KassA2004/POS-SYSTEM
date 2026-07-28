import os
import json
from fastapi import APIRouter, Depends, HTTPException, Request, Header
from app.models.auth_schemas import TenantRegistrationRequest, TenantRegistrationResponse
from app.db.database import get_db_connection
from app.services.tenant_service import activate_tenant_and_create_schema
from app.services.stripe_service import create_checkout_session, construct_event
from app.core.security import hash_password
import asyncpg

router = APIRouter()


@router.post("/register", response_model=TenantRegistrationResponse)
async def register_tenant(
    request: TenantRegistrationRequest,
    conn: asyncpg.Connection = Depends(get_db_connection),
):
    clean_schema_name = "schema_" + request.company_name.lower().replace(" ", "_").replace("-", "_")
    hashed_pw = hash_password(request.password)

    try:
        # Insert tenant with state = 0 (pending)
        tenant_query = """
            INSERT INTO tenants (name, schema_name, state)
            VALUES ($1, $2, 0)
            RETURNING id;
        """
        tenant_record = await conn.fetchrow(
            tenant_query, request.company_name, clean_schema_name
        )
        new_tenant_id = tenant_record["id"]

        # Insert tenant owner
        user_query = """
            INSERT INTO users (tenant_id, email, password_hash, role)
            VALUES ($1, $2, $3, 'TENANT_OWNER');
        """
        await conn.execute(user_query, new_tenant_id, request.email, hashed_pw)

        # Create Stripe Checkout Session
        stripe_session = create_checkout_session(
            tenant_id=new_tenant_id,
            company_name=request.company_name,
            email=request.email,
        )

        session_id = stripe_session["session_id"]
        checkout_url = stripe_session["checkout_url"]

        # Update tenant record with payment_session_id
        await conn.execute(
            "UPDATE tenants SET payment_session_id = $1 WHERE id = $2;",
            session_id,
            new_tenant_id,
        )

        # Note: CREATE SCHEMA is intentionally NOT run here. It will run upon successful payment.

        return TenantRegistrationResponse(
            tenant_id=new_tenant_id,
            company_name=request.company_name,
            schema_name=clean_schema_name,
            state=0,
            checkout_url=checkout_url,
            session_id=session_id,
            message="Registration pending payment. Please complete payment via Stripe to activate tenant schema.",
        )

    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(
            status_code=400, detail="This email or business name is already registered."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stripe-webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature"),
    conn: asyncpg.Connection = Depends(get_db_connection),
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
        # Fallback to parsing raw payload JSON when secret isn't configured in test/dev
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
            res = await activate_tenant_and_create_schema(conn, tenant_id=tenant_id, session_id=session_id)
            return {"status": "success", "tenant": res}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to activate tenant schema: {e}")

    return {"status": "ignored", "event_type": event_type}


@router.post("/verify-payment/{session_id}")
@router.get("/payment-success")
async def verify_payment(
    session_id: str,
    conn: asyncpg.Connection = Depends(get_db_connection),
):
    """
    Verifies payment and activates tenant / creates schema for a given Stripe session ID.
    Enables instant activation verification in test environments.
    """
    try:
        result = await activate_tenant_and_create_schema(conn, session_id=session_id)
        return {
            "status": "success",
            "message": "Payment verified. Tenant schema created and state updated to active (1).",
            "tenant": result,
        }
    except ValueError as e:
        raise HTTPException(status_code=444 if "not found" in str(e).lower() else 400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process payment activation: {e}")
