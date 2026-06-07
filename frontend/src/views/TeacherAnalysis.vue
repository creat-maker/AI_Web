<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue';
import { BarChart, LineChart, PieChart } from 'echarts/charts';
import { GridComponent, LegendComponent, TooltipComponent } from 'echarts/components';
import * as echarts from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { api } from '../api/client';
import { teacherAnalysisDemoSource } from '../api/mocks';
import DataCard from '../components/DataCard.vue';
import EmptyState from '../components/EmptyState.vue';
import PageHeader from '../components/PageHeader.vue';
import ProgressBar from '../components/ProgressBar.vue';
import StatCard from '../components/StatCard.vue';
import StatusBadge from '../components/StatusBadge.vue';

echarts.use([BarChart, LineChart, PieChart, GridComponent, LegendComponent, TooltipComponent, CanvasRenderer]);

function cssVar(name: string, fallback: string) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim() || fallback;
}

const chartTextStyle = { color: cssVar('--text-secondary', '#475569') };
const chartTooltip = { backgroundColor: cssVar('--bg-card', '#ffffff'), borderColor: cssVar('--border-light', '#e2e8f0'), textStyle: { color: cssVar('--text-main', '#0f172a') } };

interface AnalysisData {
  real?: {
    quiz_count?: number;
    submission_count?: number;
    student_count?: number;
    average_score?: number;
    weak_point_count?: number;
  };
  demo?: {
    source?: string;
    weak_point_distribution?: Array<{ name: string; value: number }>;
  };
  trend?: Array<{ date: string; submission_count: number; average_score: number }>;
  performance_distribution?: Array<{ name: string; value: number }>;
  recent_records?: Array<{
    id: string;
    title: string;
    type: string;
    score?: number;
    status: string;
    created_at?: string;
  }>;
  teaching_suggestions?: Array<{ title: string; content: string }>;
  knowledge_tracking?: {
    weak_knowledge_top5?: Array<{ name: string; value: number }>;
    teacher_intervention_suggestions?: Array<{ title: string; content: string }>;
  };
}

const data = ref<AnalysisData | null>(null);
const loading = ref(true);
const error = ref('');
const distributionEl = ref<HTMLDivElement | null>(null);
const trendEl = ref<HTMLDivElement | null>(null);
let distributionChart: echarts.ECharts | null = null;
let trendChart: echarts.ECharts | null = null;

const fallbackWeakPoints = [
  { name: 'HTTP 请求', value: 44 },
  { name: '函数封装', value: 38 },
  { name: '数据解析', value: 35 },
  { name: '异常处理', value: 28 },
  { name: '文件操作', value: 24 }
];

const fallbackDistribution = [
  { name: '90-100', value: 18 },
  { name: '80-89', value: 32 },
  { name: '70-79', value: 28 },
  { name: '60-69', value: 14 },
  { name: '<60', value: 8 }
];

const quizzes = computed(() => {
  const records = data.value?.recent_records?.length ? data.value.recent_records : [
    { id: 'q1', title: 'Python 爬虫基础测验', type: 'quiz', score: 86, status: '已完成', created_at: '2026-05-30T10:20:00' },
    { id: 'q2', title: '数据结构章节测验', type: 'quiz', score: 78, status: '待批改', created_at: '2026-05-29T18:30:00' },
    { id: 'q3', title: 'HTTP 请求专项练习', type: 'quiz', score: 92, status: '已完成', created_at: '2026-05-28T09:00:00' },
    { id: 'q4', title: 'RAG 系统原理测验', type: 'quiz', score: 73, status: '进行中', created_at: '2026-05-27T14:10:00' }
  ];
  return records.filter((item) => item.type !== 'report').slice(0, 6);
});

const weakPoints = computed(() => data.value?.knowledge_tracking?.weak_knowledge_top5?.length ? data.value.knowledge_tracking.weak_knowledge_top5 : (data.value?.demo?.weak_point_distribution?.length ? data.value.demo.weak_point_distribution : fallbackWeakPoints));
const suggestions = computed(() => data.value?.knowledge_tracking?.teacher_intervention_suggestions?.length ? data.value.knowledge_tracking.teacher_intervention_suggestions : (data.value?.teaching_suggestions?.length ? data.value.teaching_suggestions : [
  { title: '拆分 HTTP 请求案例', content: '建议把请求、解析、存储拆成三段演示，并补充异常处理检查点。' },
  { title: '分层布置练习', content: '对 70 分以下学生布置基础题，对 85 分以上学生增加项目挑战。' },
  { title: '课后答疑复盘', content: '将高频答疑问题整理为知识卡片，同步到知识库。' }
]));

const statCards = computed(() => [
  { label: '测验数量', value: data.value?.real?.quiz_count || quizzes.value.length, unit: '次', hint: '本月测验', icon: '测' },
  { label: '参与人数', value: data.value?.real?.student_count || 128, unit: '人', hint: '覆盖班级', icon: '人', tone: 'green' as const },
  { label: '平均分', value: data.value?.real?.average_score || 76.5, unit: '分', hint: '较上周 +3.2', icon: '分', tone: 'purple' as const },
  { label: '及格率', value: 88, unit: '%', hint: '60 分以上', icon: '及', tone: 'cyan' as const },
  { label: '待批改', value: 18, unit: '份', hint: '需尽快处理', icon: '批', tone: 'orange' as const }
]);

const heatmapRows = ['HTTP 请求', '数据解析', '函数封装', '异常处理', '文件操作'];
const heatmapClasses = ['计科大三 1 班', '计科大三 2 班', '计科大二 1 班', '计科大二 2 班'];

function heatValue(row: number, col: number) {
  return [92, 78, 64, 58, 86, 72, 61, 55, 80, 76, 68, 63, 74, 66, 59, 52, 88, 70, 65, 57][row * 4 + col] || 60;
}

function heatClass(value: number) {
  if (value >= 80) return 'good';
  if (value >= 65) return 'mid';
  return 'low';
}

function renderCharts() {
  if (distributionEl.value) {
    distributionChart = distributionChart || echarts.init(distributionEl.value);
    const items = data.value?.performance_distribution?.length ? data.value.performance_distribution : fallbackDistribution;
    distributionChart.setOption({
      color: [cssVar('--color-primary', '#2f6bff')],
      textStyle: chartTextStyle,
      tooltip: { trigger: 'axis', ...chartTooltip },
      grid: { left: 36, right: 12, top: 24, bottom: 28 },
      xAxis: { type: 'category', axisLabel: chartTextStyle, data: items.map((item) => item.name) },
      yAxis: { type: 'value', axisLabel: chartTextStyle, splitLine: { lineStyle: { color: cssVar('--border-soft', '#edf2f8') } } },
      series: [{ type: 'bar', barWidth: 28, data: items.map((item) => item.value), itemStyle: { borderRadius: [8, 8, 0, 0] } }]
    });
  }
  if (trendEl.value) {
    trendChart = trendChart || echarts.init(trendEl.value);
    const trend = data.value?.trend?.length ? data.value.trend : [
      { date: '05-01', submission_count: 12, average_score: 68 },
      { date: '05-08', submission_count: 18, average_score: 72 },
      { date: '05-15', submission_count: 24, average_score: 75 },
      { date: '05-22', submission_count: 28, average_score: 78 },
      { date: '05-31', submission_count: 36, average_score: 82 }
    ];
    trendChart.setOption({
      color: [cssVar('--color-purple', '#7c5cff'), cssVar('--status-success-solid', '#22c55e')],
      textStyle: chartTextStyle,
      tooltip: { trigger: 'axis', ...chartTooltip },
      legend: { top: 0, left: 0, textStyle: chartTextStyle },
      grid: { left: 36, right: 14, top: 42, bottom: 28 },
      xAxis: { type: 'category', boundaryGap: false, axisLabel: chartTextStyle, data: trend.map((item) => item.date.slice(-5)) },
      yAxis: { type: 'value', axisLabel: chartTextStyle, splitLine: { lineStyle: { color: cssVar('--border-soft', '#edf2f8') } } },
      series: [
        { name: '参与次数', type: 'line', smooth: true, data: trend.map((item) => item.submission_count) },
        { name: '平均分', type: 'line', smooth: true, data: trend.map((item) => item.average_score) }
      ]
    });
  }
}

function formatDate(value?: string) {
  if (!value) return '暂无时间';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
}

function statusTone(status?: string) {
  if (status === '已完成' || status === 'completed') return 'success';
  if (status === '待批改') return 'warning';
  if (status === '进行中') return 'purple';
  return 'neutral';
}

async function loadAnalysis() {
  loading.value = true;
  error.value = '';
  try {
    data.value = await api.get<AnalysisData>('/api/v1/quizzes/analysis');
  } catch (err) {
    error.value = err instanceof Error ? err.message : '教师分析接口暂不可用，当前显示演示数据。';
    data.value = {};
  } finally {
    loading.value = false;
    await nextTick();
    renderCharts();
  }
}

function resizeCharts() {
  distributionChart?.resize();
  trendChart?.resize();
}

onMounted(() => {
  loadAnalysis();
  window.addEventListener('resize', resizeCharts);
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeCharts);
  distributionChart?.dispose();
  trendChart?.dispose();
});
</script>

<template>
  <section class="page analysis-page">
    <PageHeader title="测验评价与教师分析" description="汇总测验结果、成绩分布、知识点掌握和教学建议。">
      <template #actions>
        <button class="secondary">导出分析</button>
        <button>生成教学建议</button>
      </template>
    </PageHeader>

    <p v-if="loading" class="panel muted">正在加载测验分析数据...</p>

    <div class="stat-grid">
      <StatCard v-for="item in statCards" :key="item.label" v-bind="item" />
    </div>

    <div class="analysis-layout">
      <DataCard title="测验列表" subtitle="最近测验、成绩和批改状态">
        <template #action>
          <StatusBadge :label="data?.demo?.source || teacherAnalysisDemoSource" tone="info" />
        </template>
        <div class="quiz-list">
          <article v-for="quiz in quizzes" :key="quiz.id" class="quiz-row">
            <div>
              <strong>{{ quiz.title }}</strong>
              <p>{{ formatDate(quiz.created_at) }} · {{ quiz.score ?? '-' }} 分</p>
            </div>
            <StatusBadge :label="quiz.status" :tone="statusTone(quiz.status)" />
          </article>
        </div>
      </DataCard>

      <DataCard title="成绩分布图" subtitle="按分数区间统计">
        <div ref="distributionEl" class="chart-box"></div>
      </DataCard>
    </div>

    <div class="analysis-layout">
      <DataCard title="测验趋势" subtitle="参与次数与平均分变化">
        <div ref="trendEl" class="chart-box"></div>
      </DataCard>

      <DataCard title="薄弱知识点 TOP5" subtitle="错误率与掌握不足">
        <div class="weak-list">
          <div v-for="item in weakPoints.slice(0, 5)" :key="item.name" class="weak-row">
            <span>{{ item.name }}</span>
            <ProgressBar :value="item.value" :tone="item.value > 40 ? 'warning' : 'primary'" />
            <strong>{{ item.value }}%</strong>
          </div>
        </div>
      </DataCard>
    </div>

    <DataCard title="知识点掌握热力图" subtitle="横向对比班级在关键知识点上的掌握情况">
      <div class="heatmap">
        <div class="heat-head"></div>
        <div v-for="className in heatmapClasses" :key="className" class="heat-head">{{ className }}</div>
        <template v-for="(point, rowIndex) in heatmapRows" :key="point">
          <div class="heat-label">{{ point }}</div>
          <div
            v-for="(_, colIndex) in heatmapClasses"
            :key="`${point}-${colIndex}`"
            :class="['heat-cell', heatClass(heatValue(rowIndex, colIndex))]"
          >
            {{ heatValue(rowIndex, colIndex) }}%
          </div>
        </template>
      </div>
    </DataCard>

    <DataCard title="教学建议" subtitle="面向下一轮课堂优化">
      <div class="suggestion-grid">
        <article v-for="item in suggestions" :key="item.title" class="item">
          <strong>{{ item.title }}</strong>
          <p>{{ item.content }}</p>
        </article>
      </div>
      <EmptyState v-if="!suggestions.length" title="暂无建议" description="完成测验分析后会显示。" />
    </DataCard>
  </section>
</template>

<style scoped>
.analysis-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(360px, 0.85fr);
  gap: 16px;
}

.quiz-list,
.weak-list,
.suggestion-grid {
  display: grid;
  gap: 12px;
}

.quiz-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  border-bottom: 1px solid var(--border-table);
  padding-bottom: 10px;
}

.quiz-row:last-child {
  border-bottom: 0;
  padding-bottom: 0;
}

.quiz-row p {
  margin: 4px 0 0;
  font-size: 13px;
}

.weak-row {
  display: grid;
  grid-template-columns: 92px minmax(0, 1fr) 46px;
  gap: 10px;
  align-items: center;
}

.heatmap {
  display: grid;
  grid-template-columns: 140px repeat(4, minmax(130px, 1fr));
  gap: 8px;
  overflow-x: auto;
}

.heat-head,
.heat-label,
.heat-cell {
  border-radius: 12px;
  padding: 10px;
  text-align: center;
}

.heat-head,
.heat-label {
  color: var(--color-text-sub);
  background: var(--bg-surface);
  font-weight: 700;
}

.heat-cell.good {
  color: var(--status-success-text);
  background: var(--status-success-bg);
}

.heat-cell.mid {
  color: var(--status-warning-text);
  background: var(--status-warning-bg);
}

.heat-cell.low {
  color: var(--status-danger-solid);
  background: var(--status-danger-bg);
}

.suggestion-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

@media (max-width: 1180px) {
  .analysis-layout,
  .suggestion-grid {
    grid-template-columns: 1fr;
  }
}
</style>
