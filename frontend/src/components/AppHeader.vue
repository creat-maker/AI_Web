<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import type { RuntimeInfo } from '../types';
import { findMenuItem, roleDescriptions, roleFromPath, roleLabels } from '../config/roles';

defineProps<{
  runtime: RuntimeInfo | null;
  runtimeLoading: boolean;
}>();

const route = useRoute();
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
</script>

<template>
  <header class="app-header">
    <div class="header-copy">
      <h1>{{ title }}</h1>
      <p>{{ subtitle }}</p>
    </div>
    <label class="header-search" aria-label="全局搜索">
      <input placeholder="搜索学生、课程、资源、报告..." />
    </label>
    <div class="header-actions">
      <button class="icon-button" type="button" title="通知">铃</button>
      <button class="icon-button" type="button" title="帮助">?</button>
      <div class="user-chip">
        <span class="avatar">{{ userName.slice(0, 1) }}</span>
        <div>
          <strong>{{ userName }}</strong>
          <span>{{ currentRoleLabel }} · {{ runtimeLoading ? '加载中' : runtime?.mock_mode ? '演示模式' : '在线' }}</span>
        </div>
      </div>
    </div>
  </header>
</template>
