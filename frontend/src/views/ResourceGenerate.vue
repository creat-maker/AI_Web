<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { api } from '../api/client';

const resources = ref<any[]>([]);

onMounted(async () => {
  resources.value = await api.get<any[]>('/api/v1/resources');
});
</script>

<template>
  <section class="page">
    <div class="panel">
      <h2>AI 生成资源</h2>
      <div class="list">
        <article v-for="item in resources" :key="item.id" class="item">
          <div class="row">
            <strong>{{ item.title }}</strong>
            <span class="muted">{{ item.resource_type }} / {{ item.difficulty }} / {{ item.source_agent }}</span>
          </div>
          <div class="markdown">{{ item.content }}</div>
        </article>
      </div>
    </div>
  </section>
</template>
