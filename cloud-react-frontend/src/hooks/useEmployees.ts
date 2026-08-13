import { useCallback, useMemo, useState } from 'react';
import { assignmentsApi, branchesApi, employeesApi, rolesApi } from '@/services/resources';
import { extractErrorMessage } from '@/services/api';
import { useResource } from './useResource';
import { useToast } from './useToast';
import type { Branch, BranchEmployee, Employee, EmployeeCreate, Role } from '@/types/domain';

const EMPTY_EMPLOYEES: Employee[] = [];
const EMPTY_ASSIGNMENTS: BranchEmployee[] = [];
const EMPTY_BRANCHES: Branch[] = [];
const EMPTY_ROLES: Role[] = [];

export interface EmployeeFormState {
  name: string;
  phone: string;
  date_of_birth: string;
  pin: string;
}

export const emptyEmployeeForm: EmployeeFormState = { name: '', phone: '', date_of_birth: '', pin: '' };

export function useEmployees() {
  const employeesLoader = useCallback(() => employeesApi.list(), []);
  const assignmentsLoader = useCallback(() => assignmentsApi.list(), []);
  const branchesLoader = useCallback(() => branchesApi.list(), []);
  const rolesLoader = useCallback(() => rolesApi.list(), []);

  const { data: employees, loading, error, reload } = useResource<Employee[]>(employeesLoader, EMPTY_EMPLOYEES);
  const {
    data: assignments,
    loading: assignmentsLoading,
    reload: reloadAssignments,
  } = useResource<BranchEmployee[]>(assignmentsLoader, EMPTY_ASSIGNMENTS);
  const { data: branches } = useResource<Branch[]>(branchesLoader, EMPTY_BRANCHES);
  const { data: roles } = useResource<Role[]>(rolesLoader, EMPTY_ROLES);
  const { toast } = useToast();

  // --- employee form ---
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [editing, setEditing] = useState<Employee | null>(null);
  const [form, setForm] = useState<EmployeeFormState>(emptyEmployeeForm);
  const [saving, setSaving] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);

  // --- assignment panel ---
  const [assignTarget, setAssignTarget] = useState<Employee | null>(null);
  const [assignBranchId, setAssignBranchId] = useState<string>('');
  const [assignRoleId, setAssignRoleId] = useState<string>('');
  const [assigning, setAssigning] = useState(false);
  const [assignError, setAssignError] = useState<string | null>(null);

  const [deleteTarget, setDeleteTarget] = useState<Employee | null>(null);
  const [deleting, setDeleting] = useState(false);

  /** employee_id -> their active assignments, for the table's Branches column. */
  const assignmentsByEmployee = useMemo(() => {
    const map = new Map<number, BranchEmployee[]>();
    for (const assignment of assignments) {
      const bucket = map.get(assignment.employee_id);
      if (bucket) bucket.push(assignment);
      else map.set(assignment.employee_id, [assignment]);
    }
    return map;
  }, [assignments]);

  const targetAssignments = assignTarget ? (assignmentsByEmployee.get(assignTarget.id) ?? []) : [];

  const openCreate = () => {
    setEditing(null);
    setForm(emptyEmployeeForm);
    setFormError(null);
    setDrawerOpen(true);
  };

  const openEdit = (employee: Employee) => {
    setEditing(employee);
    setForm({
      name: employee.name,
      phone: employee.phone ?? '',
      date_of_birth: employee.date_of_birth ?? '',
      pin: '',
    });
    setFormError(null);
    setDrawerOpen(true);
  };

  const closeDrawer = () => {
    setDrawerOpen(false);
    setEditing(null);
  };

  const updateForm = (patch: Partial<EmployeeFormState>) => setForm((prev) => ({ ...prev, ...patch }));

  const save = async () => {
    if (!form.name.trim()) {
      setFormError('Employee name is required.');
      return;
    }
    if (form.pin && !/^\d{4,8}$/.test(form.pin)) {
      setFormError('PIN must be 4 to 8 digits.');
      return;
    }

    setSaving(true);
    setFormError(null);
    try {
      // Omit blank optionals entirely rather than sending empty strings, which
      // would fail date/pattern validation on the backend.
      const payload: EmployeeCreate = { name: form.name.trim() };
      if (form.phone.trim()) payload.phone = form.phone.trim();
      if (form.date_of_birth) payload.date_of_birth = form.date_of_birth;
      if (form.pin) payload.pin = form.pin;

      if (editing) {
        await employeesApi.update(editing.id, payload);
        toast(`Employee "${payload.name}" updated.`);
      } else {
        await employeesApi.create(payload);
        toast(`Employee "${payload.name}" created.`);
      }
      closeDrawer();
      await reload();
    } catch (err) {
      setFormError(extractErrorMessage(err));
    } finally {
      setSaving(false);
    }
  };

  const openAssign = (employee: Employee) => {
    setAssignTarget(employee);
    setAssignBranchId('');
    setAssignRoleId('');
    setAssignError(null);
  };

  const closeAssign = () => setAssignTarget(null);

  const submitAssignment = async () => {
    if (!assignTarget) return;
    if (!assignBranchId) {
      setAssignError('Choose a branch.');
      return;
    }

    setAssigning(true);
    setAssignError(null);
    try {
      await assignmentsApi.assign(Number(assignBranchId), {
        employee_id: assignTarget.id,
        role_id: assignRoleId ? Number(assignRoleId) : null,
      });
      toast(`${assignTarget.name} assigned to branch.`);
      setAssignBranchId('');
      setAssignRoleId('');
      await reloadAssignments();
    } catch (err) {
      setAssignError(extractErrorMessage(err));
    } finally {
      setAssigning(false);
    }
  };

  const removeAssignment = async (assignmentId: number) => {
    try {
      await assignmentsApi.remove(assignmentId);
      toast('Assignment removed.');
      await reloadAssignments();
    } catch (err) {
      toast(extractErrorMessage(err), 'danger');
    }
  };

  const changeAssignmentRole = async (assignmentId: number, roleId: number | null) => {
    try {
      await assignmentsApi.update(assignmentId, { role_id: roleId });
      toast('Role updated for this branch.');
      await reloadAssignments();
    } catch (err) {
      toast(extractErrorMessage(err), 'danger');
    }
  };

  const confirmDelete = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await employeesApi.remove(deleteTarget.id);
      toast(`Employee "${deleteTarget.name}" deleted.`);
      setDeleteTarget(null);
      await Promise.all([reload(), reloadAssignments()]);
    } catch (err) {
      toast(extractErrorMessage(err), 'danger');
    } finally {
      setDeleting(false);
    }
  };

  return {
    employees,
    branches,
    roles,
    assignments,
    assignmentsByEmployee,
    loading,
    assignmentsLoading,
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

    assignTarget,
    targetAssignments,
    assignBranchId,
    setAssignBranchId,
    assignRoleId,
    setAssignRoleId,
    assigning,
    assignError,
    openAssign,
    closeAssign,
    submitAssignment,
    removeAssignment,
    changeAssignmentRole,

    deleteTarget,
    setDeleteTarget,
    deleting,
    confirmDelete,
  };
}

export default useEmployees;
