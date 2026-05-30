import { computed, ref } from 'vue';
import { roleHomePath, roleLabels, type UserRole } from '../config/roles';

const STORAGE_KEY = 'edumind.currentRole';
const availableRoles: UserRole[] = ['student', 'teacher', 'admin'];

function readInitialRole(): UserRole {
  const stored = localStorage.getItem(STORAGE_KEY) as UserRole | null;
  return stored && availableRoles.includes(stored) ? stored : 'student';
}

const currentRole = ref<UserRole>(readInitialRole());

export function useRole() {
  const currentRoleLabel = computed(() => roleLabels[currentRole.value]);
  const currentHomePath = computed(() => roleHomePath[currentRole.value]);

  function setRole(role: UserRole) {
    currentRole.value = role;
    localStorage.setItem(STORAGE_KEY, role);
  }

  return {
    availableRoles,
    currentRole,
    currentRoleLabel,
    currentHomePath,
    roleLabels,
    setRole
  };
}
