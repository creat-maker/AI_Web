<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { api } from '../api/client';
import { teacherAnalysisDemoSource } from '../api/mocks';

const data = ref<any | null>(null);

onMounted(async () => {
  data.value = await api.get('/api/v1/quizzes/analysis');
});
</script>

<template>
  <section class="page">
    <div class="panel">
      <h2>班级学情分析</h2>
      <p>真实测验数量：{{ data?.real?.quiz_count ?? 0 }}</p>
      <p class="muted">Demo 数据来源：{{ data?.demo?.source || teacherAnalysisDemoSource }}</p>
      <div class="grid">
        <div v-for="item in data?.demo?.weak_point_distribution || []" :key="item.name" class="stat">
          <span>{{ item.name }}</span>
          <strong>{{ item.value }}%</strong>
        </div>
      </div>
    </div>
  </section>
</template>
