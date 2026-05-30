<script setup lang="ts">
import { computed } from 'vue';
import { RouterLink } from 'vue-router';
import { roleDescriptions, roleMenus } from '../config/roles';
import { useRole } from '../composables/useRole';
import RoleSwitcher from './RoleSwitcher.vue';
import StatusBadge from './StatusBadge.vue';

const { currentRole, currentRoleLabel } = useRole();
const menus = computed(() => roleMenus[currentRole.value]);
const description = computed(() => roleDescriptions[currentRole.value]);
</script>

<template>
  <aside class="app-sidebar">
    <div class="brand">
      <strong>EduMind</strong>
      <span>中国软件杯 A3 · 三端演示</span>
    </div>

    <div class="role-card">
      <span>当前身份</span>
      <strong>{{ currentRoleLabel }}</strong>
      <p>{{ description }}</p>
      <RoleSwitcher />
    </div>

    <nav class="side-nav">
      <RouterLink v-for="item in menus" :key="item.path" :to="item.path">
        <span>{{ item.label }}</span>
        <StatusBadge v-if="item.badge" :label="item.badge" tone="neutral" />
      </RouterLink>
    </nav>
  </aside>
</template>
