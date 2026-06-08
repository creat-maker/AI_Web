<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue';
import { RouterLink } from 'vue-router';
import { LineChart, PieChart, RadarChart } from 'echarts/charts';
import {
  GridComponent,
  LegendComponent,
  RadarComponent,
  TooltipComponent
} from 'echarts/components';
import * as echarts from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { api } from '../api/client';
import DataCard from '../components/DataCard.vue';
import EmptyState from '../components/EmptyState.vue';
import PageHeader from '../components/PageHeader.vue';
import ProgressBar from '../components/ProgressBar.vue';
import StatCard from '../components/StatCard.vue';
import StatusBadge from '../components/StatusBadge.vue';

echarts.use([LineChart, PieChart, RadarChart, GridComponent, LegendComponent, RadarComponent, TooltipComponent, CanvasRenderer]);

function cssVar(name: string, fallback: string) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim() || fallback;
}

const chartTextStyle = { color: cssVar('--text-secondary', '#475569') };
const chartTooltip = { backgroundColor: cssVar('--bg-card', '#ffffff'), borderColor: cssVar('--border-light', '#e2e8f0'), textStyle: { color: cssVar('--text-main', '#0f172a') } };

interface DashboardSummary {
  metrics?: {
    course_count?: number;
    qa_count?: number;
    report_count?: number;
  };
  student_risk_stats?: {
    risk_student_count?: number;
    weak_points?: Array<{ name: string; count: number }>;
  };
  tutor_chat_stats?: {
    today_questions?: number;
  };
  warning_items?: Array<{ module: string; level: string; message: string; count: number }>;
}

interface AnalysisData {
  summary?: {
    student_count?: number;
    average_score?: number;
  };
  knowledge_tracking?: {
    teacher_intervention_suggestions?: Array<{ title: string; content: string }>;
  };
}

const loading = ref(true);
const error = ref('');
const summary = ref<DashboardSummary | null>(null);
const analysis = ref<AnalysisData | null>(null);
const trendEl = ref<HTMLDivElement | null>(null);
const donutEl = ref<HTMLDivElement | null>(null);
const radarEl = ref<HTMLDivElement | null>(null);
let trendChart: echarts.ECharts | null = null;
let donutChart: echarts.ECharts | null = null;
let radarChart: echarts.ECharts | null = null;

const courses = [
  { name: 'Python 爬虫基础与实践', className: '计科大三 1 班', students: 32, progress: 72, tone: 'success' as const },
  { name: '人工智能导论', className: '计科大三 2 班', students: 48, progress: 65, tone: 'primary' as const },
  { name: '数据结构与算法', className: '计科大二 1 班', students: 38, progress: 58, tone: 'primary' as const },
  { name: 'Web 开发技术', className: '计科大二 2 班', students: 30, progress: 41, tone: 'warning' as const }
];

const student = {
  name: '张三',
  className: '计科大三 1 班',
  number: '2021123456',
  score: 86,
  abilities: [
    { name: '编程能力', value: 82 },
    { name: '算法思维', value: 88 },
    { name: '数据处理', value: 75 },
    { name: '工程实践', value: 70 },
    { name: '问题解决', value: 90 },
    { name: '学习态度', value: 85 }
  ]
};

const reminders = computed(() => [
  { title: '有 18 份作业待批改', desc: 'Python 爬虫基础与实践 · 第 5 次作业', tone: 'danger' as const },
  { title: `收到 ${summary.value?.tutor_chat_stats?.today_questions || 7} 个新的答疑问题`, desc: '来自计科大三 1 班', tone: 'warning' as const },
  { title: '课程「人工智能导论」即将开始', desc: '下次课时间：明天 10:00', tone: 'info' as const },
  { title: '张三的学习进度有明显提升', desc: '近 7 天进步了 12 分', tone: 'success' as const }
]);

const weakPoints = computed(() => summary.value?.student_risk_stats?.weak_points || [
  { name: 'HTTP 请求流程', count: 42 },
  { name: 'BeautifulSoup 解析', count: 38 },
  { name: '正则表达式', count: 34 },
  { name: '异常处理', count: 28 },
  { name: '数据清洗', count: 24 }
]);

const suggestions = computed(() => analysis.value?.knowledge_tracking?.teacher_intervention_suggestions || [
  { title: '分层布置 HTTP 请求专项任务', content: '建议对进度低于 60% 的学生推送 15 分钟微练习，并关联答疑记录。' },
  { title: '加强解析与异常处理讲解', content: '集中薄弱点出现在数据解析环节，可在下一节课加入案例复盘。' }
]);

const statCards = computed(() => [
  { label: '我的课程', value: summary.value?.metrics?.course_count || 4, unit: '门', hint: '较上月', trend: '+1', icon: '课' },
  { label: '学生总数', value: analysis.value?.summary?.student_count || 128, unit: '人', hint: '较上月', trend: '+12', icon: '学', tone: 'green' as const },
  { label: '平均学习进度', value: '68.5', unit: '%', hint: '较上月', trend: '+6.2%', icon: '进', tone: 'purple' as const },
  { label: '待批改作业', value: 18, unit: '份', hint: '较昨日', trend: '-5', icon: '批', tone: 'orange' as const },
  { label: '待答疑问题', value: summary.value?.tutor_chat_stats?.today_questions || 23, unit: '条', hint: '较昨日', trend: '-3', icon: '问', tone: 'cyan' as const }
]);

function renderCharts() {
  if (trendEl.value) {
    trendChart = trendChart || echarts.init(trendEl.value);
    trendChart.setOption({
      color: [cssVar('--color-primary', '#2f6bff'), cssVar('--status-success-solid', '#22c55e')],
      textStyle: chartTextStyle,
      tooltip: { trigger: 'axis', ...chartTooltip },
      legend: { top: 0, left: 0, textStyle: chartTextStyle },
      grid: { left: 34, right: 16, top: 42, bottom: 26 },
      xAxis: { type: 'category', boundaryGap: false, axisLabel: chartTextStyle, data: ['04-20', '04-27', '05-04', '05-11', '05-18'] },
      yAxis: { type: 'value', min: 0, max: 100, axisLabel: { ...chartTextStyle, formatter: '{value}%' }, splitLine: { lineStyle: { color: cssVar('--border-soft', '#edf2f8') } } },
      series: [
        { name: '班级平均', type: 'line', smooth: true, areaStyle: { opacity: 0.08 }, data: [24, 40, 50, 62, 72] },
        { name: '优秀学生', type: 'line', smooth: true, areaStyle: { opacity: 0.08 }, data: [34, 56, 71, 78, 82] }
      ]
    });
  }
  if (donutEl.value) {
    donutChart = donutChart || echarts.init(donutEl.value);
    donutChart.setOption({
      color: [cssVar('--status-success-solid', '#22c55e'), cssVar('--color-primary', '#2f6bff'), cssVar('--border-light', '#dbe2ef')],
      textStyle: chartTextStyle,
      tooltip: { trigger: 'item', ...chartTooltip },
      legend: { orient: 'vertical', right: 0, top: 'middle', textStyle: chartTextStyle },
      series: [
        {
          name: '任务完成情况',
          type: 'pie',
          radius: ['52%', '74%'],
          center: ['38%', '50%'],
          label: { formatter: '{b}\n{c}' },
          data: [
            { name: '已完成', value: 98 },
            { name: '进行中', value: 36 },
            { name: '未开始', value: 22 }
          ]
        }
      ]
    });
  }
  if (radarEl.value) {
    radarChart = radarChart || echarts.init(radarEl.value);
    radarChart.setOption({
      color: [cssVar('--color-primary', '#2f6bff')],
      radar: {
        radius: '68%',
        indicator: student.abilities.map((item) => ({ name: item.name, max: 100 })),
        splitLine: { lineStyle: { color: cssVar('--border-link', '#dbe7ff') } },
        splitArea: { areaStyle: { color: [cssVar('--bg-surface', '#f8fbff'), cssVar('--color-primary-light', '#eef4ff')] } },
        axisLine: { lineStyle: { color: cssVar('--border-light', '#c8d6f0') } }
      },
      series: [{ type: 'radar', areaStyle: { opacity: 0.14 }, data: [{ value: student.abilities.map((item) => item.value) }] }]
    });
  }
}

async function loadPage() {
  loading.value = true;
  error.value = '';
  try {
    const [summaryResult, analysisResult] = await Promise.allSettled([
      api.get<DashboardSummary>('/api/dashboard/summary'),
      api.get<AnalysisData>('/api/v1/quizzes/analysis')
    ]);
    if (summaryResult.status === 'fulfilled') summary.value = summaryResult.value;
    if (analysisResult.status === 'fulfilled') analysis.value = analysisResult.value;
    if (summaryResult.status === 'rejected' && analysisResult.status === 'rejected') {
      error.value = '后端暂不可用，当前显示演示数据。';
    }
  } finally {
    loading.value = false;
    await nextTick();
    renderCharts();
  }
}

function resizeCharts() {
  trendChart?.resize();
  donutChart?.resize();
  radarChart?.resize();
}

onMounted(() => {
  loadPage();
  window.addEventListener('resize', resizeCharts);
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeCharts);
  trendChart?.dispose();
  donutChart?.dispose();
  radarChart?.dispose();
});
</script>

<template>
  <section class="page teacher-dashboard">
    <PageHeader title="上午好，王老师" description="欢迎回来，今天重点关注课程进度、待批改作业和学生画像。">
      <template #actions>
        <RouterLink class="btn secondary" to="/courses">新建课程</RouterLink>
        <RouterLink class="btn" to="/reports">生成报告</RouterLink>
      </template>
    </PageHeader>

    <p v-if="loading" class="panel muted">正在加载教师端班级概览...</p>

    <div class="stat-grid">
      <StatCard v-for="item in statCards" :key="item.label" v-bind="item" />
    </div>

    <DataCard title="班级学情闭环看板" subtitle="新增班级完成率、平均正确率、学习活跃度、薄弱知识点排行和风险学生干预建议。">
      <div class="insight-grid">
        <article class="insight-card">
          <span>班级完成率</span>
          <strong>78%</strong>
          <ProgressBar :value="78" tone="success" />
        </article>
        <article class="insight-card">
          <span>平均正确率</span>
          <strong>82%</strong>
          <ProgressBar :value="82" tone="primary" />
        </article>
        <article class="insight-card">
          <span>学习活跃度</span>
          <strong>91%</strong>
          <ProgressBar :value="91" tone="success" />
        </article>
      </div>
      <div class="intervention-grid">
        <section>
          <h3>薄弱知识点排行</h3>
          <article v-for="item in [
            { name: '文件操作', value: 42 },
            { name: '循环结构', value: 37 },
            { name: '函数返回值', value: 31 },
            { name: '异常处理', value: 28 }
          ]" :key="item.name" class="rank-row">
            <span>{{ item.name }}</span>
            <ProgressBar :value="item.value" tone="warning" />
            <strong>{{ item.value }}</strong>
          </article>
        </section>
        <section>
          <h3>风险学生与干预建议</h3>
          <article v-for="student in [
            { name: '王五', risk: '高风险', weak: '文件操作 / 异常处理', suggestion: '推送文件读写分步讲义，布置 15 分钟补救任务，提醒话术：先完成最小可运行代码，再补异常。' },
            { name: '赵六', risk: '需关注', weak: '循环结构', suggestion: '安排循环边界二刷，课堂中点名讲解一次变量变化表。' },
            { name: '孙七', risk: '需关注', weak: '函数', suggestion: '推荐函数封装案例包，要求提交参数和返回值说明。' }
          ]" :key="student.name" class="risk-row">
            <div>
              <strong>{{ student.name }}</strong>
              <p>{{ student.weak }}</p>
              <p>{{ student.suggestion }}</p>
            </div>
            <StatusBadge :label="student.risk" :tone="student.risk === '高风险' ? 'danger' : 'warning'" />
          </article>
        </section>
      </div>
    </DataCard>

    <div class="teacher-main-grid">
      <DataCard title="课程管理" subtitle="课程、班级、学生数与学习进度">
        <template #action>
          <RouterLink class="text-link" to="/courses">查看全部</RouterLink>
        </template>
        <table class="table course-overview-table">
          <thead>
            <tr>
              <th>课程名称</th>
              <th>班级</th>
              <th>学生数</th>
              <th>学习进度</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="course in courses" :key="course.name">
              <td>
                <strong>{{ course.name }}</strong>
                <span>2024 春季学期</span>
              </td>
              <td>{{ course.className }}</td>
              <td>{{ course.students }}</td>
              <td>
                <div class="table-progress">
                  <span>{{ course.progress }}%</span>
                  <ProgressBar :value="course.progress" :tone="course.tone" />
                </div>
              </td>
              <td><button class="secondary">详情</button></td>
            </tr>
          </tbody>
        </table>
      </DataCard>

      <DataCard title="学生画像分析" subtitle="综合评分、能力雷达与个性化建议">
        <template #action>
          <RouterLink class="text-link" to="/profiles">查看全部学生</RouterLink>
        </template>
        <div class="student-profile-card">
          <div class="student-head">
            <span class="student-avatar">张</span>
            <div>
              <strong>{{ student.name }}</strong>
              <p>{{ student.className }} | 学号：{{ student.number }}</p>
            </div>
            <div class="student-score">
              <span>综合评分</span>
              <strong>{{ student.score }}</strong><small>/100</small>
            </div>
          </div>
          <div class="profile-analysis-grid">
            <div ref="radarEl" class="small-chart"></div>
            <div class="ability-list">
              <div v-for="item in student.abilities" :key="item.name" class="ability-item">
                <span>{{ item.name }}</span>
                <ProgressBar :value="item.value" />
                <strong>{{ item.value }}/100</strong>
              </div>
              <RouterLink class="btn secondary report-button" to="/reports">生成个性化学习报告</RouterLink>
            </div>
          </div>
        </div>
      </DataCard>
    </div>

    <div class="three-panel-grid">
      <DataCard title="学习进度趋势" subtitle="近 30 天班级平均与优秀学生趋势">
        <div ref="trendEl" class="chart-box"></div>
      </DataCard>

      <DataCard title="学习任务完成情况" subtitle="总任务 156">
        <div ref="donutEl" class="chart-box"></div>
      </DataCard>

      <DataCard title="近期提醒" subtitle="待处理事项与系统建议">
        <div class="list">
          <div v-for="item in reminders" :key="item.title" class="reminder-item">
            <StatusBadge :label="item.tone === 'danger' ? '待处理' : item.tone === 'success' ? '进步' : '提醒'" :tone="item.tone" />
            <div>
              <strong>{{ item.title }}</strong>
              <p>{{ item.desc }}</p>
            </div>
          </div>
        </div>
      </DataCard>
    </div>

    <div class="role-layout">
      <DataCard title="薄弱知识点 TOP5" subtitle="基于测评和答疑记录聚合">
        <div class="weak-bars">
          <div v-for="item in weakPoints.slice(0, 5)" :key="item.name">
            <span>{{ item.name }}</span>
            <ProgressBar :value="Math.min(100, item.count * 1.6)" />
            <strong>{{ item.count }}%</strong>
          </div>
        </div>
      </DataCard>

      <DataCard title="教学建议" subtitle="下一步干预动作">
        <div v-if="suggestions.length" class="list">
          <div v-for="item in suggestions" :key="item.title" class="item">
            <strong>{{ item.title }}</strong>
            <p>{{ item.content }}</p>
          </div>
        </div>
        <EmptyState v-else title="暂无教学提醒" description="教师分析接口返回知识追踪建议后会显示。" />
      </DataCard>
    </div>
  </section>
</template>

<style scoped>
.teacher-main-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(420px, 0.98fr);
  gap: 16px;
}

.course-overview-table td:first-child span {
  display: block;
  margin-top: 4px;
  color: var(--color-text-sub);
  font-size: 12px;
}

.table-progress {
  display: grid;
  grid-template-columns: 44px minmax(100px, 1fr);
  gap: 8px;
  align-items: center;
  min-width: 160px;
}

.student-profile-card {
  display: grid;
  gap: 16px;
}

.student-head {
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid var(--color-border);
  padding-bottom: 14px;
}

.student-avatar {
  display: inline-grid;
  place-items: center;
  width: 58px;
  height: 58px;
  border-radius: 50%;
  color: var(--text-light);
  font-size: 22px;
  font-weight: 800;
  background: linear-gradient(135deg, var(--status-info-text), var(--color-primary));
}

.student-head p {
  margin: 4px 0 0;
}

.student-score {
  margin-left: auto;
  text-align: right;
}

.student-score span,
.student-score small {
  color: var(--color-text-sub);
}

.student-score strong {
  color: var(--color-success);
  font-size: 30px;
}

.profile-analysis-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px;
}

.ability-list,
.weak-bars {
  display: grid;
  gap: 11px;
}

.ability-item,
.weak-bars div {
  display: grid;
  grid-template-columns: 76px minmax(0, 1fr) 56px;
  gap: 10px;
  align-items: center;
  color: var(--color-text-sub);
  font-size: 13px;
}

.ability-item strong,
.weak-bars strong {
  color: var(--color-text-main);
  font-size: 12px;
}

.report-button {
  width: 100%;
  margin-top: 4px;
}

.three-panel-grid {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(280px, 0.9fr) minmax(320px, 0.9fr);
  gap: 16px;
}

.reminder-item {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 10px;
  align-items: start;
  border-bottom: 1px solid var(--border-table);
  padding-bottom: 10px;
}

.reminder-item:last-child {
  border-bottom: 0;
  padding-bottom: 0;
}

.reminder-item p {
  margin: 4px 0 0;
  font-size: 13px;
}

.insight-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.insight-card,
.intervention-grid section,
.risk-row {
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 12px;
  background: #fff;
}

.insight-card {
  display: grid;
  gap: 8px;
}

.insight-card span,
.rank-row span,
.risk-row p {
  color: var(--color-text-sub);
  font-size: 13px;
}

.insight-card strong {
  font-size: 24px;
}

.intervention-grid {
  display: grid;
  grid-template-columns: minmax(0, 0.85fr) minmax(0, 1.15fr);
  gap: 14px;
}

.intervention-grid h3 {
  margin: 0 0 12px;
  font-size: 16px;
}

.rank-row {
  display: grid;
  grid-template-columns: 92px minmax(0, 1fr) 44px;
  gap: 10px;
  align-items: center;
  margin-bottom: 10px;
}

.risk-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}

.risk-row p {
  margin: 5px 0 0;
}

@media (max-width: 1280px) {
  .teacher-main-grid,
  .three-panel-grid,
  .intervention-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 720px) {
  .profile-analysis-grid,
  .student-head,
  .insight-grid {
    display: grid;
    grid-template-columns: 1fr;
  }

  .student-score {
    margin-left: 0;
    text-align: left;
  }
}
</style>
