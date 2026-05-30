<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { RouterView } from 'vue-router';
import { api } from './api/client';
import AppLayout from './components/AppLayout.vue';
import type { RuntimeInfo } from './types';

const runtime = ref<RuntimeInfo | null>(null);
const runtimeLoading = ref(true);

onMounted(async () => {
  try {
    runtime.value = await api.get<RuntimeInfo>('/api/v1/runtime');
  } catch {
    runtime.value = { llm_mode: 'offline', mock_mode: true };
  } finally {
    runtimeLoading.value = false;
  }
});
</script>

<template>
  <AppLayout :runtime="runtime" :runtime-loading="runtimeLoading">
    <RouterView />
  </AppLayout>
</template>
