from fastapi import APIRouter, Depends, status
from app.models.pos_auth_schemas import POSLoginRequest, POSLoginResponse, POSLogoutResponse
from app.services.pos_auth_service import pos_login_service, pos_logout_service
from app.api.dependencies import get_current_employee

router = APIRouter(prefix="/pos/auth", tags=["POS Authentication"])


@router.post("/login", response_model=POSLoginResponse, status_code=status.HTTP_200_OK)
async def pos_login(request: POSLoginRequest):
    """
    Authenticates a POS terminal user (employee) using their numeric ID and PIN.

    The client must also supply the `branch_id` where this terminal operates and
    the `schema_name` of the tenant. On success a short-lived JWT is returned that
    encodes `employee_id`, `branch_id`, `schema_name`, `role`, and `permissions`.
    """
    return await pos_login_service(request)


@router.post("/logout", response_model=POSLogoutResponse)
async def pos_logout(current_employee: dict = Depends(get_current_employee)):
    """
    Terminates a POS terminal session.

    JWT-based auth is stateless — the client must discard the token. This endpoint
    exists for logging / audit purposes and confirms the session has ended.
    """
    return await pos_logout_service()
