<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import { api } from '../api/client';
import type { Course } from '../types';

const courses = ref<Course[]>([]);
const form = reactive({ title: 'Python 程序设计', subject: '计算机', teacher_name: '教师', description: 'Python 爬虫基础与实践' });

async function load() {
  courses.value = await api.get<Course[]>('/api/v1/courses');
}

async function createCourse() {
  await api.post<Course>('/api/v1/courses', form);
  await load();
}

async function removeCourse(id: number) {
  await api.delete(`/api/v1/courses/${id}`);
  await load();
}

onMounted(load);
</script>

<template>
  <section class="page">
    <div class="panel">
      <h2>课程新增</h2>
      <div class="form-grid">
        <label>课程名称<input v-model="form.title" /></label>
        <label>学科<input v-model="form.subject" /></label>
        <label>教师<input v-model="form.teacher_name" /></label>
        <label>简介<input v-model="form.description" /></label>
        <button @click="createCourse">保存课程</button>
      </div>
    </div>
    <div class="panel">
      <h2>课程列表</h2>
      <div class="list">
        <article v-for="course in courses" :key="course.id" class="item">
          <div class="row">
            <strong>{{ course.title }}</strong>
            <span class="muted">{{ course.subject }} / {{ course.teacher_name }}</span>
            <button class="danger" @click="removeCourse(course.id)">删除</button>
          </div>
          <p>{{ course.description }}</p>
        </article>
      </div>
    </div>
  </section>
</template>
