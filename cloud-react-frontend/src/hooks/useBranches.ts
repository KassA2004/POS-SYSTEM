import { useCallback, useState } from 'react';
import { branchesApi } from '@/services/resources';
import { extractErrorMessage } from '@/services/api';
import { useResource } from './useResource';
import { useToast } from './useToast';
import type { Branch, BranchCreate } from '@/types/domain';

const EMPTY: Branch[] = [];

export interface BranchFormState {
  name: string;
  address: string;
  is_active: boolean;
}

export const emptyBranchForm: BranchFormState = { name: '', address: '', is_active: true };

/**
 * Owns everything the Branches page needs: the list, the drawer/dialog state and
 * the mutations. The page and its child components read from this rather than
 * threading a dozen props through.
 */
export function useBranches() {
  const loader = useCallback(() => branchesApi.list(), []);
  const { data: branches, loading, error, reload } = useResource<Branch[]>(loader, EMPTY);
  const { toast } = useToast();

  const [drawerOpen, setDrawerOpen] = useState(false);
  const [editing, setEditing] = useState<Branch | null>(null);
  const [form, setForm] = useState<BranchFormState>(emptyBranchForm);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  const [deleteTarget, setDeleteTarget] = useState<Branch | null>(null);
  const [deleting, setDeleting] = useState(false);

  const openCreate = () => {
    setEditing(null);
    setForm(emptyBranchForm);
    setFormError(null);
    setDrawerOpen(true);
  };

  const openEdit = (branch: Branch) => {
    setEditing(branch);
    setForm({ name: branch.name, address: branch.address, is_active: branch.is_active });
    setFormError(null);
    setDrawerOpen(true);
  };

  const closeDrawer = () => {
    setDrawerOpen(false);
    setEditing(null);
  };

  const updateForm = (patch: Partial<BranchFormState>) => setForm((prev) => ({ ...prev, ...patch }));

  const save = async () => {
    if (!form.name.trim() || !form.address.trim()) {
      setFormError('Name and address are both required.');
      return;
    }

    setSaving(true);
    setFormError(null);
    try {
      const payload: BranchCreate = {
        name: form.name.trim(),
        address: form.address.trim(),
        is_active: form.is_active,
      };

      if (editing) {
        await branchesApi.update(editing.id, payload);
        toast(`Branch "${payload.name}" updated.`);
      } else {
        await branchesApi.create(payload);
        toast(`Branch "${payload.name}" created.`);
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
      await branchesApi.remove(deleteTarget.id);
      toast(`Branch "${deleteTarget.name}" deleted.`);
      setDeleteTarget(null);
      await reload();
    } catch (err) {
      toast(extractErrorMessage(err), 'danger');
    } finally {
      setDeleting(false);
    }
  };

  return {
    branches,
    loading,
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
    updateForm,
    save,
    deleteTarget,
    setDeleteTarget,
    deleting,
    confirmDelete,
  };
}

export default useBranches;
