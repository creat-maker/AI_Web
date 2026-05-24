<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import { api } from '../api/client';
import type { Course } from '../types';

const courses = ref<Course[]>([]);
const result = ref<any | null>(null);
const running = ref(false);
const form = reactive({
  course_id: 0,
  student_name: '张三',
  current_level: '基础薄弱',
  learning_goal: '两周内掌握 Python 爬虫基础',
  weak_points_text: '函数,文件操作,HTTP请求',
  learning_preference: '案例驱动',
  question: 'Python 爬虫发送 HTTP 请求的基本步骤是什么？'
});

const nodes = ['ProfileAgent', 'PlannerAgent', 'ResourceAgent', 'TutorAgent', 'EvaluatorAgent', 'ReporterAgent'];

onMounted(async () => {
  courses.value = await api.get<Course[]>('/api/v1/courses');
  form.course_id = courses.value[0]?.id || 0;
});

async function runFlow() {
  running.value = true;
  try {
    result.value = await api.post('/api/v1/agent-workflow/run-full-learning-flow', {
      ...form,
      weak_points: form.weak_points_text.split(',').map((item) => item.trim()).filter(Boolean)
    });
  } finally {
    running.value = false;
  }
}
</script>

<template>
  <section class="page">
    <div class="panel">
      <h2>多智能体工作流</h2>
      <div class="flow">
        <div v-for="node in nodes" :key="node" class="node" :class="{ done: result?.messages?.some((m: string) => m.includes(node)) }">{{ node }}</div>
      </div>
    </div>
    <div class="panel">
      <h2>运行参数</h2>
      <div class="form-grid">
        <label>课程<select v-model.number="form.course_id"><option v-for="c in courses" :key="c.id" :value="c.id">{{ c.title }}</option></select></label>
        <label>学生<input v-model="form.student_name" /></label>
        <label>水平<input v-model="form.current_level" /></label>
        <label>偏好<input v-model="form.learning_preference" /></label>
        <label>薄弱点<input v-model="form.weak_points_text" /></label>
        <label>学习目标<textarea v-model="form.learning_goal" /></label>
        <label>答疑问题<textarea v-model="form.question" /></label>
        <button :disabled="running" @click="runFlow">{{ running ? '运行中...' : '运行完整学习流' }}</button>
      </div>
    </div>
    <div v-if="result" class="panel">
      <h2>运行结果</h2>
      <pre>{{ result }}</pre>
    </div>
  </section>
</template>
