<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import { api } from '../api/client';
import type { Course } from '../types';

const courses = ref<Course[]>([]);
const answer = ref<any | null>(null);
const form = reactive({ course_id: 0, question: 'Python 爬虫发送 HTTP 请求的基本步骤是什么？', top_k: 3 });

onMounted(async () => {
  courses.value = await api.get<Course[]>('/api/v1/courses');
  form.course_id = courses.value[0]?.id || 0;
});

async function ask() {
  answer.value = await api.post('/api/v1/tutor/ask', form);
}
</script>

<template>
  <section class="page">
    <div class="panel">
      <h2>基于课程知识库的智能答疑</h2>
      <div class="form-grid">
        <label>课程<select v-model.number="form.course_id"><option v-for="c in courses" :key="c.id" :value="c.id">{{ c.title }}</option></select></label>
        <label>问题<textarea v-model="form.question" /></label>
        <button @click="ask">提问</button>
      </div>
    </div>
    <div v-if="answer" class="panel">
      <h2>回答</h2>
      <p>{{ answer.answer.answer }}</p>
      <h2>引用来源</h2>
      <div class="list">
        <div v-for="item in answer.retrieved_context" :key="item.content" class="item">
          <strong>{{ item.source_file }} / score {{ item.score }}</strong>
          <p>{{ item.content }}</p>
        </div>
      </div>
    </div>
  </section>
</template>
