import { computed, ref } from 'vue';
import { useRoute } from 'vue-router';
import { roleFromPath, roleHomePath, roleLabels, type UserRole } from '../config/roles';

const STORAGE_KEY = 'edumind.demoRole';
const LEGACY_STORAGE_KEY = 'edumind.currentRole';
const DEMO_USER_KEY = 'edumind.demoUserId';
const availableRoles: UserRole[] = ['student', 'teacher', 'admin'];

export const demoStudents = [
  { id: 'demo-basic', label: '张同学｜基础补弱型', shortName: '张同学', profileType: '基础补弱型' },
  { id: 'demo-advanced', label: '李同学｜项目提升型', shortName: '李同学', profileType: '项目提升型' },
  { id: 'demo-exam', label: '王同学｜考试冲刺型', shortName: '王同学', profileType: '考试冲刺型' }
];

export function demoStudentLabel(userId: string) {
  return demoStudents.find((item) => item.id === userId)?.label || '张同学｜基础补弱型';
}

function readInitialRole(): UserRole {
  const stored = (localStorage.getItem(STORAGE_KEY) || localStorage.getItem(LEGACY_STORAGE_KEY)) as UserRole | null;
  return stored && availableRoles.includes(stored) ? stored : 'student';
}

const storedRole = ref<UserRole>(readInitialRole());
const demoUserId = ref(localStorage.getItem(DEMO_USER_KEY) || 'demo-basic');

export function useRole() {
  const route = useRoute();
  const currentRole = computed<UserRole>(() => roleFromPath(route.path) || storedRole.value);
  const currentRoleLabel = computed(() => roleLabels[currentRole.value]);
  const currentHomePath = computed(() => roleHomePath[currentRole.value]);
  const demoUserLabel = computed(() => demoStudentLabel(demoUserId.value));

  function setRole(role: UserRole) {
    storedRole.value = role;
    localStorage.setItem(STORAGE_KEY, role);
  }

  function setDemoUserId(userId: string) {
    demoUserId.value = userId;
    localStorage.setItem(DEMO_USER_KEY, userId);
  }

  function clearRole() {
    storedRole.value = 'student';
    demoUserId.value = 'demo-basic';
    localStorage.removeItem(STORAGE_KEY);
    localStorage.removeItem(LEGACY_STORAGE_KEY);
    localStorage.removeItem(DEMO_USER_KEY);
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
