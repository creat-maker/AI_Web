<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { apiBase } from '../api/client';
import { api } from '../api/client';

const reports = ref<any[]>([]);

onMounted(async () => {
  reports.value = await api.get<any[]>('/api/v1/reports');
});
</script>

<template>
  <section class="page">
    <div class="panel">
      <h2>学习报告列表</h2>
      <div class="list">
        <article v-for="report in reports" :key="report.id" class="item">
          <strong>{{ report.report_title }}</strong>
          <p class="muted">{{ report.report_path }}</p>
          <a :href="`${apiBase}/api/v1/reports/${report.id}/download`" target="_blank">下载 Word 报告</a>
        </article>
      </div>
    </div>
  </section>
</template>
