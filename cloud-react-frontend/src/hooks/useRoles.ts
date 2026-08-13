import { useCallback, useMemo, useState } from 'react';
import { rolesApi } from '@/services/resources';
import { extractErrorMessage } from '@/services/api';
import { useResource } from './useResource';
import { useToast } from './useToast';
import { permissionDomain } from '@/lib/format';
import type { Permission, Role } from '@/types/domain';

const EMPTY_ROLES: Role[] = [];
const EMPTY_PERMISSIONS: Permission[] = [];

export interface RoleFormState {
  name: string;
  permissionIds: number[];
}

export const emptyRoleForm: RoleFormState = { name: '', permissionIds: [] };

export function useRoles() {
  const rolesLoader = useCallback(() => rolesApi.list(), []);
  const permissionsLoader = useCallback(() => rolesApi.permissions(), []);

  const { data: roles, loading, error, reload } = useResource<Role[]>(rolesLoader, EMPTY_ROLES);
  const { data: permissions, loading: permissionsLoading } = useResource<Permission[]>(
    permissionsLoader,
    EMPTY_PERMISSIONS
  );
  const { toast } = useToast();

  const [drawerOpen, setDrawerOpen] = useState(false);
  const [editing, setEditing] = useState<Role | null>(null);
  const [form, setForm] = useState<RoleFormState>(emptyRoleForm);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const [deleteTarget, setDeleteTarget] = useState<Role | null>(null);
  const [deleting, setDeleting] = useState(false);

  /** Permissions grouped by their `domain.action` prefix, for a scannable picker. */
  const permissionGroups = useMemo(() => {
    const groups = new Map<string, Permission[]>();
    for (const permission of permissions) {
      const domain = permissionDomain(permission.code);
      const bucket = groups.get(domain);
      if (bucket) bucket.push(permission);
      else groups.set(domain, [permission]);
    }
    return Array.from(groups.entries()).sort((a, b) => a[0].localeCompare(b[0]));
  }, [permissions]);

  const openCreate = () => {
    setEditing(null);
    setForm(emptyRoleForm);
    setFormError(null);
    setDrawerOpen(true);
  };

  const openEdit = (role: Role) => {
    setEditing(role);
    setForm({ name: role.name, permissionIds: role.permissions.map((p) => p.id) });
    setFormError(null);
    setDrawerOpen(true);
  };

  const closeDrawer = () => {
    setDrawerOpen(false);
    setEditing(null);
  };

  const setName = (name: string) => setForm((prev) => ({ ...prev, name }));

  const togglePermission = (id: number) =>
    setForm((prev) => ({
      ...prev,
      permissionIds: prev.permissionIds.includes(id)
        ? prev.permissionIds.filter((p) => p !== id)
        : [...prev.permissionIds, id],
    }));

  const toggleDomain = (domain: string) => {
    const domainIds = permissions.filter((p) => permissionDomain(p.code) === domain).map((p) => p.id);
    setForm((prev) => {
      const allSelected = domainIds.every((id) => prev.permissionIds.includes(id));
      return {
        ...prev,
        permissionIds: allSelected
          ? prev.permissionIds.filter((id) => !domainIds.includes(id))
          : Array.from(new Set([...prev.permissionIds, ...domainIds])),
      };
    });
  };

  const save = async () => {
    if (!form.name.trim()) {
      setFormError('Role name is required.');
      return;
    }
    // The backend enforces min_length=1 on permission_ids; catch it here so the
    // user gets a useful message instead of a raw 422.
    if (form.permissionIds.length === 0) {
      setFormError('Select at least one permission. A role with no permissions cannot be created.');
      return;
    }

    setSaving(true);
    setFormError(null);
    try {
      if (editing) {
        await rolesApi.update(editing.id, { name: form.name.trim(), permission_ids: form.permissionIds });
        toast(`Role "${form.name.trim()}" updated.`);
      } else {
        await rolesApi.create({ name: form.name.trim(), permission_ids: form.permissionIds });
        toast(`Role "${form.name.trim()}" created.`);
      }
      closeDrawer();
      await reload();
    } catch (err) {
      setFormError(extractErrorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  const confirmDelete = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await rolesApi.remove(deleteTarget.id);
      toast(`Role "${deleteTarget.name}" deleted.`);
      setDeleteTarget(null);
      await reload();
    } catch (err) {
      toast(extractErrorMessage(err), 'danger');
    } finally {
      setDeleting(false);
    }
  };

  return {
    roles,
    permissions,
    permissionGroups,
    loading,
    permissionsLoading,
    error,
    reload,
    drawerOpen,
    editing,
    form,
    saving,
    formError,
    openCreate,
    openEdit,
    closeDrawer,
    setName,
    togglePermission,
    toggleDomain,
    save,
    deleteTarget,
    setDeleteTarget,
    deleting,
    confirmDelete,
  };
}

export default useRoles;
