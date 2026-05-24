<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { api } from '../api/client';

const stats = ref<Record<string, number | string>>({});

onMounted(async () => {
  stats.value = await api.get<Record<string, number | string>>('/api/v1/courses/stats');
});
</script>

<template>
  <section class="page">
    <div class="grid">
      <div v-for="key in ['courses', 'profiles', 'resources', 'quizzes', 'reports', 'agent_runs']" :key="key" class="stat">
        <span>{{ key }}</span>
        <strong>{{ stats[key] ?? 0 }}</strong>
      </div>
    </div>
    <div class="panel">
      <h2>MVP 闭环</h2>
      <p class="muted">创建课程、上传资料、生成画像和学习路径、生成资源、RAG 答疑、测验评价、导出报告。</p>
      <p class="muted">{{ stats.demo_data_note }}</p>
    </div>
  </section>
</template>
