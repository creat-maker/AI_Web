<script setup lang="ts">
import { computed, reactive, ref } from 'vue';
import { RouterLink, useRoute, useRouter } from 'vue-router';
import { api } from '../api/client';
import { useRole } from '../composables/useRole';
import type { UserRole } from '../config/roles';

interface LoginResponse {
  access_token?: string;
  token?: string;
  role?: string;
  redirect?: string;
  user?: {
    id?: string;
    username?: string;
    role?: string;
    name?: string;
    display_name?: string;
    student_id?: string;
  };
  data?: any;
}

const router = useRouter();
const route = useRoute();
const { setDemoUserId, setRole } = useRole();

const roleCards: Array<{
  role: UserRole;
  label: string;
  title: string;
  description: string;
  username: string;
  userId: string;
  home: string;
  icon: string;
}> = [
  {
    role: 'student',
    label: '学生端',
    title: '个性化学习',
    description: '学习路径、资源推荐、智能答疑与学习报告。',
    username: 'student',
    userId: '1',
    home: '/student',
    icon: '学'
  },
  {
    role: 'teacher',
    label: '教师端',
    title: '教学工作台',
    description: '课程管理、资源生成、画像分析与学情报告。',
    username: 'teacher',
    userId: '2',
    home: '/teacher',
    icon: '教'
  },
  {
    role: 'admin',
    label: '管理员端',
    title: '平台治理',
    description: '资源治理、内容审核、用户角色与系统状态。',
    username: 'admin',
    userId: '3',
    home: '/dashboard',
    icon: '管'
  }
];

const workflow = ['画像诊断', '路径规划', '资源推荐', '智能辅导', '测验评价', '报告生成', '平台治理'];
const capabilities = [
  { title: '学生端', text: '个性化学习路径、资源推荐、智能答疑、学习报告', icon: 'S' },
  { title: '教师端', text: '课程管理、资源生成、画像分析、学情报告', icon: 'T' },
  { title: '管理员端', text: '资源治理、内容审核、用户角色、日志与系统状态', icon: 'A' }
];

const selectedRole = ref<UserRole>('student');
const loading = ref(false);
const error = ref('');
const form = reactive({
  username: 'student',
  password: '123456'
});

const selected = computed(() => roleCards.find((item) => item.role === selectedRole.value) || roleCards[0]);
const submitLabel = computed(() => (loading.value ? '正在进入...' : `进入${selected.value.label}`));

function isUserRole(role: unknown): role is UserRole {
  return role === 'student' || role === 'teacher' || role === 'admin';
}

function normalizeLoginResponse(raw: any) {
  const payload = raw?.data ?? raw ?? {};
  const nested = payload?.data ?? {};
  const user = payload?.user ?? nested?.user ?? {};
  const role = user?.role ?? payload?.role ?? nested?.role;
  const token = payload?.access_token ?? payload?.token ?? nested?.access_token ?? nested?.token;
  const redirect = payload?.redirect ?? nested?.redirect;
  return { token, role, user, redirect };
}

function defaultRedirect(role: UserRole) {
  if (role === 'teacher') return '/teacher';
  if (role === 'admin') return '/dashboard';
  return '/student';
}

function legalRedirect(role: UserRole, redirect: unknown) {
  if (typeof redirect !== 'string' || !redirect.startsWith('/')) return '';
  if (role === 'student' && redirect.startsWith('/student')) return redirect;
  if (
    role === 'teacher' &&
    (redirect === '/teacher' || redirect.startsWith('/teacher') || redirect === '/courses' || redirect === '/reports' || redirect === '/resource-generation')
  ) {
    return redirect;
  }
  if (role === 'admin' && (redirect === '/dashboard' || redirect.startsWith('/admin') || redirect === '/demo-status')) return redirect;
  return '';
}

function selectRole(role: UserRole) {
  const item = roleCards.find((card) => card.role === role);
  if (!item) return;
  selectedRole.value = item.role;
  form.username = item.username;
  form.password = '123456';
  error.value = '';
}

async function submitLogin() {
  if (!form.username.trim() || !form.password.trim()) {
    error.value = '请输入账号和密码。';
    return;
  }
  loading.value = true;
  error.value = '';
  try {
    const result = await api.post<LoginResponse>('/api/v1/auth/login', {
      username: form.username.trim(),
      password: form.password
    });
    const normalized = normalizeLoginResponse(result);
    if (!normalized.role) {
      error.value = '登录响应缺少角色信息，请检查登录接口。';
      return;
    }
    if (!isUserRole(normalized.role)) {
      error.value = '登录响应中的角色无效，请检查登录接口。';
      return;
    }
    if (!normalized.token) {
      error.value = '登录响应缺少访问令牌，请检查登录接口。';
      return;
    }

    const role = normalized.role;
    const matched = roleCards.find((item) => item.role === role) || selected.value;
    localStorage.setItem('edumind.accessToken', String(normalized.token));
    localStorage.setItem('edumind.user', JSON.stringify(normalized.user || {}));
    if (!setRole(role)) {
      error.value = '登录响应中的角色无效，请检查登录接口。';
      return;
    }
    const studentId = normalized.user?.student_id || matched.userId;
    setDemoUserId(studentId);
    if (role === 'student') localStorage.setItem('edumind.studentId', studentId);
    const redirect = legalRedirect(role, normalized.redirect) || legalRedirect(role, route.query.redirect) || defaultRedirect(role);
    await router.push(redirect);
  } catch (err) {
    error.value = err instanceof Error ? err.message : '登录失败，请检查账号和密码。';
  } finally {
    loading.value = false;
  }
}

async function quickLogin(role: UserRole) {
  selectRole(role);
  await submitLogin();
}
</script>

<template>
  <section class="login-page">
    <div class="ambient ambient-one"></div>
    <div class="ambient ambient-two"></div>

    <main class="login-shell">
      <section class="brand-panel">
        <div class="brand-topline">
          <div class="brand-logo">E</div>
          <div>
            <strong>EduMind Studio</strong>
            <span>面向学生、教师、管理员的教育智能体平台</span>
          </div>
        </div>

        <div class="hero-copy">
          <span class="eyebrow">Python 程序设计 / 循环结构</span>
          <h1>围绕 Python 循环结构的个性化教学闭环</h1>
          <p>聚合课程学习、资源生成、智能辅导、测评分析与报告治理，形成清晰可追踪的教学支持链路。</p>
        </div>

        <div class="workflow-strip" aria-label="核心业务链路">
          <span v-for="item in workflow" :key="item">{{ item }}</span>
        </div>

        <div class="feature-grid">
          <article v-for="item in capabilities" :key="item.title" class="feature-card">
            <span>{{ item.icon }}</span>
            <div>
              <strong>{{ item.title }}</strong>
              <p>{{ item.text }}</p>
            </div>
          </article>
        </div>
      </section>

      <section class="signin-card">
        <div class="signin-heading">
          <span>Welcome back</span>
          <h2>登录 EduMind Studio</h2>
          <p>选择角色快速进入，也可使用账号密码登录。</p>
        </div>

        <div class="role-selector">
          <button
            v-for="item in roleCards"
            :key="item.role"
            :class="['role-option', { active: selectedRole === item.role }]"
            type="button"
            @click="selectRole(item.role)"
          >
            <span>{{ item.icon }}</span>
            <strong>{{ item.label }}</strong>
            <small>{{ item.title }}</small>
          </button>
        </div>

        <form class="login-form" @submit.prevent="submitLogin">
          <label>
            <span>账号</span>
            <input v-model="form.username" autocomplete="username" placeholder="请输入账号" />
          </label>
          <label>
            <span>密码</span>
            <input v-model="form.password" autocomplete="current-password" placeholder="请输入密码" type="password" />
          </label>

          <p class="role-note">{{ selected.description }}</p>
          <p v-if="error" class="error-note">{{ error }}</p>

          <button class="primary-action" :disabled="loading" type="submit">{{ submitLabel }}</button>
        </form>

        <div class="quick-area">
          <div class="quick-row">
            <button v-for="item in roleCards" :key="item.role" :disabled="loading" type="button" @click="quickLogin(item.role)">
              {{ item.label }}快捷登录
            </button>
          </div>
          <div class="quick-row subtle">
            <RouterLink to="/demo-status">系统状态</RouterLink>
            <RouterLink to="/capability-boundary">平台能力</RouterLink>
          </div>
        </div>
      </section>
    </main>
  </section>
</template>

<style scoped>
.login-page {
  position: relative;
  min-height: 100vh;
  overflow: hidden;
  padding: 34px;
  background:
    radial-gradient(circle at 12% 10%, rgba(96, 165, 250, 0.22), transparent 28%),
    radial-gradient(circle at 86% 18%, rgba(167, 139, 250, 0.24), transparent 30%),
    linear-gradient(135deg, #f8fbff 0%, #eef6ff 45%, #f7f4ff 100%);
}

.ambient {
  position: absolute;
  border-radius: 999px;
  filter: blur(32px);
  opacity: 0.42;
  pointer-events: none;
}

.ambient-one {
  width: 260px;
  height: 260px;
  left: -70px;
  bottom: 10%;
  background: #93c5fd;
}

.ambient-two {
  width: 300px;
  height: 300px;
  right: 12%;
  top: -100px;
  background: #c4b5fd;
}

.login-shell {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: minmax(0, 1.34fr) minmax(390px, 0.96fr);
  gap: 28px;
  align-items: stretch;
  width: min(1180px, 100%);
  min-height: calc(100vh - 68px);
  margin: 0 auto;
}

.brand-panel,
.signin-card {
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 28px;
  background: rgba(255, 255, 255, 0.72);
  box-shadow: 0 26px 80px rgba(31, 41, 55, 0.12);
  backdrop-filter: blur(18px);
}

.brand-panel {
  display: grid;
  align-content: space-between;
  gap: 28px;
  padding: 34px;
}

.brand-topline,
.feature-card {
  display: flex;
  align-items: center;
  gap: 14px;
}

.brand-logo {
  display: grid;
  place-items: center;
  width: 52px;
  height: 52px;
  border-radius: 16px;
  color: #fff;
  background: linear-gradient(135deg, #2563eb, #7c3aed);
  font-size: 24px;
  font-weight: 900;
  box-shadow: 0 14px 30px rgba(37, 99, 235, 0.25);
}

.brand-topline strong {
  display: block;
  color: #172033;
  font-size: 20px;
  letter-spacing: 0;
}

.brand-topline span,
.signin-heading p,
.feature-card p,
.role-note {
  color: #64748b;
}

.hero-copy {
  max-width: 720px;
}

.eyebrow,
.signin-heading span {
  display: inline-flex;
  border: 1px solid rgba(37, 99, 235, 0.16);
  border-radius: 999px;
  padding: 7px 12px;
  color: #3156d4;
  background: rgba(239, 246, 255, 0.9);
  font-size: 12px;
  font-weight: 800;
}

.hero-copy h1 {
  max-width: 680px;
  margin: 20px 0 16px;
  color: #111827;
  font-size: clamp(34px, 4.4vw, 58px);
  line-height: 1.06;
  letter-spacing: 0;
}

.hero-copy p {
  max-width: 650px;
  margin: 0;
  color: #475569;
  font-size: 17px;
  line-height: 1.8;
}

.workflow-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.workflow-strip span {
  border: 1px solid rgba(37, 99, 235, 0.13);
  border-radius: 999px;
  padding: 9px 12px;
  color: #1d4ed8;
  background: rgba(255, 255, 255, 0.76);
  font-size: 13px;
  font-weight: 800;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.feature-card {
  min-height: 122px;
  align-items: flex-start;
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 18px;
  padding: 18px;
  background: rgba(255, 255, 255, 0.82);
  box-shadow: 0 18px 40px rgba(37, 99, 235, 0.08);
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}

.feature-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 24px 48px rgba(37, 99, 235, 0.13);
}

.feature-card > span {
  display: grid;
  flex: 0 0 auto;
  place-items: center;
  width: 34px;
  height: 34px;
  border-radius: 12px;
  color: #3156d4;
  background: #eef6ff;
  font-weight: 900;
}

.feature-card strong {
  display: block;
  margin-bottom: 7px;
  color: #1e293b;
}

.feature-card p {
  margin: 0;
  font-size: 13px;
  line-height: 1.65;
}

.signin-card {
  align-self: center;
  display: grid;
  gap: 22px;
  padding: 30px;
}

.signin-heading h2 {
  margin: 12px 0 8px;
  color: #111827;
  font-size: 30px;
  letter-spacing: 0;
}

.signin-heading p,
.role-note {
  margin: 0;
  line-height: 1.65;
}

.role-selector {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.role-option {
  display: grid;
  justify-items: start;
  gap: 7px;
  border: 1px solid #e2e8f0;
  border-radius: 18px;
  padding: 14px;
  text-align: left;
  color: #334155;
  background: #f8fafc;
  cursor: pointer;
  transition: border-color 0.18s ease, background 0.18s ease, box-shadow 0.18s ease, transform 0.18s ease;
}

.role-option:hover,
.role-option.active {
  border-color: rgba(37, 99, 235, 0.45);
  background: #fff;
  box-shadow: 0 14px 34px rgba(37, 99, 235, 0.14);
  transform: translateY(-1px);
}

.role-option span {
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  border-radius: 12px;
  color: #fff;
  background: linear-gradient(135deg, #2563eb, #7c3aed);
  font-weight: 900;
}

.role-option small {
  color: #64748b;
}

.login-form {
  display: grid;
  gap: 14px;
}

.login-form label {
  display: grid;
  gap: 8px;
  color: #334155;
  font-size: 13px;
  font-weight: 800;
}

.login-form input {
  width: 100%;
  height: 48px;
  border: 1px solid #dbe4f0;
  border-radius: 16px;
  padding: 0 15px;
  color: #111827;
  background: rgba(255, 255, 255, 0.92);
  transition: border-color 0.18s ease, box-shadow 0.18s ease;
}

.login-form input:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.12);
}

.error-note {
  margin: 0;
  border-radius: 14px;
  padding: 10px 12px;
  color: #b91c1c;
  background: #fef2f2;
  font-size: 13px;
  font-weight: 700;
}

.primary-action {
  height: 50px;
  border: 0;
  border-radius: 16px;
  color: #fff;
  background: linear-gradient(135deg, #2563eb, #4f46e5);
  box-shadow: 0 16px 34px rgba(37, 99, 235, 0.25);
  font-size: 16px;
  font-weight: 900;
}

.primary-action:disabled {
  cursor: not-allowed;
  opacity: 0.72;
}

.quick-area,
.quick-row {
  display: grid;
  gap: 10px;
}

.quick-row {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.quick-row button,
.quick-row a {
  border: 1px solid #dbe4f0;
  border-radius: 14px;
  padding: 11px 8px;
  color: #3156d4;
  background: #f8fbff;
  text-align: center;
  font-size: 13px;
  font-weight: 800;
  text-decoration: none;
}

.quick-row.subtle {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

@media (max-width: 1040px) {
  .login-page {
    padding: 22px;
  }

  .login-shell {
    grid-template-columns: 1fr;
  }

  .signin-card {
    align-self: stretch;
  }
}

@media (max-width: 720px) {
  .login-page {
    padding: 14px;
  }

  .brand-panel,
  .signin-card {
    border-radius: 22px;
    padding: 22px;
  }

  .feature-grid,
  .role-selector,
  .quick-row {
    grid-template-columns: 1fr;
  }
}

.login-page {
  padding: clamp(18px, 3vw, 38px);
  background:
    radial-gradient(circle at 78% 8%, rgba(124, 58, 237, 0.18), transparent 26%),
    radial-gradient(circle at 10% 88%, rgba(37, 99, 235, 0.18), transparent 28%),
    linear-gradient(145deg, #fbfdff 0%, #eef7ff 45%, #f8f5ff 100%);
}

.ambient {
  filter: blur(46px);
  opacity: 0.3;
}

.ambient-one {
  width: 360px;
  height: 360px;
  left: -120px;
  bottom: -80px;
  background: linear-gradient(135deg, #60a5fa, #a78bfa);
}

.ambient-two {
  width: 420px;
  height: 420px;
  right: -110px;
  top: -150px;
  background: linear-gradient(135deg, #bfdbfe, #ddd6fe);
}

.login-shell {
  width: min(1240px, 100%);
  min-height: calc(100vh - clamp(36px, 6vw, 76px));
  grid-template-columns: minmax(0, 1.22fr) minmax(420px, 0.86fr);
  gap: clamp(20px, 2.6vw, 34px);
  align-items: center;
}

.brand-panel,
.signin-card {
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 30px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.86), rgba(255, 255, 255, 0.68));
  box-shadow: 0 30px 90px rgba(30, 41, 59, 0.13), inset 0 1px 0 rgba(255, 255, 255, 0.75);
}

.brand-panel {
  min-height: 650px;
  gap: 24px;
  padding: clamp(28px, 3.2vw, 42px);
}

.signin-card {
  width: 100%;
  max-width: 470px;
  justify-self: center;
  gap: 20px;
  padding: clamp(26px, 3vw, 34px);
  background: rgba(255, 255, 255, 0.82);
}

.brand-logo {
  width: 56px;
  height: 56px;
  border-radius: 18px;
  background: linear-gradient(145deg, #2563eb 0%, #4f46e5 48%, #8b5cf6 100%);
  box-shadow: 0 16px 36px rgba(37, 99, 235, 0.28);
}

.brand-topline strong {
  font-size: 22px;
  font-weight: 900;
}

.brand-topline span {
  margin-top: 4px;
  font-size: 14px;
  line-height: 1.45;
}

.hero-copy {
  max-width: 700px;
}

.eyebrow {
  border-color: rgba(79, 70, 229, 0.16);
  padding: 8px 13px;
  color: #3347c8;
  background: linear-gradient(135deg, rgba(239, 246, 255, 0.96), rgba(245, 243, 255, 0.96));
  box-shadow: 0 8px 22px rgba(37, 99, 235, 0.08);
}

.hero-copy h1 {
  max-width: 660px;
  margin: 18px 0 14px;
  color: #0f172a;
  font-size: clamp(38px, 4.1vw, 56px);
  line-height: 1.08;
  font-weight: 950;
}

.hero-copy p {
  max-width: 620px;
  color: #475569;
  font-size: 16px;
  line-height: 1.78;
}

.workflow-strip {
  position: relative;
  gap: 8px;
  padding: 2px 0;
}

.workflow-strip span {
  position: relative;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border-color: rgba(37, 99, 235, 0.12);
  padding: 9px 12px 9px 10px;
  color: #1e3a8a;
  background: rgba(255, 255, 255, 0.72);
  box-shadow: 0 10px 24px rgba(37, 99, 235, 0.07);
}

.workflow-strip span::before {
  content: '';
  width: 8px;
  height: 8px;
  border-radius: 999px;
  background: linear-gradient(135deg, #2563eb, #8b5cf6);
  box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.1);
}

.feature-grid {
  gap: 16px;
}

.feature-card {
  min-height: 138px;
  border-color: rgba(148, 163, 184, 0.16);
  border-radius: 20px;
  padding: 18px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.94), rgba(248, 251, 255, 0.9));
  box-shadow: 0 18px 45px rgba(37, 99, 235, 0.09);
}

.feature-card:hover {
  border-color: rgba(79, 70, 229, 0.26);
  transform: translateY(-4px);
  box-shadow: 0 26px 56px rgba(37, 99, 235, 0.14);
}

.feature-card > span {
  width: 38px;
  height: 38px;
  border-radius: 999px;
  color: #fff;
  background: linear-gradient(135deg, #2563eb, #7c3aed);
}

.signin-heading span {
  padding: 6px 11px;
  color: #4338ca;
  background: #eef2ff;
}

.signin-heading h2 {
  margin: 13px 0 7px;
  font-size: 31px;
  font-weight: 950;
}

.role-selector {
  gap: 12px;
}

.role-option {
  min-height: 108px;
  border-color: #e5edf7;
  border-radius: 20px;
  padding: 14px;
  background: rgba(248, 250, 252, 0.86);
}

.role-option:hover {
  border-color: rgba(37, 99, 235, 0.28);
  box-shadow: 0 16px 34px rgba(37, 99, 235, 0.1);
}

.role-option.active {
  border-color: rgba(79, 70, 229, 0.44);
  background: linear-gradient(180deg, #ffffff, #f4f7ff);
  box-shadow: 0 18px 42px rgba(37, 99, 235, 0.16);
}

.role-option span {
  width: 34px;
  height: 34px;
  border-radius: 999px;
  box-shadow: 0 10px 22px rgba(37, 99, 235, 0.2);
}

.role-option strong {
  color: #1e293b;
}

.login-form {
  gap: 13px;
}

.login-form input {
  height: 50px;
  border-color: #dbe6f2;
  border-radius: 17px;
  background: rgba(255, 255, 255, 0.94);
}

.login-form input::placeholder {
  color: #94a3b8;
}

.login-form input:focus {
  border-color: #3b82f6;
  box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.12), 0 12px 26px rgba(37, 99, 235, 0.08);
}

.role-note {
  border: 1px solid rgba(37, 99, 235, 0.1);
  border-radius: 14px;
  padding: 10px 12px;
  background: rgba(239, 246, 255, 0.62);
  font-size: 13px;
}

.error-note {
  position: relative;
  border: 1px solid rgba(248, 113, 113, 0.22);
  border-left: 4px solid #ef4444;
  border-radius: 14px;
  padding: 10px 12px 10px 14px;
  color: #991b1b;
  background: rgba(254, 242, 242, 0.86);
}

.primary-action {
  height: 52px;
  border-radius: 17px;
  background: linear-gradient(135deg, #2563eb 0%, #4f46e5 48%, #7c3aed 100%);
  box-shadow: 0 18px 36px rgba(37, 99, 235, 0.28);
  transition: transform 0.18s ease, box-shadow 0.18s ease, filter 0.18s ease;
}

.primary-action:not(:disabled):hover {
  transform: translateY(-1px);
  filter: brightness(1.04);
  box-shadow: 0 22px 44px rgba(37, 99, 235, 0.34);
}

.primary-action:not(:disabled):active {
  transform: translateY(0);
}

.primary-action:disabled {
  filter: saturate(0.82);
}

.quick-row {
  gap: 9px;
}

.quick-row button,
.quick-row a {
  border-color: #dbe6f2;
  border-radius: 15px;
  color: #3347c8;
  background: rgba(248, 251, 255, 0.86);
  transition: border-color 0.18s ease, background 0.18s ease, transform 0.18s ease;
}

.quick-row button:not(:disabled):hover,
.quick-row a:hover {
  border-color: rgba(37, 99, 235, 0.26);
  background: #fff;
  transform: translateY(-1px);
}

.quick-row.subtle a {
  color: #64748b;
  background: transparent;
}

@media (max-width: 1080px) {
  .login-shell {
    grid-template-columns: 1fr;
    align-items: stretch;
  }

  .signin-card {
    max-width: none;
  }

  .brand-panel {
    min-height: auto;
  }
}

@media (max-width: 760px) {
  .login-page {
    padding: 12px;
  }

  .brand-panel,
  .signin-card {
    border-radius: 24px;
    padding: 22px;
  }

  .hero-copy h1 {
    font-size: 34px;
  }

  .feature-grid,
  .role-selector,
  .quick-row,
  .quick-row.subtle {
    grid-template-columns: 1fr;
  }
}
</style>
