<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import AppHeader from './AppHeader.vue';
import AppSidebar from './AppSidebar.vue';
import type { RuntimeInfo } from '../types';

defineProps<{
  runtime: RuntimeInfo | null;
  runtimeLoading: boolean;
}>();

const route = useRoute();
const isPublicPage = computed(() => route.path === '/login');
</script>

<template>
  <div v-if="isPublicPage" class="public-shell">
    <slot />
  </div>
  <div v-else class="app-shell">
    <AppSidebar />
    <main class="app-main">
      <AppHeader :runtime="runtime" :runtime-loading="runtimeLoading" />
      <div class="app-content">
        <slot />
      </div>
    </main>
  </div>
</template>
