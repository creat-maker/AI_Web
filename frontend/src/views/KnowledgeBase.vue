<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { api } from '../api/client';
import type { Course } from '../types';

const courses = ref<Course[]>([]);
const courseId = ref<number>();
const file = ref<File | null>(null);
const docs = ref<any[]>([]);
const query = ref('Python 爬虫发送 HTTP 请求的基本步骤是什么？');
const results = ref<any[]>([]);

async function loadCourses() {
  courses.value = await api.get<Course[]>('/api/v1/courses');
  courseId.value = courseId.value || courses.value[0]?.id;
  await loadDocs();
}

async function loadDocs() {
  if (!courseId.value) return;
  docs.value = await api.get<any[]>(`/api/v1/knowledge-base/documents?course_id=${courseId.value}`);
}

async function upload() {
  if (!courseId.value || !file.value) return;
  const form = new FormData();
  form.append('file', file.value);
  await api.upload(`/api/v1/knowledge-base/upload?course_id=${courseId.value}`, form);
  await loadDocs();
}

async function search() {
  if (!courseId.value) return;
  const data = await api.get<{ items: any[] }>(`/api/v1/knowledge-base/search?course_id=${courseId.value}&query=${encodeURIComponent(query.value)}&top_k=5`);
  results.value = data.items;
}

onMounted(loadCourses);
</script>

<template>
  <section class="page">
    <div class="panel">
      <h2>资料上传与解析</h2>
      <div class="form-grid">
        <label>课程<select v-model.number="courseId" @change="loadDocs"><option v-for="c in courses" :key="c.id" :value="c.id">{{ c.title }}</option></select></label>
        <label>资料文件<input type="file" @change="file = ($event.target as HTMLInputElement).files?.[0] || null" /></label>
        <button @click="upload">上传并建立知识库</button>
      </div>
    </div>
    <div class="panel">
      <h2>解析状态</h2>
      <div class="list">
        <div v-for="doc in docs" :key="doc.id" class="item">{{ doc.filename }} / {{ doc.parse_status }} / chunks: {{ doc.chunk_count }}</div>
      </div>
    </div>
    <div class="panel">
      <h2>检索测试</h2>
      <div class="row">
        <input v-model="query" />
        <button @click="search">检索</button>
      </div>
      <div class="list">
        <article v-for="item in results" :key="item.content" class="item">
          <strong>{{ item.source_file }} / score {{ item.score }}</strong>
          <p>{{ item.content }}</p>
        </article>
      </div>
    </div>
  </section>
</template>
