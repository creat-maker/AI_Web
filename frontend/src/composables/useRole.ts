import { computed, ref } from 'vue';
import { useRoute } from 'vue-router';
import { roleFromPath, roleHomePath, roleLabels, type UserRole } from '../config/roles';

const ROLE_KEY = 'edumind.demoRole';
const LEGACY_ROLE_KEY = 'edumind.currentRole';
const USER_ID_KEY = 'edumind.demoUserId';
const TOKEN_KEY = 'edumind.accessToken';

export const availableRoles: UserRole[] = ['student', 'teacher', 'admin'];

export const demoStudents = [
  { id: '1', label: '李明 - Python 循环结构专项提升', shortName: '李明', profileType: '基础薄弱 + 代码实践偏好' },
  { id: '2', label: '陈浩 - 项目实践提升', shortName: '陈浩', profileType: '项目实践提升' },
  { id: '3', label: '王悦 - 考试冲刺', shortName: '王悦', profileType: '考试冲刺' }
];

export function readStoredRole(): UserRole | null {
  const stored = (localStorage.getItem(ROLE_KEY) || localStorage.getItem(LEGACY_ROLE_KEY)) as UserRole | null;
  return stored && availableRoles.includes(stored) ? stored : null;
}

export function hasDemoSession() {
  return Boolean(localStorage.getItem(TOKEN_KEY) || readStoredRole());
}

export function demoStudentLabel(userId: string) {
  return demoStudents.find((item) => item.id === userId)?.label || demoStudents[0].label;
}

const storedRole = ref<UserRole>(readStoredRole() || 'student');
const demoUserId = ref(localStorage.getItem(USER_ID_KEY) || '1');

export function useRole() {
  const route = useRoute();
  const currentRole = computed<UserRole>(() => roleFromPath(route.path) || storedRole.value);
  const currentRoleLabel = computed(() => roleLabels[currentRole.value]);
  const currentHomePath = computed(() => roleHomePath[currentRole.value]);
  const demoUserLabel = computed(() => demoStudentLabel(demoUserId.value));

  function setRole(role: UserRole | null | undefined) {
    if (!role || !availableRoles.includes(role)) return false;
    storedRole.value = role;
    localStorage.setItem(ROLE_KEY, role);
    localStorage.setItem(LEGACY_ROLE_KEY, role);
    return true;
  }

  function setDemoUserId(userId: string) {
    demoUserId.value = userId;
    localStorage.setItem(USER_ID_KEY, userId);
  }

  function clearRole() {
    storedRole.value = 'student';
    demoUserId.value = '1';
    localStorage.removeItem(ROLE_KEY);
    localStorage.removeItem(LEGACY_ROLE_KEY);
    localStorage.removeItem(USER_ID_KEY);
    localStorage.removeItem(TOKEN_KEY);
  }

  return {
    availableRoles,
    currentRole,
    currentRoleLabel,
    currentHomePath,
    demoUserId,
    demoUserLabel,
    demoStudents,
    roleLabels,
    clearRole,
    setDemoUserId,
    setRole
  };
}
