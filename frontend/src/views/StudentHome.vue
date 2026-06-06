<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue';
import { RouterLink } from 'vue-router';
import { LineChart } from 'echarts/charts';
import { GridComponent, TooltipComponent } from 'echarts/components';
import * as echarts from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { api } from '../api/client';
import DataCard from '../components/DataCard.vue';
import EmptyState from '../components/EmptyState.vue';
import PageHeader from '../components/PageHeader.vue';
import ProgressBar from '../components/ProgressBar.vue';
import StatCard from '../components/StatCard.vue';
import StatusBadge from '../components/StatusBadge.vue';

echarts.use([LineChart, GridComponent, TooltipComponent, CanvasRenderer]);

const chartTextStyle = { color: '#475569' };
const chartTooltip = { backgroundColor: '#ffffff', borderColor: '#e2e8f0', textStyle: { color: '#0f172a' } };

interface DashboardSummary {
  metrics?: {
    report_count?: number;
    quiz_submission_count?: number;
  };
  recent_questions?: Array<{ question?: string; status?: string; created_at?: string }>;
}

interface ReportItem {
  id: number;
  title: string;
  status?: string;
  generated_at?: string;
  quality_score?: number;
}

interface Course {
  id: number;
  title: string;
  subject?: string;
  teacher_name?: string;
  description?: string;
}

const loading = ref(true);
const error = ref('');
const summary = ref<DashboardSummary | null>(null);
const reports = ref<ReportItem[]>([]);
const courses = ref<Course[]>([]);
const events = ref<Array<{ id: number; event_type: string; title: string; description: string; metadata?: Record<string, any> }>>([]);
const reportChartEl = ref<HTMLDivElement | null>(null);
let reportChart: echarts.ECharts | null = null;

const fallbackCourses = [
  { id: 1, title: 'Python 爬虫基础与实践', subject: 'Python', teacher_name: '王老师' },
  { id: 2, title: '数据结构与算法', subject: '算法', teacher_name: '陈老师' },
  { id: 3, title: '人工智能导论', subject: 'AI', teacher_name: '张老师' },
  { id: 4, title: '计算机网络原理', subject: '网络', teacher_name: '李老师' }
];

function cleanText(value: string | undefined, fallback: string) {
  if (!value || /[?]{2,}|�/.test(value)) return fallback;
  return value;
}

const courseCards = computed(() => {
  const source = courses.value.length ? courses.value.slice(0, 4) : fallbackCourses;
  return source.map((course, index) => ({
    ...course,
    title: cleanText(course.title, fallbackCourses[index]?.title || '个性化学习课程'),
    subject: cleanText(course.subject, fallbackCourses[index]?.subject || '课程'),
    teacher_name: cleanText(course.teacher_name, fallbackCourses[index]?.teacher_name || '任课教师'),
    progress: [75, 60, 40, 20][index] ?? 35,
    status: index < 3 ? '进行中' : '未开始'
  }));
});

const tasks = computed(() => {
  const assigned = events.value.filter((item) => item.event_type === 'task_assigned').slice(0, 2).map((item) => ({
    title: item.metadata?.task?.task_type || item.title,
    course: item.metadata?.task?.weak_point || item.description,
    time: item.metadata?.task?.due_date || '今天 23:59',
    done: false
  }));
  return [
    ...assigned,
    { title: '完成爬虫案例练习：豆瓣电影信息采集', course: 'Python 爬虫基础与实践', time: '今天 23:59', done: false },
    { title: '数据结构章节测验（第 3 章：栈与队列）', course: '数据结构与算法', time: '明天 18:00', done: false },
    { title: '阅读《RAG 系统原理与应用》第 2.1 节', course: '人工智能导论', time: '明天 23:59', done: false },
    { title: '学习路径：函数与 HTTP 请求', course: 'Python 爬虫基础与实践', time: '周日 20:00', done: true }
  ].slice(0, 4);
});

const latestReport = computed(() => {
  const report = reports.value[0];
  if (!report || !report.title) return null;
  return report;
});
const statCards = computed(() => [
  { label: '学习总进度', value: '68', unit: '%', hint: '较上周', trend: '+8%', icon: '进' },
  { label: '累计学习时长', value: '128 h 36 m', hint: '本周 12 h 24 m', icon: '时', tone: 'purple' as const },
  { label: '完成测验', value: `${summary.value?.metrics?.quiz_submission_count || 24} / 36`, hint: '正确率 82%', icon: '测', tone: 'green' as const },
  { label: '学习积分', value: '2,560', hint: '排名前 18%', icon: '分', tone: 'orange' as const },
  { label: '本周目标', value: '4 / 6', hint: '任务完成', icon: '标', tone: 'red' as const }
]);

const pathNodes = [
  { title: '环境搭建与基础语法', status: 'done' },
  { title: '函数与 HTTP 请求', status: 'done' },
  { title: '数据解析（正则与 BeautifulSoup）', status: 'done' },
  { title: '数据存储与管理', status: 'active' },
  { title: '反爬策略与应对', status: 'locked' },
  { title: '爬虫项目实战', status: 'locked' }
];

const badges = [
  { name: '连续学习', desc: '7 天', tone: 'blue' },
  { name: '勤奋学习者', desc: '累计学习 40 小时', tone: 'orange' },
  { name: '测验达人', desc: '正确率 >80%', tone: 'red' },
  { name: '探索先锋', desc: '完成 8 个知识点', tone: 'purple' },
  { name: '进阶学习者', desc: '连续学习 30 天', tone: 'gray' }
];

function renderChart() {
  if (!reportChartEl.value) return;
  reportChart = reportChart || echarts.init(reportChartEl.value);
  reportChart.setOption({
    color: ['#7c5cff', '#22c55e', '#2f6bff', '#f97316'],
    textStyle: chartTextStyle,
    tooltip: { trigger: 'axis', ...chartTooltip },
    grid: { left: 28, right: 8, top: 18, bottom: 24 },
    xAxis: { type: 'category', boundaryGap: false, axisLabel: chartTextStyle, data: ['周一', '周二', '周三', '周四', '周五'] },
    yAxis: { type: 'value', axisLabel: chartTextStyle, splitLine: { lineStyle: { color: '#edf2f8' } } },
    series: [
      { type: 'line', smooth: true, data: [6, 8, 7, 10, 12], areaStyle: { opacity: 0.08 } },
      { type: 'line', smooth: true, data: [3, 6, 8, 12, 18], areaStyle: { opacity: 0.08 } },
      { type: 'line', smooth: true, data: [72, 74, 78, 80, 82], areaStyle: { opacity: 0.05 } },
      { type: 'line', smooth: true, data: [86, 92, 104, 118, 126], areaStyle: { opacity: 0.05 } }
    ]
  });
}

async function loadPage() {
  loading.value = true;
  error.value = '';
  try {
    const [summaryResult, reportsResult, coursesResult, eventsResult] = await Promise.allSettled([
      api.get<DashboardSummary>('/api/dashboard/summary'),
      api.get<ReportItem[]>('/api/v1/reports'),
      api.get<Course[]>('/api/v1/courses'),
      api.get<Array<{ id: number; event_type: string; title: string; description: string; metadata?: Record<string, any> }>>('/api/v1/events?limit=20')
    ]);
    if (summaryResult.status === 'fulfilled') summary.value = summaryResult.value;
    if (reportsResult.status === 'fulfilled') reports.value = reportsResult.value;
    if (coursesResult.status === 'fulfilled') courses.value = coursesResult.value;
    if (eventsResult.status === 'fulfilled') events.value = eventsResult.value;
    if ([summaryResult, reportsResult, coursesResult].every((item) => item.status === 'rejected')) {
      error.value = '后端暂不可用，当前显示演示数据。';
    }
  } finally {
    loading.value = false;
    await nextTick();
    renderChart();
  }
}

function resizeChart() {
  reportChart?.resize();
}

onMounted(() => {
  loadPage();
  window.addEventListener('resize', resizeChart);
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeChart);
  reportChart?.dispose();
});
</script>

<template>
  <section class="page student-dashboard">
    <PageHeader title="你好，张三！" description="今天是充满收获的一天，继续保持专注。">
      <template #actions>
        <RouterLink class="btn secondary" to="/learning-path">查看路径</RouterLink>
        <RouterLink class="btn" to="/tutor-chat">继续学习</RouterLink>
      </template>
    </PageHeader>

    <p v-if="loading" class="panel muted">正在加载学生端学习总览...</p>

    <div class="student-shell">
      <main class="student-main">
        <div class="stat-grid">
          <StatCard v-for="item in statCards" :key="item.label" v-bind="item" />
        </div>

        <div class="two-column">
          <DataCard title="我的课程" subtitle="课程进度与继续学习入口">
            <template #action>
              <RouterLink class="text-link" to="/courses">查看全部</RouterLink>
            </template>
            <div class="course-list">
              <div v-for="course in courseCards" :key="course.id" class="student-course">
                <span class="course-thumb">{{ String(course.subject || course.title).slice(0, 1) }}</span>
                <div>
                  <strong>{{ course.title }}</strong>
                  <p>{{ course.teacher_name || '任课教师' }}</p>
                  <ProgressBar :value="course.progress" />
                </div>
                <span>{{ course.progress }}%</span>
                <StatusBadge :label="course.status" :tone="course.status === '进行中' ? 'purple' : 'neutral'" />
              </div>
            </div>
          </DataCard>

          <DataCard title="今日任务" subtitle="待完成事项与截止时间">
            <template #action>
              <RouterLink class="text-link" to="/teaching-calendar">查看全部</RouterLink>
            </template>
            <div class="task-list">
              <div v-for="task in tasks" :key="`${task.title}-${task.time}`" class="task-item">
                <span class="task-dot" :class="{ done: task.done }"></span>
                <div>
                  <strong>{{ task.title }}</strong>
                  <p>{{ task.course }}</p>
                </div>
                <span :class="['task-time', { urgent: task.time.includes('今天') }]">{{ task.time }}</span>
              </div>
            </div>
          </DataCard>
        </div>

        <div class="two-column">
          <DataCard title="学习路径" subtitle="Python 爬虫工程师成长路径">
            <template #action>
              <RouterLink class="text-link" to="/learning-path">查看全部</RouterLink>
            </template>
            <div class="path-card">
              <div class="path-meta">
                <strong>进度：6 / 9</strong>
                <span>当前节点：数据存储与管理</span>
              </div>
              <div class="path-list">
                <div v-for="node in pathNodes" :key="node.title" :class="['path-node', node.status]">
                  <span></span>
                  <p>{{ node.title }}</p>
                </div>
              </div>
              <RouterLink class="btn path-button" to="/learning-path">继续学习</RouterLink>
            </div>
          </DataCard>

          <DataCard title="成就徽章" subtitle="近期获得与成长记录">
            <template #action>
              <RouterLink class="text-link" to="/study-groups">查看全部</RouterLink>
            </template>
            <div class="badge-row">
              <div v-for="badge in badges" :key="badge.name" :class="['achievement-badge', badge.tone]">
                <span>{{ badge.name.slice(0, 1) }}</span>
                <strong>{{ badge.name }}</strong>
                <p>{{ badge.desc }}</p>
              </div>
            </div>
          </DataCard>
        </div>

        <DataCard title="学习报告（本周）" subtitle="学习时长、任务、正确率与知识点掌握">
          <template #action>
            <RouterLink class="text-link" to="/reports">查看详细报告</RouterLink>
          </template>
          <div class="report-summary">
            <div>
              <span>学习时长</span>
              <strong>12h 24m</strong>
              <p>较上周 +15%</p>
            </div>
            <div>
              <span>完成任务</span>
              <strong>18</strong>
              <p>较上周 +20%</p>
            </div>
            <div>
              <span>正确率</span>
              <strong>82%</strong>
              <p>较上周 +6%</p>
            </div>
            <div>
              <span>知识点掌握</span>
              <strong>126</strong>
              <p>较上周 +12%</p>
            </div>
          </div>
          <div ref="reportChartEl" class="small-chart"></div>
          <div v-if="latestReport" class="latest-report">
            <strong>{{ latestReport.title }}</strong>
            <span>质量评分 {{ latestReport.quality_score ?? '-' }}</span>
          </div>
          <EmptyState v-else title="暂无正式学习报告" description="当前看板使用演示周报，生成报告后会自动展示。" />
        </DataCard>
      </main>

      <aside class="ai-panel">
        <div class="ai-panel-header">
          <div>
            <h2>智能答疑</h2>
            <p class="muted">在线 · 基于课程资料回答</p>
          </div>
          <StatusBadge label="在线" tone="success" />
        </div>
        <div class="chat-window">
          <div class="message user">什么是函数式编程？它和面向对象编程有什么区别？</div>
          <div class="message assistant">
            函数式编程强调函数的组合、不可变性和无副作用；面向对象编程强调对象、状态和封装。学习 Python 时，可以把函数式思维用于数据处理，把面向对象用于复杂业务建模。
          </div>
        </div>
        <div class="reference-card">
          <strong>参考资料（3）</strong>
          <p>计算机科学导论 · 第 7 章 函数式编程范式</p>
          <p>Python 高级编程 · 第 18 章 函数式编程工具</p>
          <p>函数式编程实战 · 第 2 章 核心概念</p>
        </div>
        <div class="question-chips">
          <button class="secondary">纯函数是什么？</button>
          <button class="secondary">给我一个示例</button>
          <button class="secondary">如何使用高阶函数？</button>
        </div>
        <div class="ask-box">
          <input placeholder="继续提问或输入 / 选择技能..." />
          <button>发</button>
        </div>
      </aside>
    </div>
  </section>
</template>

<style scoped>
.student-shell {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 16px;
  align-items: start;
}

.student-main {
  display: grid;
  gap: 16px;
  min-width: 0;
}

.course-list,
.task-list,
.path-list {
  display: grid;
  gap: 12px;
}

.student-course {
  display: grid;
  grid-template-columns: 52px minmax(0, 1fr) 48px auto;
  gap: 12px;
  align-items: center;
}

.student-course p {
  margin: 3px 0 8px;
  font-size: 13px;
}

.course-thumb {
  display: inline-grid;
  place-items: center;
  width: 52px;
  height: 44px;
  border-radius: 12px;
  color: #fff;
  font-weight: 600;
  background: #2f6bff;
}

.task-item {
  display: grid;
  grid-template-columns: 12px minmax(0, 1fr) auto;
  gap: 12px;
  align-items: center;
  border-bottom: 1px solid #eef2f8;
  padding-bottom: 10px;
}

.task-item:last-child {
  border-bottom: 0;
  padding-bottom: 0;
}

.task-dot {
  width: 10px;
  height: 10px;
  border: 2px solid #cbd5e1;
  border-radius: 50%;
}

.task-dot.done {
  border-color: var(--color-success);
  background: var(--color-success);
}

.task-item p {
  margin: 4px 0 0;
  font-size: 13px;
}

.task-time {
  color: var(--color-text-sub);
  font-size: 13px;
  white-space: nowrap;
}

.task-time.urgent {
  color: var(--color-danger);
}

.path-card {
  display: grid;
  gap: 14px;
}

.path-meta {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  color: var(--color-text-sub);
}

.path-meta strong {
  color: var(--color-text-main);
}

.path-node {
  display: grid;
  grid-template-columns: 18px minmax(0, 1fr);
  gap: 10px;
  align-items: center;
}

.path-node span {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  border: 2px solid #cbd5e1;
}

.path-node.done span {
  border-color: var(--color-success);
  background: var(--color-success);
}

.path-node.active span {
  border-color: var(--color-purple);
  box-shadow: 0 0 0 4px rgba(124, 92, 255, 0.12);
}

.path-node.locked {
  color: var(--color-text-muted);
}

.path-node p {
  margin: 0;
}

.path-button {
  width: 100%;
}

.badge-row {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 10px;
}

.achievement-badge {
  display: grid;
  justify-items: center;
  gap: 6px;
  text-align: center;
}

.achievement-badge span {
  display: inline-grid;
  place-items: center;
  width: 52px;
  height: 52px;
  border-radius: 16px;
  color: #fff;
  font-weight: 600;
  background: #2f6bff;
}

.achievement-badge.orange span {
  background: #f97316;
}

.achievement-badge.red span {
  background: #ef4444;
}

.achievement-badge.purple span {
  background: #7c3aed;
}

.achievement-badge.gray span {
  background: #e2e8f0;
  color: #94a3b8;
}

.achievement-badge strong {
  font-size: 13px;
}

.achievement-badge p {
  margin: 0;
  font-size: 12px;
}

.report-summary {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
  margin-bottom: 8px;
}

.report-summary div {
  border-right: 1px solid var(--color-border);
  padding-right: 12px;
}

.report-summary div:last-child {
  border-right: 0;
}

.report-summary span,
.report-summary p {
  color: var(--color-text-sub);
  font-size: 12px;
}

.report-summary strong {
  display: block;
  margin-top: 4px;
  font-size: 22px;
}

.report-summary p {
  margin: 4px 0 0;
}

.latest-report {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  border-top: 1px solid var(--color-border);
  padding-top: 10px;
}

.ai-panel {
  position: sticky;
  top: 90px;
  display: grid;
  gap: 14px;
  border: 1px solid var(--color-border);
  border-radius: var(--card-radius);
  padding: 16px;
  background: var(--bg-card);
}

.ai-panel-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.ai-panel-header h2 {
  margin: 0;
  font-size: 15px;
  color: var(--color-text-main);
}

.chat-window {
  display: grid;
  gap: 12px;
}

.message {
  border-radius: 16px;
  padding: 12px;
  line-height: 1.65;
  font-size: 13px;
}

.message.user {
  margin-left: 42px;
  color: #fff;
  background: var(--color-primary);
}

.message.assistant {
  margin-right: 18px;
  color: var(--color-text-main);
  background: #f8fbff;
}

.reference-card {
  display: grid;
  gap: 8px;
  border: 1px solid var(--color-border);
  border-radius: 14px;
  padding: 12px;
  background: #fbfdff;
}

.reference-card p {
  margin: 0;
  font-size: 13px;
}

.question-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.ask-box {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 42px;
  gap: 8px;
}

@media (max-width: 1320px) {
  .student-shell {
    grid-template-columns: 1fr;
  }

  .ai-panel {
    position: static;
  }
}

@media (max-width: 760px) {
  .student-course,
  .task-item,
  .path-meta,
  .latest-report {
    display: grid;
  }

  .badge-row,
  .report-summary {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
