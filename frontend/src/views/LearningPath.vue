<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { api } from '../api/client';

const paths = ref<any[]>([]);

onMounted(async () => {
  paths.value = await api.get<any[]>('/api/v1/learning-paths');
});
</script>

<template>
  <section class="page">
    <div class="panel">
      <h2>个性化学习路径</h2>
      <div class="list">
        <article v-for="path in paths" :key="path.id" class="item">
          <strong>{{ path.path_json.course_title }}：{{ path.path_json.goal }}</strong>
          <div class="grid">
            <div v-for="stage in path.path_json.stages || []" :key="stage.name" class="item">
              <strong>{{ stage.name }}</strong>
              <p>目标：{{ stage.target }}</p>
              <p>资源：{{ (stage.resources || []).join('、') }}</p>
              <p>练习：{{ stage.practice }}</p>
              <p>掌握标准：{{ stage.mastery }}</p>
            </div>
          </div>
        </article>
      </div>
    </div>
  </section>
</template>
