<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue';
import { RouterLink } from 'vue-router';
import { LineChart, PieChart } from 'echarts/charts';
import {
  GridComponent,
  LegendComponent,
  TooltipComponent
} from 'echarts/components';
import * as echarts from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { api } from '../api/client';
import DataCard from '../components/DataCard.vue';
import PageHeader from '../components/PageHeader.vue';
import ProgressBar from '../components/ProgressBar.vue';
import StatCard from '../components/StatCard.vue';
import StatusBadge from '../components/StatusBadge.vue';

echarts.use([LineChart, PieChart, GridComponent, LegendComponent, TooltipComponent, CanvasRenderer]);

function cssVar(name: string, fallback: string) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim() || fallback;
}

const chartTextStyle = { color: cssVar('--text-secondary', '#475569') };
const chartTooltip = { backgroundColor: cssVar('--bg-card', '#ffffff'), borderColor: cssVar('--border-light', '#e2e8f0'), textStyle: { color: cssVar('--text-main', '#0f172a') } };

interface DashboardSummary {
  metrics: {
    course_count: number;
    document_count: number;
    qa_count: number;
    report_count: number;
    quiz_submission_count: number;
    knowledge_chunk_count: number;
  };
  module_health?: Array<{ module: string; status: string; message: string }>;
  knowledge_base?: {
    status: string;
    parsed_document_count: number;
    document_count: number;
  };
  agent_run_stats?: { total_runs: number; today_runs: number; failed_runs: number; latest_status: string };
  warning_items?: Array<{ module: string; level: string; message: string; count: number }>;
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
const growthEl = ref<HTMLDivElement | null>(null);
const roleEl = ref<HTMLDivElement | null>(null);
let growthChart: echarts.ECharts | null = null;
let roleChart: echarts.ECharts | null = null;

const courses = [
  { name: 'Python 爬虫基础与实践', teacher: '王老师', type: '技术课程', students: 1256, progress: 78, status: '进行中' },
  { name: '机器学习与数据挖掘', teacher: '张老师', type: '技术课程', students: 856, progress: 62, status: '进行中' },
  { name: '前端开发入门到进阶', teacher: '李老师', type: '技术课程', students: 642, progress: 45, status: '进行中' },
  { name: '数据结构与算法', teacher: '陈老师', type: '基础课程', students: 987, progress: 91, status: '进行中' },
  { name: '数学建模与应用', teacher: '刘老师', type: '通识课程', students: 554, progress: 35, status: '即将开始' }
];

const statCards = computed(() => [
  { label: '活跃课程', value: summary.value?.metrics.course_count || 128, unit: '门', hint: '较上月', trend: '+12.5%', icon: '课' },
  { label: '注册学生', value: '8,345', unit: '人', hint: '较上月', trend: '+8.6%', icon: '学', tone: 'red' as const },
  { label: '学习完成率', value: '76.3', unit: '%', hint: '较上月', trend: '+5.2%', icon: '率', tone: 'cyan' as const },
  { label: '资源总数', value: summary.value?.metrics.document_count || 2846, unit: '份', hint: '较上月', trend: '+15.3%', icon: '资', tone: 'purple' as const },
  { label: 'AI 生成次数', value: summary.value?.metrics.qa_count || 18620, unit: '次', hint: '较上月', trend: '+21.7%', icon: 'AI', tone: 'orange' as const },
  { label: '系统健康度', value: '99.8', unit: '%', hint: '运行正常', icon: '稳', tone: 'green' as const }
]);

const serviceStatus = computed(() => {
  const modules = summary.value?.module_health;
  if (modules?.length) {
    return modules.slice(0, 4).map((item) => ({
      name: item.module,
      desc: item.message,
      status: item.status === 'ready' || item.status === 'success' ? '正常' : '关注'
    }));
  }
  return [
    { name: '课务器状态', desc: '课程和任务服务响应正常', status: '正常' },
    { name: '数据库', desc: 'SQLite fallback / demo 数据可用', status: '正常' },
    { name: '存储服务', desc: '资源与报告目录可访问', status: '正常' },
    { name: 'AI 服务', desc: '演示模式可降级运行', status: '正常' }
  ];
});

function statusText(status?: string) {
  const map: Record<string, string> = {
    success: '成功',
    running: '运行中',
    failed: '失败',
    warning: '警告',
    ready: '正常',
    demo: '演示数据',
    generated: '已生成',
    completed: '已完成'
  };
  return map[status || ''] || status || '未知';
}

function formatDate(value?: string) {
  if (!value) return '刚刚';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '时间异常';
  return date.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
}

function renderCharts() {
  if (growthEl.value) {
    growthChart = growthChart || echarts.init(growthEl.value);
    const trend = activity.value?.trend?.length ? activity.value.trend : [
      { date: '2024-05-01', documents: 420, questions: 160, reports: 18 },
      { date: '2024-05-08', documents: 612, questions: 320, reports: 30 },
      { date: '2024-05-15', documents: 720, questions: 410, reports: 42 },
      { date: '2024-05-22', documents: 1040, questions: 680, reports: 68 },
      { date: '2024-05-31', documents: 1088, questions: 720, reports: 86 }
    ];
    growthChart.setOption({
      color: [cssVar('--color-primary', '#2f6bff'), cssVar('--status-success-solid', '#22c55e')],
      textStyle: chartTextStyle,
      tooltip: { trigger: 'axis', ...chartTooltip },
      legend: { top: 0, left: 0, textStyle: chartTextStyle },
      grid: { left: 36, right: 14, top: 42, bottom: 26 },
      xAxis: { type: 'category', boundaryGap: false, axisLabel: chartTextStyle, data: trend.map((item) => item.date.slice(5)) },
      yAxis: { type: 'value', axisLabel: chartTextStyle, splitLine: { lineStyle: { color: cssVar('--border-soft', '#edf2f8') } } },
      series: [
        { name: '新增学生', type: 'line', smooth: true, areaStyle: { opacity: 0.08 }, data: trend.map((item) => item.documents) },
        { name: '活跃学生', type: 'line', smooth: true, areaStyle: { opacity: 0.08 }, data: trend.map((item) => item.questions) }
      ]
    });
  }
  if (roleEl.value) {
    roleChart = roleChart || echarts.init(roleEl.value);
    roleChart.setOption({
      color: [cssVar('--color-primary', '#2f6bff'), cssVar('--status-warning-solid', '#f59e0b'), cssVar('--status-success-solid', '#22c55e'), cssVar('--color-purple', '#7c5cff')],
      textStyle: chartTextStyle,
      tooltip: { trigger: 'item', ...chartTooltip },
      legend: { orient: 'vertical', right: 0, top: 'middle', textStyle: chartTextStyle },
      series: [
        {
          type: 'pie',
          radius: ['48%', '72%'],
          center: ['36%', '50%'],
          label: { formatter: '{b}\n{c}' },
          data: [
            { name: '学生', value: 1638 },
            { name: '教师', value: 343 },
            { name: '助教', value: 98 },
            { name: '管理员', value: 77 }
          ]
        }
      ]
    });
  }
}

async function loadDashboard() {
  loading.value = true;
  error.value = '';
  try {
    const [summaryResult, activityResult, demoResult] = await Promise.allSettled([
      api.get<DashboardSummary>('/api/dashboard/summary'),
      api.get<DashboardActivity>('/api/dashboard/activity'),
      api.get<DemoStatus>('/api/v1/demo-status')
    ]);
    if (summaryResult.status === 'fulfilled') summary.value = summaryResult.value;
    if (activityResult.status === 'fulfilled') activity.value = activityResult.value;
    if (demoResult.status === 'fulfilled') demoStatus.value = demoResult.value;
    if (summaryResult.status === 'rejected' && activityResult.status === 'rejected') {
      error.value = '后端暂不可用，当前显示演示数据。';
    }
  } finally {
    loading.value = false;
    await nextTick();
    renderCharts();
  }
}

function resizeCharts() {
  growthChart?.resize();
  roleChart?.resize();
}

onMounted(() => {
  loadDashboard();
  window.addEventListener('resize', resizeCharts);
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeCharts);
  growthChart?.dispose();
  roleChart?.dispose();
});
</script>

<template>
  <section class="page admin-dashboard">
    <PageHeader title="欢迎回来，Admin" description="今天是平台运营总览，重点关注课程、用户、AI 生成和系统健康度。">
      <template #actions>
        <button class="secondary">2024-05-01 → 2024-05-31</button>
        <RouterLink class="btn" to="/resource-generation">新建生成任务</RouterLink>
      </template>
    </PageHeader>

    <p v-if="loading" class="panel muted">正在加载平台总览...</p>

    <div class="stat-grid admin-stats">
      <StatCard v-for="item in statCards" :key="item.label" v-bind="item" />
    </div>

    <div class="admin-layout">
      <DataCard title="课程管理" subtitle="平台课程数据、进度与审核状态">
        <template #action>
          <RouterLink class="text-link" to="/admin/courses">查看全部</RouterLink>
        </template>
        <div class="filter-row">
          <input placeholder="搜索课程名称、教师、分类..." />
          <select><option>全部类型</option><option>技术课程</option><option>基础课程</option></select>
          <select><option>全部状态</option><option>进行中</option><option>即将开始</option></select>
        </div>
        <table class="table admin-course-table">
          <thead>
            <tr>
              <th>课程名称</th>
              <th>教师</th>
              <th>类型</th>
              <th>学生数</th>
              <th>进度</th>
              <th>状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="course in courses" :key="course.name">
              <td><strong>{{ course.name }}</strong></td>
              <td>{{ course.teacher }}</td>
              <td><StatusBadge :label="course.type" :tone="course.type === '基础课程' ? 'purple' : 'info'" /></td>
              <td>{{ course.students }}</td>
              <td>
                <div class="table-progress">
                  <span>{{ course.progress }}%</span>
                  <ProgressBar :value="course.progress" :tone="course.progress > 70 ? 'success' : course.progress < 45 ? 'warning' : 'primary'" />
                </div>
              </td>
              <td><StatusBadge :label="course.status" :tone="course.status === '进行中' ? 'success' : 'info'" /></td>
              <td><button class="ghost">查看</button></td>
            </tr>
          </tbody>
        </table>
      </DataCard>

      <div class="admin-side">
        <DataCard title="用户增长趋势" subtitle="本月新增与活跃用户">
          <div ref="growthEl" class="small-chart"></div>
        </DataCard>

        <DataCard title="角色分布" subtitle="学生、教师、助教与管理员">
          <div ref="roleEl" class="small-chart"></div>
        </DataCard>
      </div>
    </div>

    <div class="admin-bottom-grid">
      <div class="bottom-section">
        <div class="section-header">
          <h2>最近工作流运行</h2>
          <p class="muted">Agent 执行记录</p>
        </div>
        <div class="list">
          <div v-for="item in activity?.recent_activity?.slice(0, 4) || []" :key="`${item.title}-${item.created_at}`" class="workflow-row">
            <div>
              <strong>{{ item.title }}</strong>
              <p>{{ formatDate(item.created_at) }}</p>
            </div>
            <StatusBadge :label="statusText(item.status)" :tone="item.status === 'failed' ? 'danger' : item.status === 'running' ? 'purple' : 'success'" />
          </div>
          <div v-if="!activity?.recent_activity?.length" class="workflow-row">
            <div>
              <strong>智能出卷工作流</strong>
              <p>由 Admin 触发 · 2 分钟前</p>
            </div>
            <StatusBadge label="成功" tone="success" />
          </div>
        </div>
      </div>

      <div class="bottom-section">
        <div class="section-header">
          <h2>系统日志与告警</h2>
          <p class="muted">错误、警告与信息流</p>
        </div>
        <div class="list">
          <div v-for="item in summary?.warning_items?.slice(0, 4) || []" :key="`${item.module}-${item.message}`" class="workflow-row">
            <div>
              <strong>{{ item.message }}</strong>
              <p>{{ item.module }} · {{ item.count }} 条</p>
            </div>
            <StatusBadge :label="item.level" :tone="item.level === 'error' ? 'danger' : 'warning'" />
          </div>
          <template v-if="!summary?.warning_items?.length">
            <div class="workflow-row"><strong>AI 服务响应延迟较高</strong><StatusBadge label="警告" tone="warning" /></div>
            <div class="workflow-row"><strong>资源生成失败：存储空间不足</strong><StatusBadge label="错误" tone="danger" /></div>
            <div class="workflow-row"><strong>用户登录成功：张老师</strong><StatusBadge label="信息" tone="info" /></div>
          </template>
        </div>
      </div>

      <div class="bottom-section">
        <div class="section-header">
          <h2>系统能量状态</h2>
          <p class="muted">服务健康与可用性</p>
        </div>
        <div class="service-list">
          <div v-for="item in serviceStatus" :key="item.name" class="service-item">
            <div>
              <strong>{{ item.name }}</strong>
              <p>{{ item.desc }}</p>
            </div>
            <StatusBadge :label="item.status" :tone="item.status === '正常' ? 'success' : 'warning'" />
          </div>
        </div>
        <div v-if="demoStatus" class="demo-mini">
          <strong>验收状态：{{ demoStatus.passed }}/{{ demoStatus.total }}</strong>
          <span>{{ demoStatus.message }}</span>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.admin-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 16px;
  align-items: start;
}

.admin-side {
  display: grid;
  gap: 16px;
}

.filter-row {
  display: grid;
  grid-template-columns: minmax(240px, 1fr) 160px 160px;
  gap: 10px;
  margin-bottom: 14px;
}

.table-progress {
  display: grid;
  grid-template-columns: 42px minmax(90px, 1fr);
  gap: 8px;
  align-items: center;
  min-width: 150px;
}

.admin-bottom-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.bottom-section {
  border: 1px solid var(--color-border);
  border-radius: var(--card-radius);
  padding: 16px;
  background: var(--bg-card);
}

.section-header {
  margin-bottom: 12px;
}

.section-header h2 {
  margin: 0;
  font-size: 15px;
  color: var(--color-text-main);
}

.section-header p {
  margin: 4px 0 0;
  font-size: 13px;
}

.workflow-row,
.service-item {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  border-bottom: 1px solid var(--border-table);
  padding-bottom: 10px;
}

.workflow-row:last-child,
.service-item:last-child {
  border-bottom: 0;
  padding-bottom: 0;
}

.workflow-row p,
.service-item p {
  margin: 4px 0 0;
  font-size: 13px;
}

.service-list {
  display: grid;
  gap: 10px;
}

.demo-mini {
  display: grid;
  gap: 4px;
  margin-top: 14px;
  border-radius: 14px;
  padding: 12px;
  color: var(--color-primary-dark);
  background: var(--color-primary-light);
}

.demo-mini span {
  color: var(--color-text-sub);
  font-size: 13px;
}

@media (max-width: 1280px) {
  .admin-layout,
  .admin-bottom-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .filter-row {
    grid-template-columns: 1fr;
  }

  .workflow-row,
  .service-item {
    display: grid;
  }
}
</style>
