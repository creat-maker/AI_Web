<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue';
import { RouterLink } from 'vue-router';
import { LineChart, RadarChart } from 'echarts/charts';
import { GridComponent, RadarComponent, TooltipComponent } from 'echarts/components';
import * as echarts from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { api } from '../api/client';
import DataCard from '../components/DataCard.vue';
import EmptyState from '../components/EmptyState.vue';
import PageHeader from '../components/PageHeader.vue';
import ProgressBar from '../components/ProgressBar.vue';
import StatCard from '../components/StatCard.vue';
import StatusBadge from '../components/StatusBadge.vue';
import { useRole } from '../composables/useRole';
import type { Course } from '../types';

echarts.use([LineChart, RadarChart, GridComponent, RadarComponent, TooltipComponent, CanvasRenderer]);

interface StudentProfileItem {
  id: number;
  course_id?: number;
  student_name: string;
  current_level?: string;
  learning_goal?: string;
  weak_points?: string[] | string;
  learning_preference?: string;
  profile_json?: unknown;
  created_at?: string;
}

interface StudentView {
  id: number;
  name: string;
  className: string;
  number: string;
  score: number;
  course_id?: number;
  level: string;
  goal: string;
  weakPoints: string[];
  preference: string;
  abilities: Array<{ name: string; value: number }>;
  trend: number[];
  raw?: StudentProfileItem;
}

const { currentRole } = useRole();
const courses = ref<Course[]>([]);
const profiles = ref<StudentProfileItem[]>([]);
const loading = ref(true);
const error = ref('');
const operationMessage = ref('');
const selectedId = ref<number | null>(null);
const keyword = ref('');
const radarEl = ref<HTMLDivElement | null>(null);
const trendEl = ref<HTMLDivElement | null>(null);
let radarChart: echarts.ECharts | null = null;
let trendChart: echarts.ECharts | null = null;

const taskForm = reactive({
  student_profile_id: 0,
  course_id: 0,
  weak_point: 'HTTP 请求',
  task_type: '完成练习',
  due_date: ''
});

const fallbackStudents: StudentView[] = [
  {
    id: 1,
    name: '张三',
    className: '计科大三 1 班',
    number: '2021123456',
    score: 86,
    course_id: 1,
    level: '优秀',
    goal: '两周内掌握 Python 爬虫基础',
    weakPoints: ['HTTP 请求', '异常处理', '数据存储'],
    preference: '案例驱动',
    abilities: [
      { name: '编程能力', value: 82 },
      { name: '算法思维', value: 88 },
      { name: '数据处理', value: 75 },
      { name: '工程实践', value: 70 },
      { name: '问题解决', value: 90 },
      { name: '学习态度', value: 85 }
    ],
    trend: [58, 62, 68, 71, 76, 82, 86]
  },
  {
    id: 2,
    name: '李四',
    className: '计科大三 1 班',
    number: '2021123457',
    score: 79,
    course_id: 1,
    level: '良好',
    goal: '强化数据结构应用',
    weakPoints: ['栈与队列', '递归', '复杂度分析'],
    preference: '任务驱动',
    abilities: [
      { name: '编程能力', value: 76 },
      { name: '算法思维', value: 72 },
      { name: '数据处理', value: 80 },
      { name: '工程实践', value: 74 },
      { name: '问题解决', value: 78 },
      { name: '学习态度', value: 84 }
    ],
    trend: [52, 58, 63, 65, 71, 76, 79]
  },
  {
    id: 3,
    name: '王五',
    className: '计科大二 1 班',
    number: '2021123458',
    score: 66,
    course_id: 2,
    level: '需关注',
    goal: '补齐基础语法与函数',
    weakPoints: ['函数', '文件操作', '循环嵌套'],
    preference: '视频讲解',
    abilities: [
      { name: '编程能力', value: 61 },
      { name: '算法思维', value: 58 },
      { name: '数据处理', value: 64 },
      { name: '工程实践', value: 55 },
      { name: '问题解决', value: 60 },
      { name: '学习态度', value: 72 }
    ],
    trend: [42, 45, 48, 52, 57, 61, 66]
  }
];

function cleanText(value: string | undefined, fallback: string) {
  if (!value || /[?]{2,}|�/.test(value)) return fallback;
  return value;
}

function normalizeWeakPoints(profile: StudentProfileItem, fallback: string[]) {
  const value = profile.weak_points;
  if (Array.isArray(value) && value.length) return value.map(String);
  if (typeof value === 'string' && value.trim()) return value.split(',').map((item) => item.trim()).filter(Boolean);
  const raw = profile.profile_json as Record<string, unknown> | undefined;
  const fromJson = raw?.weak_points;
  if (Array.isArray(fromJson) && fromJson.length) return fromJson.map(String);
  return fallback;
}

const students = computed<StudentView[]>(() => {
  if (!profiles.value.length) return fallbackStudents;
  return profiles.value.map((profile, index) => {
    const fallback = fallbackStudents[index % fallbackStudents.length];
    return {
      ...fallback,
      id: profile.id,
      name: cleanText(profile.student_name, fallback.name),
      course_id: profile.course_id || fallback.course_id,
      level: cleanText(profile.current_level, fallback.level),
      goal: cleanText(profile.learning_goal, fallback.goal),
      preference: cleanText(profile.learning_preference, fallback.preference),
      weakPoints: normalizeWeakPoints(profile, fallback.weakPoints),
      raw: profile
    };
  });
});

const filteredStudents = computed(() => {
  const word = keyword.value.trim().toLowerCase();
  return students.value.filter((student) => !word || `${student.name}${student.className}${student.number}`.toLowerCase().includes(word));
});

const selectedStudent = computed(() => students.value.find((item) => item.id === selectedId.value) || filteredStudents.value[0] || students.value[0]);

const statCards = computed(() => {
  const total = students.value.length;
  const average = total ? Math.round(students.value.reduce((sum, item) => sum + item.score, 0) / total) : 0;
  const risk = students.value.filter((item) => item.score < 70).length;
  return [
    { label: '画像数量', value: total, unit: '份', hint: '已生成画像', icon: '像' },
    { label: '平均评分', value: average, unit: '分', hint: '综合表现', icon: '评', tone: 'green' as const },
    { label: '需关注学生', value: risk, unit: '人', hint: '低于 70 分', icon: '关', tone: 'orange' as const },
    { label: '薄弱点标签', value: new Set(students.value.flatMap((item) => item.weakPoints)).size, unit: '类', hint: '聚合画像标签', icon: '弱', tone: 'purple' as const }
  ];
});

const suggestions = computed(() => {
  const student = selectedStudent.value;
  return [
    { title: '补强任务', content: `围绕 ${student.weakPoints[0] || '薄弱知识点'} 布置 15 分钟分层练习。` },
    { title: '课堂干预', content: '下一节课加入案例复盘，并抽查关键步骤理解情况。' },
    { title: '答疑建议', content: `建议在智能答疑中开启追问模式，匹配 ${student.preference} 学习偏好。` }
  ];
});

function cssVar(name: string, fallback: string) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim() || fallback;
}

function renderCharts() {
  const student = selectedStudent.value;
  if (!student) return;
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
  if (trendEl.value) {
    trendChart = trendChart || echarts.init(trendEl.value);
    trendChart.setOption({
      color: [cssVar('--color-primary', '#2f6bff'), cssVar('--status-success-solid', '#22c55e')],
      tooltip: { trigger: 'axis' },
      grid: { left: 34, right: 16, top: 28, bottom: 28 },
      xAxis: { type: 'category', boundaryGap: false, data: ['04-20', '04-27', '05-04', '05-11', '05-18', '05-25', '05-31'] },
      yAxis: { type: 'value', min: 0, max: 100, splitLine: { lineStyle: { color: cssVar('--border-soft', '#edf2f8') } } },
      series: [{ name: '综合评分', type: 'line', smooth: true, areaStyle: { opacity: 0.08 }, data: student.trend }]
    });
  }
}

async function load() {
  loading.value = true;
  error.value = '';
  try {
    const [courseData, profileData] = await Promise.all([
      api.get<Course[]>('/api/v1/courses').catch(() => []),
      api.get<StudentProfileItem[]>('/api/v1/profiles')
    ]);
    courses.value = courseData;
    profiles.value = profileData;
  } catch (err) {
    error.value = err instanceof Error ? err.message : '画像接口暂不可用，当前显示演示数据。';
    profiles.value = [];
  } finally {
    loading.value = false;
    selectedId.value = selectedStudent.value?.id || null;
    taskForm.student_profile_id = selectedStudent.value?.id || 0;
    taskForm.course_id = selectedStudent.value?.course_id || courses.value[0]?.id || 0;
    await nextTick();
    renderCharts();
  }
}

async function assignTask() {
  const student = selectedStudent.value;
  if (!student) return;
  operationMessage.value = '';
  taskForm.student_profile_id = student.id;
  taskForm.course_id = student.course_id || taskForm.course_id;
  taskForm.weak_point = student.weakPoints[0] || taskForm.weak_point;
  try {
    await api.post('/api/v1/events/assign-task', taskForm);
    operationMessage.value = '补强任务已布置，学生端学习路径会显示该任务。';
  } catch (err) {
    operationMessage.value = err instanceof Error ? err.message : '布置补强任务失败，当前保留演示操作。';
  }
}

function selectStudent(id: number) {
  selectedId.value = id;
  nextTick(renderCharts);
}

function resizeCharts() {
  radarChart?.resize();
  trendChart?.resize();
}

watch(selectedStudent, () => nextTick(renderCharts));

onMounted(() => {
  load();
  window.addEventListener('resize', resizeCharts);
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeCharts);
  radarChart?.dispose();
  trendChart?.dispose();
});
</script>

<template>
  <section class="page profile-page">
    <PageHeader title="学生画像分析" description="查看学生综合画像、能力结构、薄弱点和干预建议。">
      <template #actions>
        <RouterLink class="btn secondary" to="/student/profile-dialog">对话式画像构建</RouterLink>
        <RouterLink class="btn secondary" to="/reports">报告中心</RouterLink>
        <button type="button" @click="assignTask">生成个性化学习报告</button>
      </template>
    </PageHeader>

    <p v-if="loading" class="panel muted">正在加载画像数据...</p>
    <p v-if="operationMessage" class="panel muted">{{ operationMessage }}</p>

    <div class="stat-grid">
      <StatCard v-for="item in statCards" :key="item.label" v-bind="item" />
    </div>

    <div class="profile-layout">
      <DataCard title="学生列表" subtitle="按姓名、班级、学号搜索">
        <input v-model="keyword" placeholder="搜索学生..." />
        <div class="student-list">
          <button
            v-for="student in filteredStudents"
            :key="student.id"
            type="button"
            :class="['student-list-item', { active: selectedStudent?.id === student.id }]"
            @click="selectStudent(student.id)"
          >
            <span class="student-avatar small">{{ student.name.slice(0, 1) }}</span>
            <span>
              <strong>{{ student.name }}</strong>
              <small>{{ student.className }} · {{ student.score }} 分</small>
            </span>
            <StatusBadge :label="student.level" :tone="student.score >= 80 ? 'success' : student.score >= 70 ? 'info' : 'warning'" />
          </button>
        </div>
        <EmptyState v-if="!filteredStudents.length" title="暂无学生" description="调整关键词或生成画像后会显示。" />
      </DataCard>

      <main v-if="selectedStudent" class="profile-main">
        <DataCard title="学生详情" subtitle="综合评分、基础信息和学习目标">
          <template #action>
            <button class="secondary" @click="assignTask">生成个性化学习报告</button>
          </template>
          <div class="student-detail-head">
            <span class="student-avatar">{{ selectedStudent.name.slice(0, 1) }}</span>
            <div>
              <h2>{{ selectedStudent.name }}</h2>
              <p>{{ selectedStudent.className }} | 学号：{{ selectedStudent.number }}</p>
              <p>学习目标：{{ selectedStudent.goal }}</p>
            </div>
            <div class="score-card">
              <span>综合评分</span>
              <strong>{{ selectedStudent.score }}</strong><small>/100</small>
            </div>
          </div>
        </DataCard>

        <div class="two-column">
          <DataCard title="能力雷达图" subtitle="六维能力结构">
            <div ref="radarEl" class="chart-box"></div>
          </DataCard>

          <DataCard title="能力条" subtitle="关键学习能力评分">
            <div class="ability-list">
              <div v-for="item in selectedStudent.abilities" :key="item.name" class="ability-row">
                <span>{{ item.name }}</span>
                <ProgressBar :value="item.value" />
                <strong>{{ item.value }}/100</strong>
              </div>
            </div>
          </DataCard>
        </div>

        <div class="two-column">
          <DataCard title="学习进度趋势" subtitle="近 7 个观察节点综合评分">
            <div ref="trendEl" class="chart-box"></div>
          </DataCard>

          <DataCard title="薄弱知识点" subtitle="基于画像和测评聚合">
            <div class="weak-list">
              <div v-for="(point, index) in selectedStudent.weakPoints" :key="point" class="weak-item">
                <span>{{ index + 1 }}</span>
                <strong>{{ point }}</strong>
                <ProgressBar :value="82 - index * 12" :tone="index === 0 ? 'warning' : 'primary'" />
              </div>
            </div>
          </DataCard>
        </div>

        <DataCard title="干预建议" subtitle="教师下一步行动">
          <div class="suggestion-grid">
            <article v-for="item in suggestions" :key="item.title" class="item">
              <strong>{{ item.title }}</strong>
              <p>{{ item.content }}</p>
            </article>
          </div>
        </DataCard>
      </main>
    </div>
  </section>
</template>

<style scoped>
.profile-layout {
  display: grid;
  grid-template-columns: 320px minmax(0, 1fr);
  gap: 16px;
  align-items: start;
}

.profile-main,
.student-list,
.ability-list,
.weak-list,
.suggestion-grid {
  display: grid;
  gap: 12px;
}

.student-list {
  margin-top: 12px;
}

.student-list-item {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  gap: 10px;
  align-items: center;
  width: 100%;
  border: 1px solid var(--color-border);
  border-radius: 14px;
  padding: 10px;
  color: var(--color-text-main);
  text-align: left;
  background: var(--bg-surface);
  box-shadow: none;
}

.student-list-item.active {
  border-color: rgba(47, 107, 255, 0.55);
  background: var(--color-primary-light);
}

.student-list-item small {
  display: block;
  margin-top: 4px;
  color: var(--color-text-sub);
}

.student-avatar {
  display: inline-grid;
  place-items: center;
  width: 62px;
  height: 62px;
  border-radius: 50%;
  color: var(--text-light);
  font-size: 24px;
  font-weight: 800;
  background: linear-gradient(135deg, var(--status-info-text), var(--color-primary));
}

.student-avatar.small {
  width: 42px;
  height: 42px;
  font-size: 16px;
}

.student-detail-head {
  display: flex;
  align-items: center;
  gap: 14px;
}

.student-detail-head h2 {
  margin: 0 0 6px;
}

.student-detail-head p {
  margin: 4px 0 0;
}

.score-card {
  margin-left: auto;
  text-align: right;
}

.score-card span,
.score-card small {
  color: var(--color-text-sub);
}

.score-card strong {
  color: var(--color-success);
  font-size: 34px;
}

.ability-row {
  display: grid;
  grid-template-columns: 78px minmax(0, 1fr) 64px;
  gap: 10px;
  align-items: center;
}

.weak-item {
  display: grid;
  grid-template-columns: 28px 120px minmax(0, 1fr);
  gap: 10px;
  align-items: center;
}

.weak-item > span {
  display: inline-grid;
  place-items: center;
  width: 24px;
  height: 24px;
  border-radius: 8px;
  color: var(--text-light);
  background: linear-gradient(135deg, var(--color-primary), var(--color-purple));
}

.suggestion-grid {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

@media (max-width: 1180px) {
  .profile-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .student-detail-head,
  .suggestion-grid,
  .ability-row,
  .weak-item {
    display: grid;
  }

  .score-card {
    margin-left: 0;
    text-align: left;
  }
}
</style>
