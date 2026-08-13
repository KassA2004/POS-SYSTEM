import { Store, UserMinus, TriangleAlert } from 'lucide-react';
import { Drawer } from '@/globalComponents/Drawer';
import { Button } from '@/globalComponents/Button';
import { FormField } from '@/globalComponents/Input';
import { Select } from '@/globalComponents/Select';
import { Alert } from '@/globalComponents/Alert';
import { EmptyState } from '@/globalComponents/EmptyState';
import type { useEmployees } from '@/hooks/useEmployees';

export interface EmployeeAssignmentDrawerProps {
  state: ReturnType<typeof useEmployees>;
}

export function EmployeeAssignmentDrawer({ state }: EmployeeAssignmentDrawerProps) {
  const {
    assignTarget,
    targetAssignments,
    branches,
    roles,
    assignBranchId,
    setAssignBranchId,
    assignRoleId,
    setAssignRoleId,
    assigning,
    assignError,
    closeAssign,
    submitAssignment,
    removeAssignment,
    changeAssignmentRole,
  } = state;

  // An employee may hold only one role per branch, so branches they are already
  // active at must not be offered again - the API would reject it with a 409.
  const assignedBranchIds = new Set(targetAssignments.map((a) => a.branch_id));
  const availableBranches = branches.filter((b) => !assignedBranchIds.has(b.id));

  return (
    <Drawer
      open={assignTarget !== null}
      onClose={closeAssign}
      width="md"
      title="Branch assignments"
      description={assignTarget ? `Where ${assignTarget.name} works and the role they hold there.` : undefined}
      footer={
        <Button variant="secondary" onClick={closeAssign}>
          Done
        </Button>
      }
    >
      <div className="space-y-6">
        {assignError && <Alert variant="danger">{assignError}</Alert>}

        <section className="space-y-3">
          <h3 className="text-caption font-medium text-ink-secondary">Current assignments</h3>

          {targetAssignments.length === 0 ? (
            <div className="border border-border-subtle rounded-lg">
              <EmptyState
                icon={<Store size={24} strokeWidth={1.5} />}
                title="Not assigned anywhere"
                message="Assign this employee to a branch below so they can open shifts there."
              />
            </div>
          ) : (
            <ul className="space-y-2">
              {targetAssignments.map((assignment) => (
                <li
                  key={assignment.id}
                  className="flex items-center gap-3 border border-border-subtle rounded-lg p-3 bg-surface"
                >
                  <div className="min-w-0 flex-1">
                    <p className="text-body font-medium text-ink-primary truncate">{assignment.branch_name}</p>
                    {!assignment.role_name && (
                      <p className="flex items-center gap-1 text-caption text-warning-fg mt-0.5">
                        <TriangleAlert size={14} strokeWidth={2} aria-hidden="true" />
                        No role — cannot sign in at this branch
                      </p>
                    )}
                  </div>

                  <div className="w-40 shrink-0">
                    <Select
                      aria-label={`Role at ${assignment.branch_name}`}
                      value={assignment.role_id ?? ''}
                      placeholder="No role"
                      options={roles.map((r) => ({ value: r.id, label: r.name }))}
                      onChange={(e) =>
                        changeAssignmentRole(assignment.id, e.target.value ? Number(e.target.value) : null)
                      }
                    />
                  </div>

                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeAssignment(assignment.id)}
                    aria-label={`Remove from ${assignment.branch_name}`}
                    className="shrink-0 hover:text-danger-fg hover:bg-danger-bg"
                  >
                    <UserMinus size={16} strokeWidth={1.5} />
                  </Button>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="space-y-4 border-t border-border-subtle pt-6">
          <h3 className="text-caption font-medium text-ink-secondary">Assign to a branch</h3>

          {branches.length === 0 ? (
            <Alert variant="info">Create a branch first — there is nowhere to assign this employee yet.</Alert>
          ) : availableBranches.length === 0 ? (
            <Alert variant="info">This employee is already assigned to every branch.</Alert>
          ) : (
            <div className="space-y-4">
              <FormField label="Branch" required>
                <Select
                  value={assignBranchId}
                  onChange={(e) => setAssignBranchId(e.target.value)}
                  placeholder="Choose a branch"
                  options={availableBranches.map((b) => ({ value: b.id, label: b.name }))}
                />
              </FormField>

              <FormField
                label="Role at this branch"
                hint={
                  roles.length === 0
                    ? 'No roles exist yet. You can assign one later from this panel.'
                    : 'Each employee holds exactly one role per branch.'
                }
              >
                <Select
                  value={assignRoleId}
                  onChange={(e) => setAssignRoleId(e.target.value)}
                  placeholder={roles.length === 0 ? 'No roles available' : 'Choose a role'}
                  options={roles.map((r) => ({ value: r.id, label: r.name }))}
                  disabled={roles.length === 0}
                />
              </FormField>

              <Button variant="primary" onClick={submitAssignment} loading={assigning} className="w-full">
                Assign to branch
              </Button>
            </div>
          )}
        </section>
      </div>
    </Drawer>
  );
}

export default EmployeeAssignmentDrawer;
