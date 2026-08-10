from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.db.models.tenant_models import Role, Permission, RolePermission, BranchEmployee
from app.models.role_schemas import RoleCreate, RoleUpdate, RoleResponse, PermissionOut, RoleDeleteResponse


async def _validate_permission_ids(db: AsyncSession, permission_ids: List[int]):
    """
    Validates that all requested permission_ids exist in the database.
    """
    unique_ids = list(set(permission_ids))
    result = await db.execute(select(Permission.id).where(Permission.id.in_(unique_ids)))
    existing_ids = {row[0] for row in result.all()}

    missing_ids = set(unique_ids) - existing_ids
    if missing_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid permission IDs provided: {sorted(list(missing_ids))}",
        )


async def _fetch_role_with_permissions(db: AsyncSession, role_id: int) -> RoleResponse:
    """
    Helper to query role and associated permissions and assemble RoleResponse.
    """
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with ID {role_id} not found.",
        )

    perm_result = await db.execute(
        select(Permission)
        .join(RolePermission, Permission.id == RolePermission.permission_id)
        .where(RolePermission.role_id == role_id)
        .order_by(Permission.id.asc())
    )
    permissions = [
        PermissionOut(id=p.id, code=p.code, description=p.description)
        for p in perm_result.scalars().all()
    ]

    return RoleResponse(id=role.id, name=role.name, permissions=permissions)


async def get_roles_service(
    db: AsyncSession,
) -> List[RoleResponse]:
    """
    Retrieves all roles with their assigned permissions in the tenant schema.
    """
    result = await db.execute(select(Role).order_by(Role.id.asc()))
    roles = result.scalars().all()

    role_responses = []
    for role in roles:
        role_resp = await _fetch_role_with_permissions(db, role.id)
        role_responses.append(role_resp)

    return role_responses


async def get_role_by_id_service(
    db: AsyncSession,
    role_id: int,
) -> RoleResponse:
    """
    Retrieves a single role by ID with its permissions in the tenant schema.
    """
    return await _fetch_role_with_permissions(db, role_id)


async def get_all_permissions_service(
    db: AsyncSession,
) -> List[PermissionOut]:
    """
    Retrieves all available permissions in the system permissions registry.
    """
    result = await db.execute(select(Permission).order_by(Permission.id.asc()))
    perms = result.scalars().all()
    return [PermissionOut.model_validate(p) for p in perms]



async def create_role_service(
    db: AsyncSession,
    data: RoleCreate,
) -> RoleResponse:
    """
    Creates a new role with assigned permissions inside an atomic transaction.
    """
    if not data.permission_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A role must be assigned at least one valid permission.",
        )

    await _validate_permission_ids(db, data.permission_ids)

    new_role = Role(name=data.name)
    db.add(new_role)
    await db.flush()  # generate role id

    unique_perm_ids = list(set(data.permission_ids))
    for perm_id in unique_perm_ids:
        db.add(RolePermission(role_id=new_role.id, permission_id=perm_id))

    await db.flush()

    return await _fetch_role_with_permissions(db, new_role.id)


async def update_role_service(
    db: AsyncSession,
    role_id: int,
    data: RoleUpdate,
) -> RoleResponse:
    """
    Updates a role name and/or permissions, ensuring at least 1 permission is maintained.
    """
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with ID {role_id} not found.",
        )

    if data.name is None and data.permission_ids is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field (name or permission_ids) must be provided for update.",
        )

    if data.permission_ids is not None:
        if len(data.permission_ids) < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A role must maintain at least one valid permission.",
            )
        await _validate_permission_ids(db, data.permission_ids)

    if data.name is not None:
        role.name = data.name

    if data.permission_ids is not None:
        # Delete all existing role-permission mappings, then re-insert
        await db.execute(delete(RolePermission).where(RolePermission.role_id == role_id))
        unique_perm_ids = list(set(data.permission_ids))
        for perm_id in unique_perm_ids:
            db.add(RolePermission(role_id=role_id, permission_id=perm_id))

    await db.flush()

    return await _fetch_role_with_permissions(db, role_id)


async def delete_role_service(
    db: AsyncSession,
    role_id: int,
) -> RoleDeleteResponse:
    """
    Deletes a role if not assigned to any active employee in branch_employees.
    """
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()

    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with ID {role_id} not found.",
        )

    # Check for active branch_employee assignment
    active_result = await db.execute(
        select(BranchEmployee.id)
        .where(BranchEmployee.role_id == role_id, BranchEmployee.removed_at.is_(None))
        .limit(1)
    )
    if active_result.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot delete role {role_id}: it is currently assigned to an active employee in branch_employees.",
        )

    try:
        await db.delete(role)
        await db.flush()
        return RoleDeleteResponse(
            message=f"Role {role_id} deleted successfully.",
            role_id=role_id,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete role: {str(e)}",
        )
