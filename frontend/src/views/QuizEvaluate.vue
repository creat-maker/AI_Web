<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import { api } from '../api/client';

const quizzes = ref<any[]>([]);
const profiles = ref<any[]>([]);
const selectedQuizId = ref<number>();
const selectedProfileId = ref<number>();
const answers = reactive<Record<string, string>>({});
const result = ref<any | null>(null);
const loading = ref(true);
const error = ref('');
const operationMessage = ref('');

async function load() {
  loading.value = true;
  error.value = '';
  try {
    quizzes.value = await api.get<any[]>('/api/v1/quizzes');
    profiles.value = await api.get<any[]>('/api/v1/profiles');
    selectedQuizId.value = selectedQuizId.value || quizzes.value[0]?.id;
    selectedProfileId.value = selectedProfileId.value || profiles.value[0]?.id;
  } catch (err) {
    error.value = err instanceof Error ? err.message : '测验数据加载失败。';
  } finally {
    loading.value = false;
  }
}

async function submit() {
  if (!selectedQuizId.value || !selectedProfileId.value) return;
  result.value = await api.post('/api/v1/quizzes/submit', {
    quiz_id: selectedQuizId.value,
    student_profile_id: selectedProfileId.value,
    answers
  });
}

async function completeDemoQuiz() {
  operationMessage.value = '';
  try {
    result.value = await api.post('/api/v1/events/demo-quiz', {
      student_profile_id: selectedProfileId.value,
      course_id: profiles.value.find((item) => item.id === selectedProfileId.value)?.course_id,
      actor_role: 'student',
      actor_name: profiles.value.find((item) => item.id === selectedProfileId.value)?.student_name || 'demo_student'
    });
    operationMessage.value = 'demo 测验已完成，薄弱点会进入画像提示、资源推荐和学习路径调整事件。';
  } catch (err) {
    operationMessage.value = err instanceof Error ? err.message : 'demo 测验完成失败。';
  }
}

onMounted(load);
</script>

<template>
  <section class="page">
    <p v-if="loading" class="panel muted">正在加载测验数据...</p>
    <p v-if="error" class="panel error-text">{{ error }}</p>
    <p v-if="operationMessage" class="panel muted">{{ operationMessage }}</p>
    <div class="panel">
      <h2>测验题</h2>
      <div class="form-grid">
        <label>测验<select v-model.number="selectedQuizId"><option v-for="q in quizzes" :key="q.id" :value="q.id">{{ q.quiz_json.title }}</option></select></label>
        <label>学生画像<select v-model.number="selectedProfileId"><option v-for="p in profiles" :key="p.id" :value="p.id">{{ p.student_name }}</option></select></label>
      </div>
      <div v-for="question in quizzes.find((q) => q.id === selectedQuizId)?.quiz_json.questions || []" :key="question.id" class="item">
        <strong>{{ question.question }}</strong>
        <textarea v-model="answers[question.id]" placeholder="填写答案" />
      </div>
      <div class="row">
        <button @click="submit">提交答案并评价</button>
        <button class="secondary" @click="completeDemoQuiz">完成一次 demo 测验</button>
      </div>
    </div>
    <div v-if="result" class="panel">
      <h2>得分与错因分析</h2>
      <strong>{{ result.score || result.quiz_result?.score }}</strong>
      <p class="demo-banner">测验结果会记录 quiz_completed 事件，用于画像更新提示、资源推荐和路径调整。</p>
      <details open>
        <summary>测验反馈（展开查看）</summary>
        <pre>{{ result.feedback_json || result.quiz_result }}</pre>
      </details>
    </div>
  </section>
</template>
