<script setup lang="ts">
import { computed } from 'vue';
import { RouterLink, useRouter } from 'vue-router';
import { roleDescriptions, roleLabels, roleMenus } from '../config/roles';
import { useRole } from '../composables/useRole';
import StatusBadge from './StatusBadge.vue';

const router = useRouter();
const { clearRole, currentRole } = useRole();

const currentRoleLabel = computed(() => roleLabels[currentRole.value]);
const menus = computed(() => roleMenus[currentRole.value]);
const description = computed(() => roleDescriptions[currentRole.value]);
const roleSubtitle = computed(() => {
  if (currentRole.value === 'teacher') return '教学端';
  if (currentRole.value === 'admin') return '管理控制台';
  return '学生端';
});

function backToLogin() {
  clearRole();
  router.push('/login');
}
</script>

<template>
  <aside class="app-sidebar">
    <div class="brand">
      <span class="brand-mark">E</span>
      <div>
        <strong>EduMind Studio</strong>
        <span>{{ roleSubtitle }}</span>
      </div>
    </div>

    <div class="role-card">
      <span>当前角色</span>
      <strong>{{ currentRoleLabel }}</strong>
      <p>{{ description }}</p>
    </div>

    <nav class="side-nav">
      <RouterLink v-for="item in menus" :key="item.path" :to="item.path">
        <span>{{ item.label }}</span>
        <StatusBadge v-if="item.badge" :label="item.badge" tone="neutral" />
      </RouterLink>
    </nav>

    <div class="sidebar-footer">
      <strong>EduMind 助教</strong>
      <p>数据驱动教学闭环，覆盖课程、路径、答疑、测评与报告。</p>
      <button class="sidebar-logout" type="button" @click="backToLogin">退出登录</button>
    </div>
  </aside>
</template>
