<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import { api } from '../api/client';
import type { Course } from '../types';

interface RetrievedContext {
  content: string;
  source_file?: string;
  document_id?: number;
  score?: number;
  confidence?: number;
}

interface CitationSource {
  document_name: string;
  snippet: string;
  relevance?: number;
  confidence?: number;
}

interface TutorAnswer {
  answer?: {
    answer?: string;
    [key: string]: unknown;
  };
  retrieved_context: RetrievedContext[];
  citation_sources?: CitationSource[];
  follow_up_suggestions?: string[];
  based_on_material?: boolean;
  confidence?: number;
  confidence_level?: 'high' | 'medium' | 'low';
  confidence_breakdown?: { avg: number; max: number; min: number; count: number };
  teaching_strategy?: string;
  hint_level?: string;
  hint_text?: string;
  detected_misconception?: string;
  mastery_delta?: number;
  guiding_questions?: string[];
  demo_fallback_note?: string;
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
  citation_sources?: CitationSource[];
  follow_up_suggestions?: string[];
  based_on_material?: boolean;
  confidence?: number;
  confidence_level?: 'high' | 'medium' | 'low';
  confidence_breakdown?: { avg: number; max: number; min: number; count: number };
  teaching_strategy?: string;
  hint_level?: string;
  detected_misconception?: string;
  mastery_delta?: number;
  mode: string;
  created_at: string;
}

const courses = ref<Course[]>([]);
const answer = ref<TutorAnswer | null>(null);
const history = ref<TutorHistoryItem[]>([]);
const pageLoading = ref(true);
const loading = ref(false);
const historyLoading = ref(false);
const error = ref('');
const form = reactive({
  course_id: 0,
  question: 'Python 爬虫发送 HTTP 请求的基本步骤是什么？',
  top_k: 3,
  heuristic_mode: true,
  no_direct_answer: false,
  hint_level: 'medium'
});

function answerText(value?: TutorAnswer | TutorHistoryItem | null) {
  if (!value) return '';
  return value.answer?.answer || JSON.stringify(value.answer || {}, null, 2);
}

function formatDate(value?: string) {
  if (!value) return '暂无时间';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '时间格式异常';
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
}

function getConfidenceColor(confidence?: number): string {
  if (!confidence) return '#94a3b8';
  if (confidence >= 0.7) return '#22c55e';
  if (confidence >= 0.4) return '#eab308';
  return '#ef4444';
}

function getConfidenceLabel(level?: 'high' | 'medium' | 'low'): string {
  if (level === 'high') return '高可信';
  if (level === 'medium') return '中可信';
  if (level === 'low') return '低可信';
  return '未知';
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
  } catch (err) {
    error.value = err instanceof Error ? err.message : '问答历史加载失败';
  } finally {
    historyLoading.value = false;
  }
}

async function loadCourses() {
  pageLoading.value = true;
  error.value = '';
  try {
    courses.value = await api.get<Course[]>('/api/v1/courses');
    form.course_id = courses.value[0]?.id || 0;
    await loadHistory();
  } catch (err) {
    error.value = err instanceof Error ? err.message : '课程列表加载失败，请确认后端已启动。';
  } finally {
    pageLoading.value = false;
  }
}

async function ask() {
  if (!form.course_id || !form.question.trim()) return;
  loading.value = true;
  error.value = '';
  try {
    answer.value = await api.post<TutorAnswer>('/api/v1/tutor/ask', {
      course_id: form.course_id,
      question: form.question.trim(),
      top_k: form.top_k,
      heuristic_mode: form.heuristic_mode,
      no_direct_answer: form.no_direct_answer,
      hint_level: form.hint_level
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
        <p class="demo-note">当前支持 mock/demo 答疑和轻量 RAG fallback；引用来源用于演示资料依据，不代表真实商业产品能力。</p>
      </div>
      <div class="mode-card">
        <span>回答模式</span>
        <strong>{{ answer?.mode || (form.heuristic_mode ? '启发式 demo 模式' : 'mock / online') }}</strong>
      </div>
    </div>

    <p v-if="pageLoading" class="panel muted">正在加载课程和问答历史...</p>

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
          <label>
            提示层级
            <select v-model="form.hint_level">
              <option value="light">轻提示</option>
              <option value="medium">中提示</option>
              <option value="detailed">详细解释</option>
            </select>
          </label>
          <label class="check-row">
            <input v-model="form.heuristic_mode" type="checkbox" />
            启发式答疑模式
          </label>
          <label class="check-row">
            <input v-model="form.no_direct_answer" type="checkbox" />
            不直接给最终答案
          </label>
        </div>
        <p v-if="!pageLoading && !courses.length" class="muted">暂无课程，请先在课程管理中创建课程或运行演示数据脚本。</p>
        <label class="question-box">
          问题
          <textarea v-model="form.question" />
        </label>
        <p v-if="error" class="error-text">{{ error }}</p>
        <button :disabled="loading || !form.course_id || !form.question.trim()" @click="ask">
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
      <div class="answer-flags">
        <span>{{ answer.based_on_material ? '基于资料回答' : '未命中资料，使用 fallback 回答' }}</span>
        <span>置信度 {{ answer.confidence ?? '-' }}</span>
        <span>{{ form.no_direct_answer ? '不直接给答案' : '可给出结构化回答' }}</span>
        <span>提示层级 {{ answer.hint_level || form.hint_level }}</span>
        <span>掌握度变化 +{{ answer.mastery_delta ?? 0 }}</span>
      </div>
      <div v-if="answer.teaching_strategy || answer.detected_misconception" class="teaching-card">
        <strong>教学策略：{{ answer.teaching_strategy || '暂无策略' }}</strong>
        <p>错因识别：{{ answer.detected_misconception || '暂无识别' }}</p>
        <p>分层提示：{{ answer.hint_text || '暂无提示' }}</p>
        <small>{{ answer.demo_fallback_note || '当前教学字段为规则估计，用于演示教学型对话闭环。' }}</small>
      </div>
      <div v-if="answer.guiding_questions?.length" class="guiding-list">
        <button
          v-for="item in answer.guiding_questions"
          :key="item"
          type="button"
          class="secondary"
          @click="form.question = item"
        >
          {{ item }}
        </button>
      </div>
      <div v-if="answer.follow_up_suggestions?.length" class="follow-list">
        <button
          v-for="item in answer.follow_up_suggestions"
          :key="item"
          type="button"
          class="secondary"
          @click="form.question = item"
        >
          {{ item }}
        </button>
      </div>
    </section>

    <section v-if="answer" class="panel">
      <div class="panel-title">
        <h2>引用来源</h2>
        <span class="muted">知识库检索结果</span>
      </div>
      <div v-if="answer.confidence !== undefined" class="confidence-summary">
        <div class="confidence-badge" :style="{ background: getConfidenceColor(answer.confidence) }">
          {{ getConfidenceLabel(answer.confidence_level) }}
        </div>
        <span class="confidence-score">整体可信度 {{ (answer.confidence * 100).toFixed(0) }}%</span>
        <span v-if="answer.confidence_breakdown" class="confidence-detail">
          (最高 {{ (answer.confidence_breakdown.max * 100).toFixed(0) }}% / 最低 {{ (answer.confidence_breakdown.min * 100).toFixed(0) }}%)
        </span>
      </div>
      <div class="source-grid">
        <article v-for="item in answer.citation_sources || []" :key="`${item.document_name}-${item.snippet}`" class="source-card">
          <div class="source-header">
            <strong>{{ item.document_name || '未知来源' }}</strong>
            <div v-if="item.confidence !== undefined" class="source-confidence">
              <div class="confidence-bar-bg">
                <div class="confidence-bar-fill" :style="{ width: `${(item.confidence || 0) * 100}%`, background: getConfidenceColor(item.confidence) }"></div>
              </div>
              <span class="confidence-value">{{ ((item.confidence || 0) * 100).toFixed(0) }}%</span>
            </div>
          </div>
          <span class="source-relevance">相关度 {{ (item.relevance ?? 0) >= 0 ? (item.relevance * 100).toFixed(0) + '%' : '-' }}</span>
          <p>{{ item.snippet }}</p>
        </article>
      </div>
      <p v-if="!(answer.citation_sources?.length || answer.retrieved_context.length)" class="muted">本次回答未检索到引用片段，请先上传课程资料或调整问题。</p>
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
  color: var(--color-primary-dark);
  font-size: 13px;
  font-weight: 700;
}

.demo-note {
  margin: 8px 0 0;
  color: var(--status-warning-text);
  font-size: 13px;
}

.mode-card {
  min-width: 180px;
  border: 1px solid var(--border-soft);
  border-radius: 8px;
  padding: 14px;
  background: var(--bg-surface);
}

.mode-card span,
.mode-card strong {
  display: block;
}

.mode-card span {
  color: var(--text-muted);
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

.check-row {
  display: flex;
  gap: 8px;
  align-items: center;
}

.check-row input {
  width: auto;
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
  border: 1px solid var(--border-soft);
  border-radius: 8px;
  padding: 12px;
  background: var(--bg-surface);
}

.history-item p {
  margin: 8px 0;
  color: var(--text-secondary);
}

.history-item span,
.source-card span {
  color: var(--text-muted);
  font-size: 13px;
}

.answer-box {
  white-space: pre-wrap;
  line-height: 1.7;
  color: var(--text-main);
}

.answer-flags,
.follow-list,
.guiding-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.answer-flags span {
  border-radius: 999px;
  padding: 6px 9px;
  color: var(--color-primary-dark);
  background: var(--color-primary-light);
}

.teaching-card {
  margin-top: 12px;
  border: 1px solid var(--border-soft);
  border-radius: 8px;
  padding: 12px;
  background: var(--bg-surface);
}

.teaching-card p {
  margin: 8px 0 0;
  color: var(--text-secondary);
}

.teaching-card small {
  display: block;
  margin-top: 8px;
  color: var(--status-warning-text);
}

.source-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 12px;
}

.source-card {
  border: 1px solid var(--border-soft);
  border-radius: 8px;
  padding: 12px;
  background: var(--bg-surface);
}

.source-card p {
  margin: 10px 0 0;
  color: var(--text-secondary);
}

.source-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
}

.source-confidence {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-shrink: 0;
}

.confidence-bar-bg {
  width: 50px;
  height: 6px;
  background: var(--border-soft);
  border-radius: 3px;
  overflow: hidden;
}

.confidence-bar-fill {
  height: 100%;
  border-radius: 3px;
  transition: width 0.3s ease;
}

.confidence-value {
  font-size: 12px;
  color: var(--text-muted);
  min-width: 28px;
}

.confidence-summary {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 14px;
  padding: 10px 14px;
  background: var(--bg-surface);
  border: 1px solid var(--border-soft);
  border-radius: 8px;
}

.confidence-badge {
  padding: 4px 10px;
  border-radius: 999px;
  color: white;
  font-size: 12px;
  font-weight: 600;
}

.confidence-score {
  font-weight: 500;
  color: var(--text-main);
}

.confidence-detail {
  font-size: 13px;
  color: var(--text-muted);
}

.error-text {
  color: var(--status-danger-dark);
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
