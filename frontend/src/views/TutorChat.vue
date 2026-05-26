<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import { api } from '../api/client';
import type { Course } from '../types';

interface RetrievedContext {
  content: string;
  source_file?: string;
  document_id?: number;
  score?: number;
}

interface TutorAnswer {
  answer?: {
    answer?: string;
    [key: string]: unknown;
  };
  retrieved_context: RetrievedContext[];
  mode: string;
}

interface TutorHistoryItem {
  id: number;
  course_id: number;
  question: string;
  answer: {
    answer?: string;
    [key: string]: unknown;
  };
  retrieved_context: RetrievedContext[];
  mode: string;
  created_at: string;
}

const courses = ref<Course[]>([]);
const answer = ref<TutorAnswer | null>(null);
const history = ref<TutorHistoryItem[]>([]);
const loading = ref(false);
const historyLoading = ref(false);
const error = ref('');
const form = reactive({
  course_id: 0,
  question: 'Python 爬虫发送 HTTP 请求的基本步骤是什么？',
  top_k: 3
});

function answerText(value?: TutorAnswer | TutorHistoryItem | null) {
  if (!value) return '';
  return value.answer?.answer || JSON.stringify(value.answer || {}, null, 2);
}

function formatDate(value?: string) {
  if (!value) return '暂无时间';
  return new Date(value).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
}

async function loadHistory() {
  if (!form.course_id) {
    history.value = [];
    return;
  }
  historyLoading.value = true;
  try {
    history.value = await api.get<TutorHistoryItem[]>(
      `/api/v1/tutor/history?course_id=${form.course_id}&limit=12`
    );
  } finally {
    historyLoading.value = false;
  }
}

async function loadCourses() {
  courses.value = await api.get<Course[]>('/api/v1/courses');
  form.course_id = courses.value[0]?.id || 0;
  await loadHistory();
}

async function ask() {
  if (!form.course_id || !form.question.trim()) return;
  loading.value = true;
  error.value = '';
  try {
    answer.value = await api.post<TutorAnswer>('/api/v1/tutor/ask', {
      course_id: form.course_id,
      question: form.question.trim(),
      top_k: form.top_k
    });
    await loadHistory();
  } catch (err) {
    error.value = err instanceof Error ? err.message : '智能答疑请求失败';
  } finally {
    loading.value = false;
  }
}

onMounted(loadCourses);
</script>

<template>
  <section class="page tutor-page">
    <div class="panel tutor-hero">
      <div>
        <p class="eyebrow">RAG 智能答疑</p>
        <h2>基于课程知识库的智能答疑</h2>
        <p class="muted">选择课程后提问，系统会检索知识库片段并生成可追溯回答。</p>
      </div>
      <div class="mode-card">
        <span>回答模式</span>
        <strong>{{ answer?.mode || 'mock / online' }}</strong>
      </div>
    </div>

    <div class="tutor-layout">
      <section class="panel">
        <h2>提问</h2>
        <div class="form-grid">
          <label>
            课程
            <select v-model.number="form.course_id" @change="loadHistory">
              <option v-for="course in courses" :key="course.id" :value="course.id">{{ course.title }}</option>
            </select>
          </label>
          <label>
            检索片段数
            <select v-model.number="form.top_k">
              <option :value="2">2</option>
              <option :value="3">3</option>
              <option :value="5">5</option>
            </select>
          </label>
        </div>
        <label class="question-box">
          问题
          <textarea v-model="form.question" />
        </label>
        <p v-if="error" class="error-text">{{ error }}</p>
        <button :disabled="loading || !form.course_id" @click="ask">
          {{ loading ? '生成中...' : '提交问题' }}
        </button>
      </section>

      <section class="panel">
        <div class="panel-title">
          <h2>最近问答</h2>
          <span class="muted">{{ historyLoading ? '加载中...' : `${history.length} 条记录` }}</span>
        </div>
        <div class="history-list">
          <article v-for="item in history" :key="item.id" class="history-item">
            <strong>{{ item.question }}</strong>
            <p>{{ answerText(item) }}</p>
            <span>{{ formatDate(item.created_at) }} · {{ item.mode }}</span>
          </article>
          <p v-if="!historyLoading && !history.length" class="muted">暂无问答记录，完成一次提问后会显示在这里。</p>
        </div>
      </section>
    </div>

    <section v-if="answer" class="panel">
      <div class="panel-title">
        <h2>本次回答</h2>
        <span class="muted">引用 {{ answer.retrieved_context.length }} 个知识片段</span>
      </div>
      <div class="answer-box">{{ answerText(answer) }}</div>
    </section>

    <section v-if="answer" class="panel">
      <div class="panel-title">
        <h2>引用来源</h2>
        <span class="muted">知识库检索结果</span>
      </div>
      <div class="source-grid">
        <article v-for="item in answer.retrieved_context" :key="`${item.document_id}-${item.content}`" class="source-card">
          <strong>{{ item.source_file || '未知来源' }}</strong>
          <span>score {{ item.score ?? '-' }}</span>
          <p>{{ item.content }}</p>
        </article>
      </div>
      <p v-if="!answer.retrieved_context.length" class="muted">本次回答未检索到引用片段，请先上传课程资料或调整问题。</p>
    </section>
  </section>
</template>

<style scoped>
.tutor-page {
  gap: 18px;
}

.tutor-hero,
.panel-title,
.history-item,
.source-card strong {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.tutor-hero {
  align-items: center;
}

.tutor-hero h2 {
  margin: 0 0 8px;
  font-size: 24px;
}

.eyebrow {
  margin: 0 0 6px;
  color: #2264d1;
  font-size: 13px;
  font-weight: 700;
}

.mode-card {
  min-width: 180px;
  border: 1px solid #d9e0ea;
  border-radius: 8px;
  padding: 14px;
  background: #f8fbff;
}

.mode-card span,
.mode-card strong {
  display: block;
}

.mode-card span {
  color: #66758a;
  margin-bottom: 6px;
}

.tutor-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(320px, 0.9fr);
  gap: 16px;
}

.question-box {
  display: block;
  margin: 12px 0;
}

.question-box textarea {
  min-height: 150px;
}

.history-list {
  display: grid;
  gap: 10px;
}

.history-item {
  display: block;
  border: 1px solid #e4e9f1;
  border-radius: 8px;
  padding: 12px;
  background: #fbfcff;
}

.history-item p {
  margin: 8px 0;
  color: #39475a;
}

.history-item span,
.source-card span {
  color: #66758a;
  font-size: 13px;
}

.answer-box {
  white-space: pre-wrap;
  line-height: 1.7;
  color: #263244;
}

.source-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 12px;
}

.source-card {
  border: 1px solid #e4e9f1;
  border-radius: 8px;
  padding: 12px;
  background: #fbfcff;
}

.source-card p {
  margin: 10px 0 0;
  color: #39475a;
}

.error-text {
  color: #b42318;
}

@media (max-width: 980px) {
  .tutor-layout,
  .tutor-hero {
    display: grid;
  }

  .mode-card {
    min-width: 0;
  }
}
</style>
