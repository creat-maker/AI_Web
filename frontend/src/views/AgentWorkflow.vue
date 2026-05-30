<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { api } from '../api/client';
import type { Course } from '../types';

type StepStatus = 'waiting' | 'running' | 'success' | 'failed' | string;

interface WorkflowStep {
  key: string;
  name: string;
  status: StepStatus;
  input_summary: string;
  output_summary: string;
  duration?: string;
  duration_ms?: number;
  error?: string;
}

interface WorkflowRecord {
  id: number;
  run_id?: string;
  langgraph_run_id?: string | null;
  task_name?: string;
  workflow_name: string;
  created_at?: string;
  status: StepStatus;
  trigger_source?: string;
  result_entry?: string;
}

interface WorkflowSummary {
  today_run_count: number;
  success_rate: number;
  average_duration: string;
  average_duration_ms?: number;
  artifact_count: number;
}

interface WorkflowArtifacts {
  tutor_answer?: { title?: string; summary?: string };
  knowledge_references?: {
    title?: string;
    count?: number;
    items?: Array<{ source?: string; content?: string }>;
  };
  weak_points?: { title?: string; summary?: string };
  teaching_suggestions?: {
    title?: string;
    items?: Array<{ title?: string; content?: string }>;
  };
  report?: { title?: string; report_id?: number; path?: string; entry?: string };
}

interface WorkflowCenter {
  workflow_summary: WorkflowSummary;
  steps: WorkflowStep[];
  records: WorkflowRecord[];
  artifacts: WorkflowArtifacts;
  workflow_templates?: Array<{ name: string; demo_fallback_note?: string; nodes: WorkflowStep[] }>;
  business_event_records?: Array<{ id: number; event_type: string; title: string; description: string; run_id?: string; status?: string }>;
}

interface FlowResult {
  workflow_summary?: WorkflowSummary;
  steps?: WorkflowStep[];
  artifacts?: WorkflowArtifacts;
  agent_run_id?: number;
  messages?: string[];
}

const stepTemplates: WorkflowStep[] = [
  { key: 'task_receive', name: '任务接收', status: 'waiting', input_summary: '等待提交任务', output_summary: '暂无输出', duration: '-' },
  { key: 'intent_recognition', name: '意图识别', status: 'waiting', input_summary: '等待学习目标', output_summary: '暂无输出', duration: '-' },
  { key: 'knowledge_retrieval', name: '知识库检索', status: 'waiting', input_summary: '等待问题或目标', output_summary: '暂无输出', duration: '-' },
  { key: 'answer_generation', name: '答案生成', status: 'waiting', input_summary: '等待知识片段', output_summary: '暂无输出', duration: '-' },
  { key: 'learning_analysis', name: '学情分析', status: 'waiting', input_summary: '等待薄弱点', output_summary: '暂无输出', duration: '-' },
  { key: 'teaching_advice', name: '教学建议', status: 'waiting', input_summary: '等待分析结果', output_summary: '暂无输出', duration: '-' },
  { key: 'report_generation', name: '报告生成', status: 'waiting', input_summary: '等待工作流汇总', output_summary: '暂无输出', duration: '-' }
];

const fallbackCenter: WorkflowCenter = {
  workflow_summary: {
    today_run_count: 0,
    success_rate: 0,
    average_duration: '暂无',
    artifact_count: 0
  },
  steps: stepTemplates,
  records: [],
  artifacts: {},
  workflow_templates: [],
  business_event_records: []
};

const courses = ref<Course[]>([]);
const center = ref<WorkflowCenter>(fallbackCenter);
const result = ref<FlowResult | null>(null);
const selectedRunId = ref<number | null>(null);
const loading = ref(true);
const running = ref(false);
const error = ref('');
const operationMessage = ref('');
const fallbackActive = ref(false);

const form = reactive({
  course_id: 0,
  student_name: '张三',
  current_level: '基础薄弱',
  learning_goal: '两周内掌握 Python 爬虫基础',
  weak_points_text: '函数,文件操作,HTTP请求',
  learning_preference: '案例驱动',
  question: 'Python 爬虫发送 HTTP 请求的基本步骤是什么？'
});

const summaryCards = computed(() => [
  { label: '今日运行次数', value: center.value.workflow_summary.today_run_count, unit: '次' },
  { label: '成功率', value: center.value.workflow_summary.success_rate, unit: '%' },
  { label: '平均耗时', value: center.value.workflow_summary.average_duration || '暂无', unit: '' },
  { label: '生成产物数量', value: center.value.workflow_summary.artifact_count, unit: '项' }
]);

const visibleSteps = computed(() => {
  if (running.value) {
    return stepTemplates.map((item, index) => ({
      ...item,
      status: index === 0 ? 'running' : 'waiting',
      output_summary: index === 0 ? '正在校验课程、学生和学习目标。' : item.output_summary
    }));
  }
  return center.value.steps?.length ? center.value.steps : stepTemplates;
});

const artifacts = computed(() => center.value.artifacts || {});
const hasArtifacts = computed(() => Boolean(
  artifacts.value.tutor_answer?.summary
  || artifacts.value.knowledge_references?.items?.length
  || artifacts.value.weak_points?.summary
  || artifacts.value.teaching_suggestions?.items?.length
  || artifacts.value.report?.path
  || artifacts.value.report?.report_id
));

function statusText(status?: StepStatus) {
  const map: Record<string, string> = {
    waiting: '等待中',
    running: '运行中',
    success: '成功',
    failed: '失败'
  };
  return map[status || ''] || status || '未知';
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

function courseTitle(courseId: number) {
  return courses.value.find((item) => item.id === courseId)?.title || `课程 #${courseId}`;
}

async function loadCenter() {
  const data = await api.get<WorkflowCenter>('/api/v1/agent-workflow');
  center.value = {
    workflow_summary: data.workflow_summary || fallbackCenter.workflow_summary,
    steps: data.steps?.length ? data.steps : stepTemplates,
    records: data.records || [],
    artifacts: data.artifacts || {},
    workflow_templates: data.workflow_templates || [],
    business_event_records: data.business_event_records || []
  };
}

async function loadPage() {
  loading.value = true;
  error.value = '';
  fallbackActive.value = false;
  try {
    const [courseData] = await Promise.all([
      api.get<Course[]>('/api/v1/courses'),
      loadCenter()
    ]);
    courses.value = courseData;
    form.course_id = form.course_id || courses.value[0]?.id || 0;
  } catch (err) {
    error.value = err instanceof Error ? err.message : '智能体工作流数据加载失败';
    fallbackActive.value = true;
    center.value = fallbackCenter;
  } finally {
    loading.value = false;
  }
}

async function runFlow() {
  if (!form.course_id) {
    error.value = '请先创建或选择课程后再运行工作流。';
    return;
  }
  running.value = true;
  error.value = '';
  operationMessage.value = '';
  fallbackActive.value = false;
  try {
    const data = await api.post<FlowResult>('/api/v1/agent-workflow/run-full-learning-flow', {
      ...form,
      weak_points: form.weak_points_text.split(',').map((item) => item.trim()).filter(Boolean)
    });
    result.value = data;
    center.value = {
      workflow_summary: data.workflow_summary || center.value.workflow_summary,
      steps: data.steps?.length ? data.steps : center.value.steps,
      records: center.value.records,
      artifacts: data.artifacts || center.value.artifacts,
      workflow_templates: center.value.workflow_templates,
      business_event_records: center.value.business_event_records
    };
    await loadCenter();
    operationMessage.value = `工作流运行完成，run_id：${center.value.records[0]?.run_id || `run-${center.value.records[0]?.id || ''}`}`;
  } catch (err) {
    error.value = err instanceof Error ? err.message : '工作流运行失败，已保留页面兜底展示。';
    fallbackActive.value = true;
  } finally {
    running.value = false;
  }
}

async function rerunRecord(record: WorkflowRecord) {
  running.value = true;
  error.value = '';
  operationMessage.value = '';
  try {
    const next = await api.post<WorkflowRecord>(`/api/v1/agent-workflow/runs/${record.id}/rerun`);
    await loadCenter();
    selectedRunId.value = center.value.records[0]?.id || null;
    operationMessage.value = `已完成模拟重跑：${next.run_id || `run-${next.id}`}`;
  } catch (err) {
    error.value = err instanceof Error ? err.message : '模拟重新运行失败';
  } finally {
    running.value = false;
  }
}

onMounted(loadPage);
</script>

<template>
  <section class="page workflow-page">
    <div class="panel workflow-hero">
      <div>
        <p class="eyebrow">教学智能体工作流中心</p>
        <h2>从任务接收到报告生成的教学闭环</h2>
        <p class="muted">展示任务编排、知识库检索、答疑生成、学情分析和教学建议产物，适合比赛现场演示。</p>
        <p class="demo-note">当前为 EduMind 内置 demo/fallback 编排，已预留 langgraph_run_id 字段，未接入真实 LangGraph。</p>
      </div>
      <div class="hero-action">
        <span>当前课程</span>
        <strong>{{ form.course_id ? courseTitle(form.course_id) : '暂无课程' }}</strong>
      </div>
    </div>

    <p v-if="error" class="panel error-text">{{ error }}</p>
    <p v-if="operationMessage" class="panel success-text">{{ operationMessage }}</p>
    <p v-if="fallbackActive" class="panel muted">接口暂不可用，页面已切换到本地 fallback 展示，避免白屏。</p>
    <p v-else-if="loading" class="panel muted">正在加载智能体工作流数据...</p>

    <div class="overview-grid">
      <article v-for="item in summaryCards" :key="item.label" class="stat overview-card">
        <span>{{ item.label }}</span>
        <strong>{{ item.value }}</strong>
        <small>{{ item.unit || ' ' }}</small>
      </article>
    </div>

    <div class="workflow-layout">
      <section class="panel">
        <div class="panel-title">
          <h2>运行参数</h2>
          <span class="muted">提交后生成完整教学工作流</span>
        </div>
        <div class="form-grid">
          <label>课程<select v-model.number="form.course_id"><option v-for="c in courses" :key="c.id" :value="c.id">{{ c.title }}</option></select></label>
          <label>学生<input v-model="form.student_name" /></label>
          <label>水平<input v-model="form.current_level" /></label>
          <label>偏好<input v-model="form.learning_preference" /></label>
          <label>薄弱点<input v-model="form.weak_points_text" /></label>
          <label>学习目标<textarea v-model="form.learning_goal" /></label>
          <label>答疑问题<textarea v-model="form.question" /></label>
          <button :disabled="running || loading" @click="runFlow">{{ running ? '运行中...' : '运行完整学习流' }}</button>
        </div>
      </section>

      <section class="panel">
        <div class="panel-title">
          <h2>最近运行</h2>
          <span class="muted">{{ center.records.length }} 条记录</span>
        </div>
        <div class="record-list">
          <article v-for="item in center.records.slice(0, 5)" :key="item.id" class="record-card">
            <div>
              <strong>{{ item.task_name || item.workflow_name }}</strong>
              <p>{{ item.run_id || `run-${item.id}` }} / {{ item.langgraph_run_id || 'langgraph_run_id 预留' }}</p>
              <p>{{ formatDate(item.created_at) }} · {{ item.trigger_source || '本地页面' }}</p>
            </div>
            <div class="record-actions">
              <span :class="['status-pill', item.status]">{{ statusText(item.status) }}</span>
              <button class="secondary" type="button" :disabled="running" @click="rerunRecord(item)">模拟重跑</button>
              <RouterLink :to="item.result_entry || '/reports'">结果入口</RouterLink>
            </div>
          </article>
          <p v-if="!center.records.length && !loading" class="empty-state">暂无运行记录。提交一次完整学习流后，这里会显示任务名称、状态和结果入口。</p>
        </div>
      </section>
    </div>

    <section class="panel">
      <div class="panel-title">
        <h2>三类 demo 工作流模板</h2>
        <span class="muted">profile_agent / knowledge_agent / planning_agent / generation_agent / review_agent / recommendation_agent</span>
      </div>
      <div class="step-grid">
        <article v-for="template in center.workflow_templates || []" :key="template.name" class="step-card success">
          <div class="step-head">
            <strong>{{ template.name }}</strong>
            <span class="status-pill success">demo</span>
          </div>
          <p class="demo-note">{{ template.demo_fallback_note || '当前为 demo/fallback 模板。' }}</p>
          <dl>
            <template v-for="node in template.nodes" :key="`${template.name}-${node.key}`">
              <dt>{{ node.name }}</dt>
              <dd>{{ node.input_summary }} → {{ node.output_summary }}（{{ node.duration_ms }}ms）</dd>
            </template>
          </dl>
        </article>
      </div>
    </section>

    <section class="panel">
      <div class="panel-title">
        <h2>业务事件联动历史</h2>
        <span class="muted">资源生成 / 路径更新 / 报告生成事件映射为模拟 run_id</span>
      </div>
      <div class="record-list">
        <article v-for="item in center.business_event_records || []" :key="item.id" class="record-card">
          <div>
            <strong>{{ item.title }}</strong>
            <p>{{ item.run_id }} · {{ item.event_type }}</p>
            <p>{{ item.description }}</p>
          </div>
          <span :class="['status-pill', item.status || 'success']">{{ statusText(item.status || 'success') }}</span>
        </article>
        <p v-if="!(center.business_event_records || []).length" class="empty-state">暂无业务事件联动记录。生成资源包、更新路径或重跑工作流后会出现。</p>
      </div>
    </section>

    <section class="panel">
      <div class="panel-title">
        <h2>流程节点</h2>
        <span class="muted">任务接收 / 意图识别 / 检索 / 生成 / 分析 / 建议 / 报告</span>
      </div>
      <div class="step-grid">
        <article v-for="step in visibleSteps" :key="step.key" :class="['step-card', step.status]">
          <div class="step-head">
            <strong>{{ step.name }}</strong>
            <span :class="['status-pill', step.status]">{{ statusText(step.status) }}</span>
          </div>
          <dl>
            <dt>输入摘要</dt>
            <dd>{{ step.input_summary }}</dd>
            <dt>输出摘要</dt>
            <dd>{{ step.output_summary }}</dd>
            <dt>耗时</dt>
            <dd>{{ step.duration || '-' }}</dd>
            <dt v-if="step.error">错误信息</dt>
            <dd v-if="step.error" class="error-text">{{ step.error }}</dd>
          </dl>
        </article>
      </div>
    </section>

    <section class="panel">
      <div class="panel-title">
        <h2>产物摘要</h2>
        <span class="muted">{{ hasArtifacts ? '最近一次运行结果' : '等待生成' }}</span>
      </div>
      <div class="artifact-grid">
        <article class="artifact-card">
          <span>答疑结果</span>
          <p>{{ artifacts.tutor_answer?.summary || '暂无答疑结果，运行完整学习流后展示。' }}</p>
        </article>
        <article class="artifact-card">
          <span>知识库引用</span>
          <p>{{ artifacts.knowledge_references?.count || 0 }} 条引用</p>
          <ul v-if="artifacts.knowledge_references?.items?.length">
            <li v-for="item in artifacts.knowledge_references.items" :key="`${item.source}-${item.content}`">
              {{ item.source }}：{{ item.content }}
            </li>
          </ul>
        </article>
        <article class="artifact-card">
          <span>薄弱点分析</span>
          <p>{{ artifacts.weak_points?.summary || '暂无薄弱点分析。' }}</p>
        </article>
        <article class="artifact-card">
          <span>教学建议</span>
          <div v-if="artifacts.teaching_suggestions?.items?.length" class="suggestion-list">
            <p v-for="item in artifacts.teaching_suggestions.items" :key="item.title">
              <strong>{{ item.title }}</strong>：{{ item.content }}
            </p>
          </div>
          <p v-else>暂无教学建议。</p>
        </article>
        <article class="artifact-card report-card">
          <span>报告入口</span>
          <p>{{ artifacts.report?.path || '暂无报告文件。' }}</p>
          <RouterLink :to="artifacts.report?.entry || '/reports'">查看报告中心</RouterLink>
        </article>
      </div>
    </section>
  </section>
</template>

<style scoped>
.workflow-page {
  gap: 18px;
}

.workflow-hero,
.panel-title,
.record-card,
.step-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.workflow-hero {
  align-items: center;
}

.workflow-hero h2 {
  margin: 0 0 8px;
  font-size: 24px;
}

.eyebrow {
  margin: 0 0 6px;
  color: #2264d1;
  font-size: 13px;
  font-weight: 700;
}

.demo-note {
  margin: 8px 0 0;
  color: #955600;
  font-size: 13px;
}

.hero-action {
  width: 260px;
  border: 1px solid #d9e0ea;
  border-radius: 8px;
  padding: 14px;
  background: #f8fbff;
}

.hero-action span,
.overview-card small,
.artifact-card span {
  display: block;
  color: #66758a;
}

.hero-action strong {
  display: block;
  margin-top: 6px;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}

.overview-card {
  min-height: 112px;
}

.workflow-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(320px, 0.8fr);
  gap: 16px;
}

.record-list,
.suggestion-list {
  display: grid;
  gap: 10px;
}

.record-card,
.step-card,
.artifact-card {
  border: 1px solid #e4e9f1;
  border-radius: 8px;
  padding: 12px;
  background: #fbfcff;
}

.record-card {
  align-items: center;
}

.record-card p,
.artifact-card p,
.artifact-card ul {
  margin: 8px 0 0;
  color: #66758a;
  line-height: 1.55;
}

.record-actions {
  display: flex;
  gap: 8px;
  align-items: center;
  white-space: nowrap;
}

.record-actions a,
.report-card a {
  color: #2264d1;
  text-decoration: none;
  font-weight: 700;
}

.step-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 12px;
}

.step-card {
  border-left: 4px solid #cfd9e8;
}

.step-card.running {
  border-left-color: #f59f00;
  background: #fffaf0;
}

.step-card.success {
  border-left-color: #44a36f;
}

.step-card.failed {
  border-left-color: #d64545;
  background: #fff8f8;
}

.step-card dl {
  margin: 12px 0 0;
}

.step-card dt {
  margin-top: 10px;
  color: #66758a;
  font-size: 12px;
}

.step-card dd {
  margin: 4px 0 0;
  line-height: 1.5;
}

.status-pill {
  border-radius: 999px;
  padding: 5px 8px;
  font-size: 12px;
  color: #1453aa;
  background: #edf4ff;
}

.status-pill.running {
  color: #955600;
  background: #fff7e8;
}

.status-pill.success {
  color: #1f7a45;
  background: #effaf4;
}

.status-pill.failed {
  color: #b42318;
  background: #fff0f0;
}

.artifact-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}

.artifact-card strong {
  color: #1c2430;
}

.artifact-card ul {
  padding-left: 18px;
}

.empty-state {
  margin: 0;
  color: #66758a;
}

.error-text {
  color: #b42318;
}

.success-text {
  color: #1f7a45;
}

@media (max-width: 980px) {
  .workflow-layout,
  .workflow-hero,
  .panel-title,
  .record-card,
  .step-head {
    display: grid;
  }

  .hero-action {
    width: auto;
  }

  .record-actions {
    white-space: normal;
  }
}
</style>
