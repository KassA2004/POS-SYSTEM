import asyncpg
from typing import List
from fastapi import HTTPException, status
from app.models.role_schemas import RoleCreate, RoleUpdate, RoleResponse, PermissionOut, RoleDeleteResponse


async def _validate_permission_ids(conn: asyncpg.Connection, permission_ids: List[int]):
    """
    Validates that all requested permission_ids exist in the database.
    """
    unique_ids = list(set(permission_ids))
    query = "SELECT id FROM permissions WHERE id = ANY($1::int[]);"
    existing_rows = await conn.fetch(query, unique_ids)
    existing_ids = {row["id"] for row in existing_rows}

    missing_ids = set(unique_ids) - existing_ids
    if missing_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid permission IDs provided: {sorted(list(missing_ids))}",
        )


async def _fetch_role_with_permissions(conn: asyncpg.Connection, role_id: int) -> RoleResponse:
    """
    Helper to query role and associated permissions and assemble RoleResponse.
    """
    role_row = await conn.fetchrow("SELECT id, name FROM roles WHERE id = $1;", role_id)
    if not role_row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with ID {role_id} not found.",
        )

    perm_query = """
        SELECT p.id, p.code, p.description
        FROM permissions p
        JOIN role_permissions rp ON p.id = rp.permission_id
        WHERE rp.role_id = $1
        ORDER BY p.id ASC;
    """
    perm_rows = await conn.fetch(perm_query, role_id)
    permissions = [PermissionOut(**dict(r)) for r in perm_rows]

    return RoleResponse(
        id=role_row["id"],
        name=role_row["name"],
        permissions=permissions,
    )


async def create_role_service(
    conn: asyncpg.Connection,
    data: RoleCreate,
) -> RoleResponse:
    """
    Creates a new role with assigned permissions inside an atomic transaction.
    """
    # 1. Enforce business rule: at least 1 permission required
    if not data.permission_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A role must be assigned at least one valid permission.",
        )

    # 2. Validate that all permission_ids exist
    await _validate_permission_ids(conn, data.permission_ids)

    # 3. Atomic creation inside a database transaction
    async with conn.transaction():
        # Insert role
        role_row = await conn.fetchrow(
            "INSERT INTO roles (name) VALUES ($1) RETURNING id;",
            data.name,
        )
        new_role_id = role_row["id"]

        # Insert role permissions
        unique_perm_ids = list(set(data.permission_ids))
        insert_rp_query = """
            INSERT INTO role_permissions (role_id, permission_id)
            SELECT $1, unnest($2::int[]);
        """
        await conn.execute(insert_rp_query, new_role_id, unique_perm_ids)

    # 4. Fetch and return created role object
    return await _fetch_role_with_permissions(conn, new_role_id)


async def update_role_service(
    conn: asyncpg.Connection,
    role_id: int,
    data: RoleUpdate,
) -> RoleResponse:
    """
    Updates a role name and/or permissions, ensuring at least 1 permission is maintained.
    """
    # 1. Verify existence
    existing = await conn.fetchrow("SELECT id FROM roles WHERE id = $1;", role_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with ID {role_id} not found.",
        )

    if data.name is None and data.permission_ids is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one field (name or permission_ids) must be provided for update.",
        )

    # 2. If permission_ids supplied, enforce min_length >= 1 & validate validity
    if data.permission_ids is not None:
        if len(data.permission_ids) < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A role must maintain at least one valid permission.",
            )
        await _validate_permission_ids(conn, data.permission_ids)

    # 3. Perform atomic update
    async with conn.transaction():
        if data.name is not None:
            await conn.execute("UPDATE roles SET name = $1 WHERE id = $2;", data.name, role_id)

        if data.permission_ids is not None:
            # Delete old permissions and insert new permissions
            await conn.execute("DELETE FROM role_permissions WHERE role_id = $1;", role_id)
            unique_perm_ids = list(set(data.permission_ids))
            insert_rp_query = """
                INSERT INTO role_permissions (role_id, permission_id)
                SELECT $1, unnest($2::int[]);
            """
            await conn.execute(insert_rp_query, role_id, unique_perm_ids)

    # 4. Fetch and return updated role object
    return await _fetch_role_with_permissions(conn, role_id)


async def delete_role_service(
    conn: asyncpg.Connection,
    role_id: int,
) -> RoleDeleteResponse:
    """
    Deletes a role if not assigned to any active employee in branch_employees.
    """
    # 1. Verify existence
    existing = await conn.fetchrow("SELECT id FROM roles WHERE id = $1;", role_id)
    if not existing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with ID {role_id} not found.",
        )

    # 2. Check active assignment in branch_employees
    active_assignment = await conn.fetchrow(
        "SELECT id FROM branch_employees WHERE role_id = $1 AND removed_at IS NULL LIMIT 1;",
        role_id,
    )
    if active_assignment:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot delete role {role_id}: it is currently assigned to an active employee in branch_employees.",
        )

    # 3. Delete role (cascades to role_permissions)
    try:
        await conn.execute("DELETE FROM roles WHERE id = $1;", role_id)
        return RoleDeleteResponse(
            message=f"Role {role_id} deleted successfully.",
            role_id=role_id,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete role: {str(e)}",
        )
