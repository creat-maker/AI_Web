<script setup lang="ts">
import { computed } from 'vue';
import { RouterLink, useRoute } from 'vue-router';
import type { RuntimeInfo } from '../types';
import { findMenuItem, roleDescriptions } from '../config/roles';
import { useRole } from '../composables/useRole';
import StatusBadge from './StatusBadge.vue';

defineProps<{
  runtime: RuntimeInfo | null;
  runtimeLoading: boolean;
}>();

const route = useRoute();
const { currentRole, currentRoleLabel } = useRole();

const currentMenu = computed(() => findMenuItem(currentRole.value, route.path));
const title = computed(() => currentMenu.value?.label || String(route.meta.title || 'EduMind 三端工作台'));
const subtitle = computed(() => currentMenu.value?.description || roleDescriptions[currentRole.value]);
</script>

<template>
  <header class="app-header">
    <div class="header-copy">
      <p class="eyebrow">当前身份：{{ currentRoleLabel }}</p>
      <h1>{{ title }}</h1>
      <p>{{ subtitle }}</p>
    </div>
    <div class="header-actions">
      <StatusBadge :label="runtime?.mock_mode ? '当前模式：演示模式' : '当前模式：真实 AI 配置'" :tone="runtime?.mock_mode ? 'warning' : 'success'" />
      <StatusBadge label="数据来源：SQLite fallback / demo 数据" tone="info" />
      <RouterLink class="text-link" to="/capability-boundary">能力边界说明</RouterLink>
      <span v-if="runtimeLoading" class="muted">运行信息加载中...</span>
    </div>
  </header>
</template>
