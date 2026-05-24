<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import { api } from '../api/client';
import type { Course } from '../types';

const courses = ref<Course[]>([]);
const profiles = ref<any[]>([]);
const form = reactive({
  course_id: 0,
  student_name: '张三',
  current_level: '基础薄弱',
  learning_goal: '两周内掌握 Python 爬虫基础',
  weak_points_text: '函数,文件操作,HTTP请求',
  learning_preference: '案例驱动'
});

async function load() {
  courses.value = await api.get<Course[]>('/api/v1/courses');
  form.course_id = form.course_id || courses.value[0]?.id || 0;
  profiles.value = await api.get<any[]>('/api/v1/profiles');
}

async function createProfile() {
  await api.post('/api/v1/profiles/generate', {
    ...form,
    weak_points: form.weak_points_text.split(',').map((item) => item.trim()).filter(Boolean)
  });
  await load();
}

onMounted(load);
</script>

<template>
  <section class="page">
    <div class="panel">
      <h2>基础问卷</h2>
      <div class="form-grid">
        <label>课程<select v-model.number="form.course_id"><option v-for="c in courses" :key="c.id" :value="c.id">{{ c.title }}</option></select></label>
        <label>学生<input v-model="form.student_name" /></label>
        <label>当前水平<input v-model="form.current_level" /></label>
        <label>学习偏好<input v-model="form.learning_preference" /></label>
        <label>薄弱点<input v-model="form.weak_points_text" /></label>
        <label>学习目标<textarea v-model="form.learning_goal" /></label>
        <button @click="createProfile">生成画像</button>
      </div>
    </div>
    <div class="panel">
      <h2>画像详情</h2>
      <div class="list">
        <article v-for="profile in profiles" :key="profile.id" class="item">
          <strong>{{ profile.student_name }}</strong>
          <pre>{{ profile.profile_json }}</pre>
        </article>
      </div>
    </div>
  </section>
</template>
