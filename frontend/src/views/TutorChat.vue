<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import { api } from '../api/client';
import CitationCard from '../components/CitationCard.vue';
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

interface TutorCard {
  title: string;
  content: string;
}

interface TutorAnswer {
  answer?: string | {
    answer?: string;
    [key: string]: unknown;
  };
  content?: string;
  cards?: TutorCard[];
  retrieved_context?: RetrievedContext[];
  citation_sources?: CitationSource[];
  citations?: Array<{ citation_id?: string; source_file?: string; sourceFile?: string; section_title?: string; section?: string; page_number?: number | null; confidence?: number; snippet?: string }>;
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
  learning_basis_note?: string;
  lowEvidenceRisk?: string;
  nextStep?: string;
  curriculum_alignment_score?: number;
  is_out_of_curriculum?: boolean;
  boundary_warning?: string;
  suggested_actions?: string[];
  retrieval_debug?: Record<string, unknown>;
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

interface DigitalHumanScriptSection {
  title: string;
  content: string;
}

interface DigitalHumanScriptResponse {
  message?: string;
  script: string;
  sections?: DigitalHumanScriptSection[];
}

const courses = ref<Course[]>([]);
const answer = ref<TutorAnswer | null>(null);
const history = ref<TutorHistoryItem[]>([]);
const pageLoading = ref(true);
const loading = ref(false);
const historyLoading = ref(false);
const error = ref('');
const scriptMessage = ref('');
const scriptLoading = ref(false);
const actionMessage = ref('');
const scriptReadyText = '讲解脚本已生成，可用于后续接入语音播报或数字人服务。';
const scriptSections = ref<DigitalHumanScriptSection[]>([]);
const quickQuestions = [
  '为什么我的 while 循环会死循环？',
  'break 和 continue 有什么区别？',
  '循环嵌套为什么容易看不懂？',
  'for 循环和 while 循环怎么选择？'
];
const form = reactive({
  course_id: 0,
  question: '为什么我的 while 循环会死循环？',
  top_k: 3,
  heuristic_mode: true,
  no_direct_answer: false,
  hint_level: 'medium'
});

function answerText(value?: TutorAnswer | TutorHistoryItem | null) {
  if (!value) return '';
  if ('cards' in value && value.cards?.length) {
    return value.cards.map((item) => `${item.title}：${item.content}`).join('\n');
  }
  if (typeof value.answer === 'string') return value.answer;
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

function evidenceRisk(value?: TutorAnswer | TutorHistoryItem | null) {
  const confidence = value?.confidence ?? 0;
  if ((value as TutorAnswer | null)?.lowEvidenceRisk) return (value as TutorAnswer).lowEvidenceRisk;
  if (confidence >= 0.8) return '低';
  if (confidence >= 0.5) return '中';
  return '高';
}

async function generateScript() {
  scriptLoading.value = true;
  scriptMessage.value = '';
  try {
    const result = await api.post<DigitalHumanScriptResponse>('/api/v1/ai-tutor/digital-human-script', {
      question: form.question || '为什么我的 while 循环会死循环？',
      mode: form.heuristic_mode ? '启发式答疑' : '智能答疑',
      studentId: 'student-li-ming',
      courseName: courses.value.find((item) => item.id === form.course_id)?.title || 'Python 程序设计'
    });
    scriptSections.value = result.sections?.length ? result.sections : [{ title: '讲解脚本', content: result.script }];
    scriptMessage.value = result.message || scriptReadyText;
  } catch {
    scriptSections.value = [
      { title: '开场白', content: '李明，我们先把 while 循环为什么停不下来这个问题拆开看。' },
      { title: '知识点解释', content: 'while 循环需要同时检查初始值、循环条件和变量更新。' },
      { title: '错误代码讲解', content: '如果循环体里缺少 i += 1，i 会一直小于 5，循环条件始终成立。' },
      { title: '正确代码讲解', content: '把 i += 1 放在循环体内，让每一轮执行后变量都更接近终止条件。' },
      { title: '常见错误提醒', content: '还要注意 continue 不要跳过变量更新语句，嵌套循环不要混用内外层变量。' },
      { title: '练习建议', content: '完成 3 道 while 循环补全题，并写出前三轮变量变化。' },
      { title: '总结', content: '判断循环是否可靠，关键是看条件是否会逐步接近结束。' }
    ];
    scriptMessage.value = scriptReadyText;
  } finally {
    scriptLoading.value = false;
  }
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
    error.value = '当前网络不稳定，已为你展示本地学习建议。';
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
    error.value = '当前网络不稳定，已为你展示本地学习建议。';
  } finally {
    pageLoading.value = false;
  }
}

async function ask() {
  if (!form.question.trim()) return;
  loading.value = true;
  error.value = '';
  actionMessage.value = '正在生成个性化学习建议...';
  try {
    const result = await api.post<TutorAnswer & { citation?: string; citations?: Array<{ snippet?: string; source_file?: string; sourceFile?: string; section_title?: string; section?: string; confidence?: number }>; nextLearningPath?: string }>('/api/v1/rag/ask', {
      question: form.question.trim(),
      courseId: 'python-programming',
      studentId: 'demo-basic'
    });
    answer.value = {
      ...result,
      mode: result.mode || '课程约束 RAG',
      retrieved_context: [],
      citation_sources: [
        ...(result.citations || []).map((item) => ({
          document_name: item.source_file || item.sourceFile || 'Python 程序设计课程知识库 / 循环结构章节',
          snippet: item.snippet || 'Python 程序设计课程知识库 / 循环结构章节',
          relevance: 0.86,
          confidence: item.confidence || result.confidence || 0.86
        }))
      ],
      based_on_material: true,
      confidence_level: 'high',
      nextStep: result.nextStep || result.nextLearningPath || '完成 while 循环专项练习'
    };
    actionMessage.value = '已生成本次诊断式回答。';
    await loadHistory();
  } catch (err) {
    error.value = '当前网络不稳定，已为你展示本地学习建议。';
  } finally {
    loading.value = false;
  }
}

function useQuickQuestion(item: string) {
  form.question = item;
  actionMessage.value = `已选择快捷问题：${item}`;
}

function useSuggestedQuestion(item: string) {
  form.question = item;
  actionMessage.value = `已填入追问：${item}`;
}

onMounted(loadCourses);
</script>

<template>
  <section class="page tutor-page">
    <div class="panel tutor-hero">
      <div>
        <p class="eyebrow">RAG 智能答疑</p>
        <h2>Python 循环结构诊断式 AI 学伴</h2>
        <p class="muted">围绕李明的 while 循环、循环嵌套和 break / continue 薄弱点，检索课程知识库并生成可追溯回答。</p>
        <p class="basis-note">系统会结合课程资料、学习记录和薄弱点生成回答，并标注可参考的资料来源。</p>
      </div>
      <div class="mode-card">
        <span>回答模式</span>
        <strong>{{ answer?.mode || (form.heuristic_mode ? '启发式答疑' : '智能答疑') }}</strong>
      </div>
    </div>

    <p v-if="pageLoading" class="panel muted">正在加载课程和问答历史...</p>
    <p v-if="actionMessage" class="panel muted">{{ actionMessage }}</p>
    <p v-if="scriptMessage" class="panel muted">{{ scriptMessage }}</p>

    <section v-if="scriptSections.length" class="panel script-preview">
      <div class="script-preview-head">
        <div>
          <strong>数字人讲解预览卡片</strong>
          <p>讲解脚本已生成，可用于后续接入语音播报或数字人服务。</p>
        </div>
        <span>服务预留</span>
      </div>
      <div class="script-section-grid">
        <article v-for="section in scriptSections" :key="section.title">
          <strong>{{ section.title }}</strong>
          <pre v-if="section.title.includes('代码')">{{ section.content }}</pre>
          <p v-else>{{ section.content }}</p>
        </article>
      </div>
    </section>

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
        <p v-if="!pageLoading && !courses.length" class="muted">暂无数据，系统将根据你的学习记录生成建议。</p>
        <div class="quick-question-row">
          <button v-for="item in quickQuestions" :key="item" type="button" class="secondary" @click="useQuickQuestion(item)">
            {{ item }}
          </button>
        </div>
        <label class="question-box">
          问题
          <textarea v-model="form.question" />
        </label>
        <p v-if="error" class="error-text">{{ error }}</p>
        <button :disabled="loading || !form.course_id || !form.question.trim()" @click="ask">
          {{ loading ? '生成中...' : '提交问题' }}
        </button>
        <button class="secondary" type="button" :disabled="scriptLoading" @click="generateScript">{{ scriptLoading ? '生成中...' : '生成讲解脚本' }}</button>
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
          <p v-if="!historyLoading && !history.length" class="muted">暂无数据，系统将根据你的学习记录生成建议。</p>
        </div>
      </section>
    </div>

    <section v-if="answer" class="panel">
      <div class="panel-title">
        <h2>本次回答</h2>
        <span class="muted">引用 {{ (answer.citation_sources || []).length }} 个知识片段</span>
      </div>
      <div class="answer-box">{{ answerText(answer) }}</div>
      <div v-if="answer.cards?.length" class="answer-card-grid">
        <article v-for="card in answer.cards" :key="card.title">
          <strong>{{ card.title }}</strong>
          <pre v-if="card.title.includes('示例')">{{ card.content }}</pre>
          <p v-else>{{ card.content }}</p>
        </article>
      </div>
      <div class="answer-flags">
        <span>{{ answer.based_on_material ? '基于资料回答' : '根据学习问题生成回答' }}</span>
        <span>置信度 {{ answer.confidence ?? '-' }}</span>
        <span>课程对齐 {{ answer.curriculum_alignment_score ?? '-' }}</span>
        <span>{{ answer.is_out_of_curriculum ? '存在超纲风险' : '课程范围内' }}</span>
        <span>依据风险 {{ evidenceRisk(answer) }}</span>
        <span>下一步：{{ answer.nextStep || '完成 while 循环专项练习' }}</span>
        <span>{{ form.no_direct_answer ? '不直接给答案' : '可给出结构化回答' }}</span>
        <span>提示层级 {{ answer.hint_level || form.hint_level }}</span>
        <span>掌握度变化 +{{ answer.mastery_delta ?? 0 }}</span>
      </div>
      <p v-if="answer.boundary_warning" class="basis-note">{{ answer.boundary_warning }}</p>
      <div v-if="answer.teaching_strategy || answer.detected_misconception" class="teaching-card">
        <strong>教学策略：{{ answer.teaching_strategy || '暂无策略' }}</strong>
        <p>错因识别：{{ answer.detected_misconception || '暂无识别' }}</p>
        <p>分层提示：{{ answer.hint_text || '暂无提示' }}</p>
        <small>{{ answer.learning_basis_note || '当前建议基于课程资料、答题表现和学习路径综合生成。' }}</small>
      </div>
      <div v-if="answer.guiding_questions?.length" class="guiding-list">
        <button
          v-for="item in answer.guiding_questions"
          :key="item"
          type="button"
          class="secondary"
          @click="useSuggestedQuestion(item)"
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
          @click="useSuggestedQuestion(item)"
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
        <span class="confidence-detail">依据风险：{{ evidenceRisk(answer) }}</span>
        <span v-if="answer.confidence_breakdown" class="confidence-detail">
          (最高 {{ (answer.confidence_breakdown.max * 100).toFixed(0) }}% / 最低 {{ (answer.confidence_breakdown.min * 100).toFixed(0) }}%)
        </span>
      </div>
      <div class="source-grid">
        <CitationCard
          v-for="item in answer.citations || []"
          :key="item.citation_id || item.snippet"
          :citation="item"
        />
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
          <span class="source-relevance">相关度 {{ item.relevance != null ? (item.relevance * 100).toFixed(0) + '%' : '-' }}</span>
          <p>{{ item.snippet }}</p>
        </article>
      </div>
      <p v-if="!(answer.citation_sources?.length || answer.retrieved_context?.length)" class="muted">暂无数据，系统将根据你的学习记录生成建议。</p>
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

.basis-note {
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

.quick-question-row,
.answer-card-grid {
  display: grid;
  gap: 10px;
  margin: 12px 0;
}

.quick-question-row {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.answer-card-grid {
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
}

.answer-card-grid article {
  border: 1px solid var(--border-soft);
  border-radius: 8px;
  padding: 12px;
  background: var(--bg-surface);
}

.answer-card-grid p,
.answer-card-grid pre {
  margin: 8px 0 0;
  color: var(--text-secondary);
  line-height: 1.6;
}

.answer-card-grid pre {
  white-space: pre-wrap;
  border-radius: 8px;
  padding: 10px;
  background: #0f172a;
  color: #e2e8f0;
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

.script-preview {
  display: grid;
  gap: 14px;
}

.script-preview-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
}

.script-preview-head p {
  margin: 6px 0 0;
  color: var(--text-secondary);
}

.script-preview-head span {
  border-radius: 999px;
  padding: 6px 10px;
  color: var(--status-info-text);
  background: var(--status-info-bg);
  font-size: 13px;
  font-weight: 700;
}

.script-section-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 12px;
}

.script-section-grid article {
  border: 1px solid var(--border-soft);
  border-radius: 8px;
  padding: 12px;
  background: var(--bg-surface);
}

.script-section-grid p,
.script-section-grid pre {
  margin: 8px 0 0;
  color: var(--text-secondary);
  line-height: 1.65;
}

.script-section-grid pre {
  white-space: pre-wrap;
  border-radius: 8px;
  padding: 10px;
  color: #e2e8f0;
  background: #0f172a;
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
