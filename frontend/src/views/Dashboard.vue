<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue';
import { BarChart, LineChart } from 'echarts/charts';
import {
  GridComponent,
  LegendComponent,
  TooltipComponent,
  type GridComponentOption,
  type LegendComponentOption,
  type TooltipComponentOption
} from 'echarts/components';
import * as echarts from 'echarts/core';
import type { BarSeriesOption, LineSeriesOption } from 'echarts/charts';
import type { ComposeOption } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { api } from '../api/client';

echarts.use([BarChart, LineChart, GridComponent, LegendComponent, TooltipComponent, CanvasRenderer]);

type DashboardChartOption = ComposeOption<
  | BarSeriesOption
  | LineSeriesOption
  | GridComponentOption
  | LegendComponentOption
  | TooltipComponentOption
>;

interface DashboardSummary {
  metrics: {
    course_count: number;
    document_count: number;
    qa_count: number;
    report_count: number;
    quiz_submission_count: number;
    knowledge_chunk_count: number;
  };
  overview_cards?: Array<{ key: string; label: string; value: number | string; unit?: string }>;
  module_health?: Array<{ module: string; status: string; message: string }>;
  knowledge_base_stats?: {
    document_count: number;
    indexed_document_count: number;
    chunk_count: number;
    coverage_rate: number;
    quality_score: number;
  };
  tutor_chat_stats?: { total_questions: number; today_questions: number; citation_enabled: boolean };
  agent_run_stats?: { total_runs: number; today_runs: number; failed_runs: number; latest_status: string };
  report_stats?: { total_reports: number; today_reports: number };
  student_risk_stats?: {
    risk_student_count: number;
    weak_points: Array<{ name: string; count: number }>;
    items: Array<{ student_name: string; risk_level: string; reason: string }>;
  };
  warning_items?: Array<{ module: string; level: string; message: string; count: number }>;
  data_loop?: { steps: Array<{ name: string; done: boolean }> };
  knowledge_base: {
    status: 'empty' | 'building' | 'ready' | string;
    parsed_document_count: number;
    document_count: number;
  };
  recent_documents: RecentDocument[];
  recent_questions: RecentQuestion[];
}

interface RecentDocument {
  id: number;
  filename: string;
  course_id: number;
  status: string;
  chunk_count: number;
  created_at?: string;
}

interface RecentQuestion {
  id: number;
  course_id: number;
  workflow_name: string;
  question?: string;
  status: string;
  created_at?: string;
  source?: string;
}

interface DashboardActivity {
  trend: Array<{
    date: string;
    documents: number;
    questions: number;
    reports: number;
  }>;
  recent_activity: Array<{
    type: string;
    title: string;
    status: string;
    created_at?: string;
  }>;
}

interface DemoStatus {
  status: string;
  passed: number;
  total: number;
  pass_rate: string;
  report_path: string;
  last_checked_at: string;
  message: string;
}

const summary = ref<DashboardSummary | null>(null);
const activity = ref<DashboardActivity | null>(null);
const demoStatus = ref<DemoStatus | null>(null);
const loading = ref(true);
const error = ref('');
const chartEl = ref<HTMLDivElement | null>(null);
let chart: echarts.ECharts | null = null;

const metricCards = [
  { key: 'course_count', label: '课程数量', unit: '门' },
  { key: 'document_count', label: '文档数量', unit: '份' },
  { key: 'qa_count', label: '问答次数', unit: '次' },
  { key: 'report_count', label: '报告数量', unit: '份' },
  { key: 'quiz_submission_count', label: '测评记录', unit: '次' },
  { key: 'knowledge_chunk_count', label: '知识切片', unit: '段' }
] as const;

const dashboardCards = computed(() => {
  if (summary.value?.overview_cards?.length) return summary.value.overview_cards;
  return metricCards.map((card) => ({
    key: card.key,
    label: card.label,
    value: summary.value?.metrics[card.key] ?? 0,
    unit: card.unit
  }));
});

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

function statusText(status?: string) {
  const map: Record<string, string> = {
    empty: '待构建',
    building: '构建中',
    ready: '已就绪',
    parsed: '已解析',
    parsing: '解析中',
    generated: '已生成',
    answered: '已回答',
    completed: '已完成',
    success: '成功',
    running: '运行中',
    failed: '失败',
    warning: '需关注',
    demo: '演示数据',
    indexed: '已入库',
    fallback: '降级演示'
  };
  return map[status || ''] || status || '未知';
}

function renderChart() {
  if (!chartEl.value || !activity.value) return;
  chart = chart || echarts.init(chartEl.value);
  const trend = activity.value.trend;
  const option: DashboardChartOption = {
    color: ['#2264d1', '#44a36f', '#f59f00'],
    tooltip: { trigger: 'axis' },
    legend: { top: 0, right: 0 },
    grid: { left: 36, right: 18, top: 46, bottom: 28 },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: trend.map((item) => item.date.slice(5))
    },
    yAxis: {
      type: 'value',
      minInterval: 1,
      splitLine: { lineStyle: { color: '#edf1f7' } }
    },
    series: [
      {
        name: '文档上传',
        type: 'line',
        smooth: true,
        areaStyle: { opacity: 0.08 },
        data: trend.map((item) => item.documents)
      },
      {
        name: '智能问答',
        type: 'line',
        smooth: true,
        areaStyle: { opacity: 0.08 },
        data: trend.map((item) => item.questions)
      },
      {
        name: '报告生成',
        type: 'bar',
        barWidth: 14,
        data: trend.map((item) => item.reports)
      }
    ]
  };
  chart.setOption(option);
}

async function loadDashboard() {
  loading.value = true;
  error.value = '';
  try {
    const [summaryData, activityData] = await Promise.all([
      api.get<DashboardSummary>('/api/dashboard/summary'),
      api.get<DashboardActivity>('/api/dashboard/activity')
    ]);
    summary.value = summaryData;
    activity.value = activityData;
    demoStatus.value = await api.get<DemoStatus>('/api/v1/demo-status').catch(() => null);
    await nextTick();
    renderChart();
  } catch (err) {
    error.value = err instanceof Error ? err.message : 'Dashboard 数据加载失败';
  } finally {
    loading.value = false;
  }
}

function resizeChart() {
  chart?.resize();
}

onMounted(() => {
  loadDashboard();
  window.addEventListener('resize', resizeChart);
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeChart);
  chart?.dispose();
});
</script>

<template>
  <section class="page dashboard-page">
    <div class="dashboard-hero panel">
      <div>
        <p class="eyebrow">教学运行总览</p>
        <h2>EduMind 数据看板</h2>
        <p class="muted">汇总课程、知识库、问答、测评和报告产出，适合比赛演示时快速说明系统闭环。</p>
      </div>
      <div class="kb-status" :class="summary?.knowledge_base.status || 'empty'">
        <span>知识库状态</span>
        <strong>{{ statusText(summary?.knowledge_base.status) }}</strong>
        <small>{{ summary?.knowledge_base.parsed_document_count ?? 0 }} / {{ summary?.knowledge_base.document_count ?? 0 }} 份文档已解析</small>
      </div>
    </div>

    <p v-if="error" class="panel error-text">{{ error }}</p>
    <p v-else-if="loading" class="panel muted">正在加载 Dashboard 数据...</p>

    <section v-if="demoStatus" class="panel demo-status-card">
      <div>
        <p class="eyebrow">比赛演示状态</p>
        <h2>{{ demoStatus.status === 'ready' ? 'Ready' : demoStatus.status === 'missing_report' ? 'Missing Report' : 'Warning' }}</h2>
        <p class="muted">{{ demoStatus.message }}</p>
      </div>
      <div class="demo-status-metrics">
        <strong>{{ demoStatus.passed }}/{{ demoStatus.total }}</strong>
        <span>{{ demoStatus.pass_rate }} · {{ demoStatus.last_checked_at || '未验收' }}</span>
        <RouterLink class="text-link" to="/demo-status">进入比赛演示模式</RouterLink>
      </div>
    </section>

    <div v-if="summary" class="dashboard-grid">
      <article v-for="card in dashboardCards" :key="card.key" class="stat metric-card">
        <span>{{ card.label }}</span>
        <strong>{{ card.value }}</strong>
        <small>{{ card.unit }}</small>
      </article>
    </div>

    <div v-if="summary" class="dashboard-layout">
      <section class="panel">
        <div class="panel-title">
          <h2>模块健康状态</h2>
          <span class="muted">面向比赛演示的运行总控</span>
        </div>
        <div class="table-list">
          <div v-for="item in summary.module_health || []" :key="item.module" class="table-row">
            <div>
              <strong>{{ item.module }}</strong>
              <p>{{ item.message }}</p>
            </div>
            <span>{{ statusText(item.status) }}</span>
          </div>
          <p v-if="!summary.module_health?.length" class="muted">暂无模块健康状态，后端统计接口恢复后会自动展示。</p>
        </div>
      </section>

      <section class="panel">
        <div class="panel-title">
          <h2>数据闭环概览</h2>
          <span class="muted">资料到报告的链路</span>
        </div>
        <div class="loop-list">
          <span v-for="step in summary.data_loop?.steps || []" :key="step.name" :class="['loop-step', { done: step.done }]">
            {{ step.name }}
          </span>
        </div>
        <div class="weak-list">
          <small v-for="item in summary.student_risk_stats?.weak_points || []" :key="item.name">
            {{ item.name }} x{{ item.count }}
          </small>
          <p v-if="!summary.student_risk_stats?.weak_points?.length" class="muted">暂无集中薄弱点，完成测评或生成学生画像后会显示。</p>
        </div>
      </section>
    </div>

    <div class="dashboard-layout">
      <section class="panel trend-panel">
        <div class="panel-title">
          <h2>最近 7 天趋势</h2>
          <span class="muted">文档上传 / 智能问答 / 报告生成</span>
        </div>
        <div ref="chartEl" class="trend-chart"></div>
      </section>

      <section class="panel">
        <div class="panel-title">
          <h2>最近活动</h2>
          <span class="muted">系统关键动作</span>
        </div>
        <div class="activity-list">
          <div v-for="item in activity?.recent_activity || []" :key="`${item.type}-${item.title}-${item.created_at}`" class="activity-item">
            <span class="activity-dot" :class="item.type"></span>
            <div>
              <strong>{{ item.title }}</strong>
              <p>{{ statusText(item.status) }} · {{ formatDate(item.created_at) }}</p>
            </div>
          </div>
          <p v-if="!activity?.recent_activity?.length" class="muted">暂无活动记录，完成一次上传或工作流后会显示在这里。</p>
        </div>
      </section>
    </div>

    <div class="dashboard-layout">
      <section class="panel">
        <div class="panel-title">
          <h2>最近上传文档</h2>
          <span class="muted">知识库输入</span>
        </div>
        <div class="table-list">
          <div v-for="doc in summary?.recent_documents || []" :key="doc.id" class="table-row">
            <div>
              <strong>{{ doc.filename }}</strong>
              <p>课程 #{{ doc.course_id }} · {{ doc.chunk_count }} 个切片</p>
            </div>
            <span>{{ statusText(doc.status) }}</span>
          </div>
          <p v-if="!summary?.recent_documents?.length" class="muted">暂无上传文档。</p>
        </div>
      </section>

      <section class="panel">
        <div class="panel-title">
          <h2>最近问答记录</h2>
          <span class="muted">可扩展为真实问答日志</span>
        </div>
        <div class="table-list">
          <div v-for="question in summary?.recent_questions || []" :key="question.id" class="table-row">
            <div>
              <strong>{{ question.question || question.workflow_name }}</strong>
              <p>课程 #{{ question.course_id }} · {{ formatDate(question.created_at) }}</p>
            </div>
            <span>{{ statusText(question.status) }}</span>
          </div>
          <p v-if="!summary?.recent_questions?.length" class="muted">暂无真实问答记录，后续接入问答日志表即可展示。</p>
        </div>
      </section>
    </div>
  </section>
</template>

<style scoped>
.dashboard-page {
  gap: 18px;
}

.dashboard-hero {
  display: flex;
  justify-content: space-between;
  gap: 18px;
  align-items: center;
}

.demo-status-card {
  display: flex;
  justify-content: space-between;
  gap: 16px;
  align-items: center;
  border-left: 4px solid #2264d1;
}

.demo-status-card h2 {
  margin: 0 0 8px;
}

.demo-status-metrics {
  display: grid;
  gap: 6px;
  min-width: 220px;
  text-align: right;
}

.demo-status-metrics strong {
  color: #1453aa;
  font-size: 28px;
}

.dashboard-hero h2 {
  margin: 0 0 8px;
  font-size: 24px;
}

.eyebrow {
  margin: 0 0 6px;
  color: #2264d1;
  font-size: 13px;
  font-weight: 700;
}

.kb-status {
  min-width: 220px;
  border: 1px solid #d9e0ea;
  border-radius: 8px;
  padding: 14px;
  background: #f8fbff;
}

.kb-status span,
.kb-status small,
.metric-card small {
  display: block;
  color: #66758a;
}

.kb-status strong {
  display: block;
  margin: 6px 0;
  font-size: 24px;
}

.kb-status.ready {
  border-color: #bce7cc;
  background: #f1fbf5;
}

.kb-status.building {
  border-color: #ffe1ad;
  background: #fff8eb;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
}

.metric-card {
  min-height: 112px;
}

.metric-card strong {
  margin-top: 8px;
}

.dashboard-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.45fr) minmax(320px, 0.9fr);
  gap: 16px;
}

.panel-title {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: baseline;
  margin-bottom: 10px;
}

.panel-title h2 {
  margin: 0;
}

.trend-chart {
  width: 100%;
  height: 320px;
}

.activity-list,
.table-list,
.weak-list {
  display: grid;
  gap: 10px;
}

.loop-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.loop-step,
.weak-list small {
  border-radius: 999px;
  padding: 6px 9px;
  color: #955600;
  background: #fff7e8;
}

.loop-step.done {
  color: #1f7a45;
  background: #effaf4;
}

.activity-item,
.table-row {
  display: flex;
  gap: 10px;
  align-items: center;
  justify-content: space-between;
  border: 1px solid #e4e9f1;
  border-radius: 8px;
  padding: 10px 12px;
  background: #fbfcff;
}

.activity-item {
  justify-content: flex-start;
}

.activity-item p,
.table-row p {
  margin: 4px 0 0;
  color: #66758a;
  font-size: 13px;
}

.table-row span {
  white-space: nowrap;
  color: #1453aa;
  background: #edf4ff;
  border-radius: 999px;
  padding: 5px 8px;
  font-size: 12px;
}

.activity-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #2264d1;
  flex: 0 0 auto;
}

.activity-dot.report {
  background: #44a36f;
}

.activity-dot.agent {
  background: #f59f00;
}

.error-text {
  color: #b42318;
}

@media (max-width: 1100px) {
  .dashboard-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .dashboard-hero,
  .panel-title,
  .table-row {
    display: grid;
  }

  .kb-status {
    min-width: 0;
  }
}
</style>
