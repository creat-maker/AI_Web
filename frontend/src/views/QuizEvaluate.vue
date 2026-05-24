<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import { api } from '../api/client';

const quizzes = ref<any[]>([]);
const profiles = ref<any[]>([]);
const selectedQuizId = ref<number>();
const selectedProfileId = ref<number>();
const answers = reactive<Record<string, string>>({});
const result = ref<any | null>(null);

async function load() {
  quizzes.value = await api.get<any[]>('/api/v1/quizzes');
  profiles.value = await api.get<any[]>('/api/v1/profiles');
  selectedQuizId.value = selectedQuizId.value || quizzes.value[0]?.id;
  selectedProfileId.value = selectedProfileId.value || profiles.value[0]?.id;
}

async function submit() {
  if (!selectedQuizId.value || !selectedProfileId.value) return;
  result.value = await api.post('/api/v1/quizzes/submit', {
    quiz_id: selectedQuizId.value,
    student_profile_id: selectedProfileId.value,
    answers
  });
}

onMounted(load);
</script>

<template>
  <section class="page">
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
      <button @click="submit">提交答案并评价</button>
    </div>
    <div v-if="result" class="panel">
      <h2>得分与错因分析</h2>
      <strong>{{ result.score }}</strong>
      <pre>{{ result.feedback_json }}</pre>
    </div>
  </section>
</template>
