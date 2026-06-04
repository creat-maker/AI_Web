<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import type { RuntimeInfo } from '../types';
import { findMenuItem, roleDescriptions, roleFromPath, roleLabels, type UserRole } from '../config/roles';
import { useRole } from '../composables/useRole';

const props = defineProps<{
  runtime: RuntimeInfo | null;
  runtimeLoading: boolean;
}>();

const route = useRoute();
const router = useRouter();
const { clearRole, setRole, availableRoles } = useRole();

const currentRole = computed(() => roleFromPath(route.path) || 'student');
const currentRoleLabel = computed(() => roleLabels[currentRole.value]);
const currentMenu = computed(() => findMenuItem(currentRole.value, route.path));
const title = computed(() => currentMenu.value?.label || String(route.meta.title || 'EduMind 三端工作台'));
const subtitle = computed(() => currentMenu.value?.description || roleDescriptions[currentRole.value]);

const userName = computed(() => {
  if (currentRole.value === 'teacher') return '王老师';
  if (currentRole.value === 'admin') return '管理员';
  return '张三';
});

// Role-specific theme colors
const roleTheme = computed(() => {
  switch (currentRole.value) {
    case 'teacher': return { accent: '#059669', accentLight: '#ecfdf5', label: '教学端' };
    case 'admin': return { accent: '#7c3aed', accentLight: '#f3e8ff', label: '管理端' };
    default: return { accent: '#2563eb', accentLight: '#eff6ff', label: '学习端' };
  }
});

// Search
const searchOpen = ref(false);
const searchQuery = ref('');
const searchInput = ref<HTMLInputElement | null>(null);
const recentSearches = computed(() => {
  try { return JSON.parse(localStorage.getItem('edumind.recentSearches') || '[]'); } catch { return []; }
});

function openSearch() {
  searchOpen.value = true;
  setTimeout(() => searchInput.value?.focus(), 100);
}
function closeSearch() {
  searchOpen.value = false;
  searchQuery.value = '';
}
function handleSearch() {
  if (!searchQuery.value.trim()) return;
  const recent = recentSearches.value.filter((s: string) => s !== searchQuery.value);
  recent.unshift(searchQuery.value);
  if (recent.length > 5) recent.pop();
  localStorage.setItem('edumind.recentSearches', JSON.stringify(recent));
  closeSearch();
}

// Keyboard shortcut Ctrl+K
function onKeydown(e: KeyboardEvent) {
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault();
    openSearch();
  }
  if (e.key === 'Escape' && searchOpen.value) closeSearch();
}
onMounted(() => document.addEventListener('keydown', onKeydown));
onUnmounted(() => document.removeEventListener('keydown', onKeydown));

// Notifications
const notifOpen = ref(false);
const notifDrawer = ref<HTMLElement | null>(null);
const notifications = computed(() => {
  if (currentRole.value === 'teacher') {
    return [
      { id: 1, type: 'grading', text: '3 份作业待批改', time: '5 分钟前', unread: true },
      { id: 2, type: 'question', text: '李四提出了新问题', time: '20 分钟前', unread: true },
      { id: 3, type: 'report', text: '班级学习报告已生成', time: '1 小时前', unread: false },
    ];
  }
  if (currentRole.value === 'admin') {
    return [
      { id: 1, type: 'system', text: 'Agent 工作流运行完成', time: '3 分钟前', unread: true },
      { id: 2, type: 'review', text: '2 份报告待审核', time: '15 分钟前', unread: true },
      { id: 3, type: 'alert', text: '知识库文档解析异常', time: '30 分钟前', unread: false },
    ];
  }
  return [
    { id: 1, type: 'task', text: '今日测验截止提醒', time: '10 分钟前', unread: true },
    { id: 2, type: 'path', text: '学习路径已更新', time: '1 小时前', unread: true },
    { id: 3, type: 'badge', text: '获得新徽章「坚持学习」', time: '2 小时前', unread: false },
  ];
});
const unreadCount = computed(() => notifications.value.filter(n => n.unread).length);

function toggleNotifDrawer() {
  notifOpen.value = !notifOpen.value;
}

// User dropdown
const userDropdownOpen = ref(false);
const roleSubmenuOpen = ref(false);
function toggleUserDropdown() {
  userDropdownOpen.value = !userDropdownOpen.value;
  if (!userDropdownOpen.value) roleSubmenuOpen.value = false;
}

function openRoleSubmenu() {
  roleSubmenuOpen.value = true;
}

function switchRole(role: UserRole) {
  setRole(role);
  userDropdownOpen.value = false;
  roleSubmenuOpen.value = false;
  const homePaths: Record<UserRole, string> = { student: '/student', teacher: '/teacher', admin: '/dashboard' };
  router.push(homePaths[role]);
}

function logout() {
  userDropdownOpen.value = false;
  roleSubmenuOpen.value = false;
  clearRole();
  router.push('/login');
}

// Close dropdowns on outside click
function onDocClick(e: MouseEvent) {
  const target = e.target as HTMLElement;
  if (!target.closest('.header-user-area')) userDropdownOpen.value = false;
  if (!target.closest('.header-notif-area') && !target.closest('.notif-drawer')) notifOpen.value = false;
}
onMounted(() => document.addEventListener('click', onDocClick));
onUnmounted(() => document.removeEventListener('click', onDocClick));

// Student-specific: credits display
const studentCredits = ref(1280);
const studentLevel = ref('Lv.5');

// Admin-specific: system status
const systemStatus = computed(() => {
  if (!props.runtime) return 'offline';
  return props.runtime.mock_mode ? 'demo' : 'online';
});

// Fullscreen toggle
function toggleFullscreen() {
  document.documentElement.requestFullscreen?.();
}
</script>

<template>
  <header class="app-header" :data-role="currentRole">
    <!-- Left: Page title -->
    <div class="header-copy">
      <h1>{{ title }}</h1>
      <p>{{ subtitle }}</p>
    </div>

    <!-- Right: Flexbox right-aligned area -->
    <div class="header-right">
      <!-- Global Search -->
      <div class="header-search-area" :class="{ expanded: searchOpen }">
        <button class="search-trigger" type="button" @click="openSearch" title="全局搜索 (Ctrl+K)">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
          <span class="search-placeholder">{{ currentRole === 'admin' ? '搜索配置、功能、命令...' : '搜索学生、课程、资源...' }}</span>
          <kbd class="search-kbd">Ctrl+K</kbd>
        </button>
        <!-- Search overlay -->
        <Teleport to="body">
          <div v-if="searchOpen" class="search-overlay" @click.self="closeSearch">
            <div class="search-modal">
              <div class="search-modal-input">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
                <input ref="searchInput" v-model="searchQuery" :placeholder="currentRole === 'admin' ? '输入命令或搜索配置项...' : '搜索学生、课程、资源、报告...'" @keydown.enter="handleSearch" />
                <kbd @click="closeSearch">ESC</kbd>
              </div>
              <div v-if="recentSearches.length && !searchQuery" class="search-recent">
                <span class="search-recent-label">最近搜索</span>
                <button v-for="s in recentSearches" :key="s" class="search-recent-item" @click="searchQuery = s; handleSearch()">{{ s }}</button>
              </div>
            </div>
          </div>
        </Teleport>
      </div>

      <!-- Teacher: Quick Create Button -->
      <button v-if="currentRole === 'teacher'" class="quick-create-btn" type="button" @click="router.push('/courses')">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M12 5v14M5 12h14"/></svg>
        新建课程
      </button>

      <!-- Student: My Courses shortcut -->
      <button v-if="currentRole === 'student'" class="student-shortcut-btn" type="button" @click="router.push('/student/courses')">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"/><path d="M8 7h6M8 11h4"/></svg>
        我的课表
      </button>

      <!-- Admin: System Status Indicator -->
      <div v-if="currentRole === 'admin'" class="system-status-indicator" :class="systemStatus">
        <span class="status-dot"></span>
        <span class="status-label">{{ systemStatus === 'online' ? '运行正常' : systemStatus === 'demo' ? '演示模式' : '离线' }}</span>
      </div>

      <!-- Tool Icons Group -->
      <div class="header-tool-icons">
        <!-- Notification Bell -->
        <div class="header-notif-area">
          <button class="icon-btn" :class="{ 'has-badge': unreadCount > 0 }" type="button" title="通知中心" @click="toggleNotifDrawer">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>
            <span v-if="unreadCount > 0" class="badge-count">{{ unreadCount }}</span>
          </button>
        </div>

        <!-- Help -->
        <button class="icon-btn" type="button" title="帮助与反馈">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><path d="M12 17h.01"/></svg>
        </button>

        <!-- Fullscreen -->
        <button class="icon-btn" type="button" title="全屏" @click="toggleFullscreen">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"/></svg>
        </button>
      </div>

      <!-- User Account Area -->
      <div class="header-user-area">
        <button class="user-trigger" type="button" @click="toggleUserDropdown">
          <div class="user-avatar-wrap">
            <span class="avatar">{{ userName.slice(0, 1) }}</span>
            <span class="online-dot" :class="{ online: !runtimeLoading }"></span>
          </div>
          <div class="user-info">
            <strong>{{ userName }}</strong>
            <span class="user-role-tag" :style="{ background: roleTheme.accentLight, color: roleTheme.accent }">{{ currentRoleLabel }}</span>
          </div>
          <!-- Student: credits tag -->
          <span v-if="currentRole === 'student'" class="student-credits-tag">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>
            {{ studentCredits }}
          </span>
          <svg class="chevron" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="m6 9 6 6 6-6"/></svg>
        </button>

        <!-- User Dropdown -->
        <Transition name="dropdown">
          <div v-if="userDropdownOpen" class="user-dropdown">
            <!-- Arrow indicator -->
            <div class="dropdown-arrow"></div>

            <!-- Block 1: User Identity Header -->
            <div class="dropdown-identity" :style="{ background: roleTheme.accentLight }">
              <span class="avatar avatar-lg">{{ userName.slice(0, 1) }}</span>
              <div class="identity-text">
                <strong>{{ userName }}</strong>
                <div class="identity-badges">
                  <span class="role-badge" :style="{ background: roleTheme.accent, color: '#fff' }">{{ currentRoleLabel }}</span>
                  <span class="mode-badge">{{ runtimeLoading ? '加载中' : runtime?.mock_mode ? '演示模式' : '在线' }}</span>
                </div>
              </div>
            </div>

            <!-- Block 2: Core Function List -->
            <div class="dropdown-body">
              <button class="dropdown-item" type="button">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
                个人中心
              </button>
              <button class="dropdown-item" type="button">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
                账号设置
              </button>
              <button class="dropdown-item" type="button">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><path d="M12 17h.01"/></svg>
                帮助中心
              </button>

              <div class="dropdown-divider"></div>

              <!-- Switch Role: Submenu trigger -->
              <button class="dropdown-item submenu-trigger" type="button" @click="openRoleSubmenu">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 1l4 4-4 4"/><path d="M3 11V9a4 4 0 0 1 4-4h14"/><path d="M7 23l-4-4 4-4"/><path d="M21 13v2a4 4 0 0 1-4 4H3"/></svg>
                切换身份
                <svg class="submenu-arrow" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="m9 18 6-6-6-6"/></svg>
              </button>
            </div>

            <!-- Block 3: Footer -->
            <div class="dropdown-footer">
              <button class="dropdown-item danger" type="button" @click="logout">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
                退出登录
              </button>
            </div>

            <!-- Role Submenu (方案A: slides in from right) -->
            <Transition name="submenu">
              <div v-if="roleSubmenuOpen" class="role-submenu">
                <div class="submenu-header">
                  <button class="submenu-back" type="button" @click="roleSubmenuOpen = false">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="m15 18-6-6 6-6"/></svg>
                  </button>
                  <strong>切换身份</strong>
                </div>
                <div class="submenu-list">
                  <button v-for="role in availableRoles" :key="role" class="role-option" :class="{ active: role === currentRole }" type="button" @click="switchRole(role)">
                    <span class="role-icon" :style="{ background: role === 'teacher' ? '#059669' : role === 'admin' ? '#7c3aed' : '#2563eb' }">
                      {{ roleLabels[role].charAt(0) }}
                    </span>
                    <div class="role-option-text">
                      <strong>{{ roleLabels[role] }}</strong>
                      <span>{{ role === 'student' ? '学习路径、课程、答疑' : role === 'teacher' ? '课程管理、测评、报告' : '平台治理、Agent、日志' }}</span>
                    </div>
                    <svg v-if="role === currentRole" class="role-check" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M20 6 9 17l-5-5"/></svg>
                  </button>
                </div>
              </div>
            </Transition>
          </div>
        </Transition>
      </div>
    </div>

    <!-- Notification Drawer -->
    <Teleport to="body">
      <Transition name="drawer">
        <div v-if="notifOpen" class="notif-drawer">
          <div class="notif-drawer-header">
            <h3>通知中心</h3>
            <button class="icon-btn-sm" type="button" @click="notifOpen = false">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M18 6 6 18M6 6l12 12"/></svg>
            </button>
          </div>
          <div class="notif-list">
            <div v-for="n in notifications" :key="n.id" class="notif-item" :class="{ unread: n.unread }">
              <span class="notif-dot" v-if="n.unread"></span>
              <div class="notif-content">
                <p>{{ n.text }}</p>
                <span class="notif-time">{{ n.time }}</span>
              </div>
            </div>
          </div>
          <div class="notif-drawer-footer">
            <button class="text-btn" type="button">查看全部通知</button>
          </div>
        </div>
      </Transition>
      <Transition name="fade">
        <div v-if="notifOpen" class="drawer-backdrop" @click="notifOpen = false"></div>
      </Transition>
    </Teleport>
  </header>
</template>
