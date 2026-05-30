<script setup lang="ts">
import AppHeader from './AppHeader.vue';
import AppSidebar from './AppSidebar.vue';
import type { RuntimeInfo } from '../types';

defineProps<{
  runtime: RuntimeInfo | null;
  runtimeLoading: boolean;
}>();
</script>

<template>
  <div class="app-shell">
    <AppSidebar />
    <main class="app-main">
      <AppHeader :runtime="runtime" :runtime-loading="runtimeLoading" />
      <slot />
    </main>
  </div>
</template>
