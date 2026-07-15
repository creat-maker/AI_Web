<script setup lang="ts">
import { computed, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import type { RuntimeInfo } from '../types';
import { findMenuItem, roleDescriptions, roleHomePath, roleLabels, type UserRole } from '../config/roles';
import { useRole } from '../composables/useRole';

defineProps<{
  runtime: RuntimeInfo | null;
  runtimeLoading: boolean;
}>();

const route = useRoute();
const router = useRouter();
const { availableRoles, clearRole, currentRole, setRole } = useRole();

const currentRoleLabel = computed(() => roleLabels[currentRole.value]);
const currentMenu = computed(() => findMenuItem(currentRole.value, route.path));
const title = computed(() => currentMenu.value?.label || String(route.meta.title || 'EduMind Studio'));
const subtitle = computed(() => currentMenu.value?.description || roleDescriptions[currentRole.value]);
const userDropdownOpen = ref(false);
const searchOpen = ref(false);
const searchQuery = ref('');

const userName = computed(() => {
  if (currentRole.value === 'teacher') return '王老师';
  if (currentRole.value === 'admin') return '管理员';
  return '李明';
});

const searchResults = computed(() => {
  const word = searchQuery.value.trim().toLowerCase();
  const entries = [
    { title: '我的课程', path: '/student/courses', role: 'student', desc: '查看课程进度' },
    { title: '学习资源', path: '/student/resources', role: 'student', desc: '搜索循环结构资源' },
    { title: '课程管理', path: '/teacher/courses', role: 'teacher', desc: '新建和管理课程' },
    { title: '报告中心', path: '/teacher/reports', role: 'teacher', desc: '预览和导出报告' },
    { title: '资源生成中心', path: '/admin/resource-generate', role: 'admin', desc: '生成课程资源包' },
    { title: '用户与角色', path: '/admin/users', role: 'admin', desc: '管理用户和权限' },
    { title: '系统运行状态', path: '/admin/demo-status', role: 'admin', desc: '查看健康检查' }
  ].filter((item) => item.role === currentRole.value);
  if (!word) return entries;
  return entries.filter((item) => `${item.title} ${item.desc}`.toLowerCase().includes(word));
});

function go(path: string) {
  searchOpen.value = false;
  userDropdownOpen.value = false;
  router.push(path);
}

function switchRole(role: UserRole) {
  setRole(role);
  userDropdownOpen.value = false;
  router.push(roleHomePath[role]);
}

function logout() {
  clearRole();
  router.push('/login');
}
</script>

<template>
  <header class="app-header" :data-role="currentRole">
    <div class="header-copy">
      <h1>{{ title }}</h1>
      <p>{{ subtitle }}</p>
    </div>

    <div class="header-right">
      <div class="search-wrap">
        <button class="search-trigger" type="button" @click="searchOpen = true">
          搜索课程、资源、报告...
        </button>
        <div v-if="searchOpen" class="search-popover">
          <input v-model="searchQuery" autofocus placeholder="输入关键词，例如：循环" @keyup.enter.prevent />
          <div class="search-list">
            <button v-for="item in searchResults" :key="item.path" type="button" @click="go(item.path)">
              <strong>{{ item.title }}</strong>
              <span>{{ item.desc }}</span>
            </button>
            <p v-if="!searchResults.length" class="muted">未找到相关入口。</p>
          </div>
          <button class="ghost" type="button" @click="searchOpen = false">关闭</button>
        </div>
      </div>

      <button v-if="currentRole === 'teacher'" class="quick-btn" type="button" @click="go('/teacher/courses')">新建课程</button>
      <button v-if="currentRole === 'student'" class="quick-btn" type="button" @click="go('/student/resources')">学习资源</button>
      <button v-if="currentRole === 'admin'" class="quick-btn" type="button" @click="go('/admin/demo-status')">系统状态</button>

      <button class="icon-btn" type="button" title="帮助中心" @click="go('/help-center')">?</button>

      <div class="user-area">
        <button class="user-trigger" type="button" @click="userDropdownOpen = !userDropdownOpen">
          <span class="avatar">{{ userName.slice(0, 1) }}</span>
          <span>{{ userName }}</span>
          <small>{{ currentRoleLabel }}</small>
        </button>
        <div v-if="userDropdownOpen" class="user-dropdown">
          <button type="button" @click="go('/profile')">个人中心</button>
          <button type="button" @click="go('/account-settings')">账号设置</button>
          <button type="button" @click="go('/help-center')">帮助中心</button>
          <div class="divider"></div>
          <button v-for="role in availableRoles" :key="role" type="button" @click="switchRole(role)">
            切换到{{ roleLabels[role] }}
          </button>
          <div class="divider"></div>
          <button class="danger" type="button" @click="logout">退出登录</button>
        </div>
      </div>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
  border-bottom: 1px solid var(--border-light);
  padding: 18px 24px;
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(16px);
}

.header-copy h1 {
  margin: 0;
  color: var(--text-main);
  font-size: 22px;
}

.header-copy p {
  margin: 5px 0 0;
  color: var(--text-secondary);
  font-size: 13px;
}

.header-right {
  display: flex;
  gap: 10px;
  align-items: center;
}

.search-wrap,
.user-area {
  position: relative;
}

.search-trigger,
.quick-btn,
.icon-btn,
.user-trigger {
  border: 1px solid var(--border-light);
  border-radius: 12px;
  padding: 10px 12px;
  color: var(--text-secondary);
  background: #fff;
  font-weight: 800;
}

.quick-btn {
  color: #fff;
  background: var(--color-primary);
}

.icon-btn {
  width: 40px;
  height: 40px;
  padding: 0;
}

.search-popover,
.user-dropdown {
  position: absolute;
  right: 0;
  top: calc(100% + 10px);
  z-index: 30;
  width: 320px;
  border: 1px solid var(--border-light);
  border-radius: 16px;
  padding: 12px;
  background: #fff;
  box-shadow: 0 20px 60px rgba(15, 23, 42, 0.16);
}

.search-list,
.user-dropdown {
  display: grid;
  gap: 8px;
}

.search-list button,
.user-dropdown button {
  display: grid;
  gap: 4px;
  width: 100%;
  border: 0;
  border-radius: 10px;
  padding: 10px;
  color: var(--text-main);
  background: #f8fafc;
  text-align: left;
}

.search-list span {
  color: var(--text-secondary);
  font-size: 12px;
}

.user-trigger {
  display: flex;
  gap: 8px;
  align-items: center;
}

.user-trigger small {
  color: var(--color-primary);
}

.avatar {
  display: grid;
  place-items: center;
  width: 30px;
  height: 30px;
  border-radius: 10px;
  color: #fff;
  background: var(--color-primary);
  font-weight: 900;
}

.divider {
  height: 1px;
  background: var(--border-light);
}

.danger {
  color: #b91c1c !important;
}

@media (max-width: 980px) {
  .app-header,
  .header-right {
    align-items: stretch;
    flex-direction: column;
  }

  .search-popover,
  .user-dropdown {
    left: 0;
    right: auto;
    width: min(320px, 90vw);
  }
}
</style>
