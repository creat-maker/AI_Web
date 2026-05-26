<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue';
import { BarChart, LineChart, PieChart } from 'echarts/charts';
import {
  GridComponent,
  LegendComponent,
  TooltipComponent,
  type GridComponentOption,
  type LegendComponentOption,
  type TooltipComponentOption
} from 'echarts/components';
import * as echarts from 'echarts/core';
import type { BarSeriesOption, LineSeriesOption, PieSeriesOption } from 'echarts/charts';
import type { ComposeOption } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { api } from '../api/client';
import { teacherAnalysisDemoSource } from '../api/mocks';

echarts.use([BarChart, LineChart, PieChart, GridComponent, LegendComponent, TooltipComponent, CanvasRenderer]);

type AnalysisChartOption = ComposeOption<
  | BarSeriesOption
  | LineSeriesOption
  | PieSeriesOption
  | GridComponentOption
  | LegendComponentOption
  | TooltipComponentOption
>;

interface AnalysisData {
  real?: {
    quiz_count?: number;
    submission_count?: number;
    student_count?: number;
    average_score?: number;
    weak_point_count?: number;
    report_count?: number;
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
}

const data = ref<AnalysisData | null>(null);
const loading = ref(true);
const error = ref('');
const trendEl = ref<HTMLDivElement | null>(null);
const weakEl = ref<HTMLDivElement | null>(null);
const distributionEl = ref<HTMLDivElement | null>(null);
let trendChart: echarts.ECharts | null = null;
let weakChart: echarts.ECharts | null = null;
let distributionChart: echarts.ECharts | null = null;

const fallbackWeakPoints = [
  { name: '函数', value: 32 },
  { name: '文件操作', value: 24 },
  { name: 'HTTP 请求', value: 44 }
];

const fallbackDistribution = [
  { name: '优秀', value: 8 },
  { name: '良好', value: 18 },
  { name: '需关注', value: 7 },
  { name: '高风险', value: 3 }
];

function weakPoints() {
  return data.value?.demo?.weak_point_distribution?.length ? data.value.demo.weak_point_distribution : fallbackWeakPoints;
}

function trendItems() {
  return data.value?.trend?.length
    ? data.value.trend
    : [
        { date: 'Day 1', submission_count: 1, average_score: 68 },
        { date: 'Day 2', submission_count: 2, average_score: 72 },
        { date: 'Day 3', submission_count: 2, average_score: 78 },
        { date: 'Day 4', submission_count: 3, average_score: 82 }
      ];
}

function performanceItems() {
  return data.value?.performance_distribution?.length ? data.value.performance_distribution : fallbackDistribution;
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

function riskLevel(value: number) {
  if (value >= 70) return '高风险';
  if (value >= 45) return '中风险';
  return '低风险';
}

function renderCharts() {
  if (!data.value) return;

  if (trendEl.value) {
    trendChart = trendChart || echarts.init(trendEl.value);
    const trend = trendItems();
    const option: AnalysisChartOption = {
      color: ['#2264d1', '#44a36f'],
      tooltip: { trigger: 'axis' },
      legend: { top: 0, right: 0 },
      grid: { left: 36, right: 18, top: 46, bottom: 28 },
      xAxis: { type: 'category', boundaryGap: false, data: trend.map((item) => item.date.slice(5)) },
      yAxis: { type: 'value', minInterval: 1, splitLine: { lineStyle: { color: '#edf1f7' } } },
      series: [
        { name: '测评次数', type: 'bar', barWidth: 14, data: trend.map((item) => item.submission_count) },
        { name: '平均得分', type: 'line', smooth: true, data: trend.map((item) => item.average_score) }
      ]
    };
    trendChart.setOption(option);
  }

  if (weakEl.value) {
    weakChart = weakChart || echarts.init(weakEl.value);
    const points = weakPoints();
    const option: AnalysisChartOption = {
      color: ['#f59f00'],
      tooltip: { trigger: 'axis' },
      grid: { left: 36, right: 18, top: 20, bottom: 28 },
      xAxis: { type: 'category', data: points.map((item) => item.name) },
      yAxis: { type: 'value', max: 100, splitLine: { lineStyle: { color: '#edf1f7' } } },
      series: [{ name: '薄弱程度', type: 'bar', barWidth: 22, data: points.map((item) => item.value) }]
    };
    weakChart.setOption(option);
  }

  if (distributionEl.value) {
    distributionChart = distributionChart || echarts.init(distributionEl.value);
    const option: AnalysisChartOption = {
      color: ['#2264d1', '#44a36f', '#f59f00', '#d64545'],
      tooltip: { trigger: 'item' },
      legend: { bottom: 0 },
      series: [
        {
          name: '学生表现',
          type: 'pie',
          radius: ['45%', '68%'],
          center: ['50%', '44%'],
          data: performanceItems()
        }
      ]
    };
    distributionChart.setOption(option);
  }
}

async function loadAnalysis() {
  loading.value = true;
  error.value = '';
  try {
    data.value = await api.get<AnalysisData>('/api/v1/quizzes/analysis');
    await nextTick();
    renderCharts();
  } catch (err) {
    error.value = err instanceof Error ? err.message : '学情分析数据加载失败';
  } finally {
    loading.value = false;
  }
}

function resizeCharts() {
  trendChart?.resize();
  weakChart?.resize();
  distributionChart?.resize();
}

onMounted(() => {
  loadAnalysis();
  window.addEventListener('resize', resizeCharts);
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeCharts);
  trendChart?.dispose();
  weakChart?.dispose();
  distributionChart?.dispose();
});
</script>

<template>
  <section class="page analysis-page">
    <div class="panel analysis-hero">
      <div>
        <p class="eyebrow">教师学情分析中心</p>
        <h2>班级测评与薄弱点洞察</h2>
        <p class="muted">汇总测评、学生表现、薄弱知识点和教学建议，用于课堂复盘和比赛展示。</p>
      </div>
      <div class="source-card">
        <span>数据来源</span>
        <strong>{{ data?.demo?.source || teacherAnalysisDemoSource }}</strong>
      </div>
    </div>

    <p v-if="error" class="panel error-text">{{ error }}</p>
    <p v-else-if="loading" class="panel muted">正在加载学情分析数据...</p>

    <div v-if="data" class="overview-grid">
      <article class="stat overview-card">
        <span>测评次数</span>
        <strong>{{ data.real?.submission_count ?? data.real?.quiz_count ?? 0 }}</strong>
        <small>次</small>
      </article>
      <article class="stat overview-card">
        <span>参与学生</span>
        <strong>{{ data.real?.student_count || 0 }}</strong>
        <small>人</small>
      </article>
      <article class="stat overview-card">
        <span>平均得分</span>
        <strong>{{ data.real?.average_score || 0 }}</strong>
        <small>分</small>
      </article>
      <article class="stat overview-card">
        <span>薄弱知识点</span>
        <strong>{{ data.real?.weak_point_count ?? weakPoints().length }}</strong>
        <small>个</small>
      </article>
    </div>

    <div v-if="data" class="analysis-layout">
      <section class="panel">
        <div class="panel-title">
          <h2>学情趋势</h2>
          <span class="muted">最近测评次数 / 平均得分</span>
        </div>
        <div ref="trendEl" class="chart"></div>
      </section>

      <section class="panel">
        <div class="panel-title">
          <h2>学生表现分布</h2>
          <span class="muted">优秀 / 良好 / 需关注 / 高风险</span>
        </div>
        <div ref="distributionEl" class="chart"></div>
      </section>
    </div>

    <div v-if="data" class="analysis-layout">
      <section class="panel">
        <div class="panel-title">
          <h2>薄弱知识点分析</h2>
          <span class="muted">错误率 / 薄弱程度</span>
        </div>
        <div ref="weakEl" class="chart"></div>
        <div class="risk-grid">
          <article v-for="item in weakPoints()" :key="item.name" class="risk-card">
            <strong>{{ item.name }}</strong>
            <span :class="['risk-pill', riskLevel(item.value)]">{{ riskLevel(item.value) }}</span>
            <p>{{ item.value }}%</p>
          </article>
        </div>
      </section>

      <section class="panel">
        <div class="panel-title">
          <h2>教学建议</h2>
          <span class="muted">面向下一轮教学</span>
        </div>
        <div class="suggestion-list">
          <article v-for="item in data.teaching_suggestions || []" :key="item.title" class="suggestion-card">
            <strong>{{ item.title }}</strong>
            <p>{{ item.content }}</p>
          </article>
          <p v-if="!data.teaching_suggestions?.length" class="muted">暂无建议，完成测评后会生成教学建议。</p>
        </div>
      </section>
    </div>

    <section v-if="data" class="panel">
      <div class="panel-title">
        <h2>最近报告 / 测评记录</h2>
        <span class="muted">{{ data.recent_records?.length || 0 }} 条记录</span>
      </div>
      <div class="record-grid">
        <article v-for="item in data.recent_records || []" :key="item.id" class="record-card">
          <div>
            <strong>{{ item.title }}</strong>
            <p>{{ item.type === 'report' ? '学习报告' : '测评记录' }} · {{ formatDate(item.created_at) }}</p>
          </div>
          <span>{{ item.status }}{{ item.score !== undefined ? ` · ${item.score} 分` : '' }}</span>
        </article>
        <p v-if="!data.recent_records?.length" class="empty-state">暂无报告或测评记录。</p>
      </div>
    </section>
  </section>
</template>

<style scoped>
.analysis-page {
  gap: 18px;
}

.analysis-hero,
.panel-title,
.record-card {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.analysis-hero {
  align-items: center;
}

.analysis-hero h2 {
  margin: 0 0 8px;
  font-size: 24px;
}

.eyebrow {
  margin: 0 0 6px;
  color: #2264d1;
  font-size: 13px;
  font-weight: 700;
}

.source-card {
  max-width: 360px;
  border: 1px solid #d9e0ea;
  border-radius: 8px;
  padding: 14px;
  background: #f8fbff;
}

.source-card span,
.overview-card small {
  display: block;
  color: #66758a;
}

.source-card strong {
  display: block;
  margin-top: 6px;
  font-size: 13px;
  line-height: 1.5;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}

.overview-card {
  min-height: 112px;
}

.analysis-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(320px, 0.9fr);
  gap: 16px;
}

.chart {
  width: 100%;
  height: 320px;
}

.risk-grid,
.suggestion-list,
.record-grid {
  display: grid;
  gap: 10px;
}

.risk-grid {
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  margin-top: 12px;
}

.risk-card,
.suggestion-card,
.record-card {
  border: 1px solid #e4e9f1;
  border-radius: 8px;
  padding: 12px;
  background: #fbfcff;
}

.risk-card p,
.suggestion-card p,
.record-card p {
  margin: 8px 0 0;
  color: #66758a;
}

.risk-pill,
.record-card span {
  white-space: nowrap;
  border-radius: 999px;
  padding: 5px 8px;
  font-size: 12px;
  color: #1453aa;
  background: #edf4ff;
}

.risk-pill.高风险 {
  color: #b42318;
  background: #fff0f0;
}

.risk-pill.中风险 {
  color: #955600;
  background: #fff7e8;
}

.risk-pill.低风险 {
  color: #1f7a45;
  background: #effaf4;
}

.empty-state {
  margin: 0;
  color: #66758a;
}

.error-text {
  color: #b42318;
}

@media (max-width: 980px) {
  .analysis-layout,
  .analysis-hero,
  .panel-title,
  .record-card {
    display: grid;
  }

  .source-card {
    max-width: none;
  }
}
</style>
