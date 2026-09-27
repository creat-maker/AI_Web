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
import ProfileRadarCard from '../components/ProfileRadarCard.vue';
import ProgressBar from '../components/ProgressBar.vue';
import StatCard from '../components/StatCard.vue';
import StatusBadge from '../components/StatusBadge.vue';
import { demoStudents, useRole } from '../composables/useRole';
import type { Course } from '../types';

echarts.use([LineChart, RadarChart, GridComponent, RadarComponent, TooltipComponent, CanvasRenderer]);

interface StudentProfileItem {
  id: number;
  user_id?: string;
  profile_type?: string;
  major?: string;
  course_id?: number;
  student_name: string;
  current_level?: string;
  knowledge_level?: string;
  learning_goal?: string;
  weak_points?: string[] | string;
  learning_preference?: string;
  learning_style?: string;
  mistake_pattern?: string;
  available_time?: string;
  resource_preference?: string;
  risk_level?: string;
  recommended_strategy?: string;
  profile_json?: unknown;
  created_at?: string;
  updated_at?: string;
  change_log?: unknown[];
  evidence_items?: EvidenceItem[];
  dialog_extraction?: DialogExtraction;
  dimension_scores?: Record<string, { score?: number; label?: string } | number>;
}

interface EvidenceItem {
  source_type: string;
  description: string;
  related_field: string;
  confidence: number;
}

interface DialogExtraction {
  mode?: string;
  raw_answer?: string;
  extracted_fields?: Record<string, unknown>;
  confidence?: number;
  evidence_basis?: string;
}

interface ProfileUpdateResult {
  before_profile?: StudentProfileItem;
  after_profile?: StudentProfileItem;
  change_log?: unknown[];
  updated_at?: string;
}

interface StudentView {
  id: number;
  name: string;
  className: string;
  number: string;
  score: number;
  course_id?: number;
  user_id?: string;
  profileType?: string;
  major?: string;
  level: string;
  goal: string;
  weakPoints: string[];
  preference: string;
  mistakePattern?: string;
  availableTime?: string;
  resourcePreference?: string;
  riskLevel?: string;
  recommendedStrategy?: string;
  updatedAt?: string;
  changeLog?: unknown[];
  evidenceItems?: EvidenceItem[];
  dialogExtraction?: DialogExtraction;
  abilities: Array<{ name: string; value: number }>;
  trend: number[];
  raw?: StudentProfileItem;
}

const { currentRole, demoUserId, setDemoUserId } = useRole();
const reportCenterPath = computed(() => (currentRole.value === 'teacher' ? '/teacher/reports' : '/student/reports'));
const pageTitle = computed(() => (currentRole.value === 'teacher' ? '学生画像分析' : '我的学习画像'));
const pageDescription = computed(() => (
  currentRole.value === 'teacher'
    ? '查看演示范围内学生的综合画像、能力结构、薄弱点和干预建议。'
    : '查看当前登录学生本人的学习目标、能力结构和薄弱知识点。'
));
const demoUsers = demoStudents;
const courses = ref<Course[]>([]);
const profiles = ref<StudentProfileItem[]>([]);
const loading = ref(true);
const error = ref('');
const operationMessage = ref('');
const visualizationMessage = ref('');
const dialogInput = ref('我正在学 Python 程序设计，循环结构有点弱，尤其是 while 循环和循环嵌套，我更喜欢代码案例和图解，想尽快完成课程作业。');
const dialogProfile = ref({
  summary: '系统已根据你的学习情况生成个性化建议，你在循环结构上还需要加强。',
  riskLevel: '学习状态：需巩固',
  weakKnowledgePoints: ['while 循环', '循环嵌套', 'break / continue'],
  resourcePreference: '代码实操案例、变量变化图解、分层练习题',
  sourceDescription: '自然语言对话 + 学习历史 + 测验结果 + AI 问答记录',
  dimensions: [
    { name: '知识基础', value: '基础薄弱' },
    { name: '认知风格', value: '代码案例 + 图解' },
    { name: '学习目标', value: '完成课程作业和基础项目' },
    { name: '学习进度', value: '46%' },
    { name: '易错偏好', value: '循环条件更新遗漏、循环嵌套变量混用' },
    { name: '资源偏好', value: '代码实操案例、变量变化图解、分层练习题' },
    { name: '学习能力', value: '能跟随示例完成迁移，需要脚手架提示' },
    { name: '学习状态', value: '需巩固' }
  ]
});
const selectedId = ref<number | null>(null);
const keyword = ref('');
const lastUpdateResult = ref<ProfileUpdateResult | null>(null);
const radarEl = ref<HTMLDivElement | null>(null);
const trendEl = ref<HTMLDivElement | null>(null);
let radarChart: echarts.ECharts | null = null;
let trendChart: echarts.ECharts | null = null;

const taskForm = reactive({
  student_profile_id: 0,
  course_id: 0,
  weak_point: 'while 循环',
  task_type: '完成练习',
  due_date: ''
});

const fallbackStudents: StudentView[] = [
  {
    id: 1,
    name: '李明',
    className: '计科大三 1 班',
    number: '2021123456',
    score: 67,
    course_id: 1,
    level: '需巩固',
    goal: '两周内补齐 Python 循环结构，完成课程作业和基础代码实操',
    weakPoints: ['while 循环', '循环嵌套', 'break / continue'],
    preference: '代码实操案例 + 变量变化图解',
    abilities: [
      { name: '知识基础', value: 48 },
      { name: 'for 循环', value: 70 },
      { name: 'while 循环', value: 48 },
      { name: 'break / continue', value: 55 },
      { name: '循环嵌套', value: 43 },
      { name: '代码实操', value: 62 }
    ],
    trend: [42, 45, 48, 52, 57, 63, 67]
  },
  {
    id: 2,
    name: '陈思',
    className: '计科大三 1 班',
    number: '2021123457',
    score: 79,
    course_id: 1,
    level: '良好',
    goal: '强化循环嵌套变量追踪能力',
    weakPoints: ['循环嵌套', '变量变化表', 'for 循环边界'],
    preference: '任务驱动 + 表格追踪',
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
    name: '赵雨',
    className: '计科大二 1 班',
    number: '2021123458',
    score: 66,
    course_id: 2,
    level: '需关注',
    goal: '区分 break / continue 的循环控制场景',
    weakPoints: ['break / continue', 'while 循环', '输出结果判断'],
    preference: '短讲解 + 输出推演',
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

function rawProfile(profile: StudentProfileItem) {
  return (profile.profile_json as Record<string, unknown> | undefined) || {};
}

function fieldText(profile: StudentProfileItem, key: string, fallback = '') {
  const raw = rawProfile(profile);
  const value = (profile as unknown as Record<string, unknown>)[key] ?? raw[key];
  return typeof value === 'string' && value.trim() ? value : fallback;
}

function arrayField<T>(profile: StudentProfileItem, key: string): T[] {
  const raw = rawProfile(profile);
  const value = (profile as unknown as Record<string, unknown>)[key] ?? raw[key];
  return Array.isArray(value) ? value as T[] : [];
}

function objectField<T>(profile: StudentProfileItem, key: string): T | undefined {
  const raw = rawProfile(profile);
  const value = (profile as unknown as Record<string, unknown>)[key] ?? raw[key];
  return value && typeof value === 'object' && !Array.isArray(value) ? value as T : undefined;
}

function profileAbilities(profile: StudentProfileItem) {
  const dimensions = profile.dimension_scores || {};
  return Object.entries(dimensions).map(([name, value]) => ({
    name,
    value: Math.round(typeof value === 'number' ? value : Number(value?.score || 0))
  }));
}

function simulateWeakPoint() {
  if (demoUserId.value === 'demo-advanced') return '循环嵌套变量变化';
  if (demoUserId.value === 'demo-exam') return 'break / continue 区分';
  return 'while 循环条件更新';
}

function weakPointText(profile?: StudentProfileItem) {
  if (!profile) return '-';
  const points = normalizeWeakPoints(profile, []);
  return points.length ? points.join('、') : '-';
}

function updateReason(result: ProfileUpdateResult | null) {
  const latest = result?.change_log?.[result.change_log.length - 1];
  if (!latest || typeof latest === 'string') return latest || '-';
  const item = latest as Record<string, unknown>;
  const changes = item.changes;
  return Array.isArray(changes) ? changes.join('；') : JSON.stringify(item);
}

const students = computed<StudentView[]>(() => {
  if (!profiles.value.length) return currentRole.value === 'student' ? [] : fallbackStudents;
  return profiles.value.map((profile, index) => {
    const isStudentSelf = currentRole.value === 'student';
    const fallback = isStudentSelf
      ? {
          ...fallbackStudents[0],
          name: profile.student_name,
          className: '',
          number: '',
          major: '',
          score: 0,
          abilities: [],
          trend: []
        }
      : fallbackStudents[index % fallbackStudents.length];
    const abilities = profileAbilities(profile);
    const score = abilities.length
      ? Math.round(abilities.reduce((sum, item) => sum + item.value, 0) / abilities.length)
      : fallback.score;
    return {
      ...fallback,
      id: profile.id,
      user_id: fieldText(profile, 'user_id', ''),
      name: cleanText(profile.student_name, fallback.name),
      score,
      profileType: fieldText(profile, 'profile_type', '个性化学习画像'),
      major: fieldText(profile, 'major', '未填写'),
      course_id: profile.course_id || fallback.course_id,
      level: cleanText(profile.current_level || profile.knowledge_level, fallback.level),
      goal: cleanText(profile.learning_goal, fallback.goal),
      preference: cleanText(profile.learning_style || profile.learning_preference, fallback.preference),
      weakPoints: normalizeWeakPoints(profile, fallback.weakPoints),
      mistakePattern: fieldText(profile, 'mistake_pattern', '暂无错因模式'),
      availableTime: fieldText(profile, 'available_time', '暂无可用时间'),
      resourcePreference: fieldText(profile, 'resource_preference', '暂无资源偏好'),
      riskLevel: fieldText(profile, 'risk_level', fallback.level),
      recommendedStrategy: fieldText(profile, 'recommended_strategy', ''),
      updatedAt: fieldText(profile, 'updated_at', String(profile.updated_at || '')),
      changeLog: (profile.change_log || rawProfile(profile).change_log || []) as unknown[],
      evidenceItems: arrayField<EvidenceItem>(profile, 'evidence_items'),
      dialogExtraction: objectField<DialogExtraction>(profile, 'dialog_extraction'),
      abilities: abilities.length ? abilities : fallback.abilities,
      trend: fallback.trend,
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
  if (!student) return [];
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
    if (currentRole.value === 'student') {
      const [courseData, studentProfile] = await Promise.all([
        api.get<Course[]>('/api/v1/courses').catch(() => []),
        api.get<StudentProfileItem>('/api/v1/profiles/me')
      ]);
      courses.value = courseData;
      profiles.value = studentProfile ? [studentProfile] : [];
    } else {
      const [courseData, profileData] = await Promise.all([
        api.get<Course[]>('/api/v1/courses').catch(() => []),
        api.get<StudentProfileItem[]>('/api/v1/profiles')
      ]);
      courses.value = courseData;
      profiles.value = profileData;
    }
  } catch (err) {
    error.value = currentRole.value === 'student'
      ? '画像接口暂不可用，未显示本地学生身份数据。'
      : `画像接口暂不可用，当前显示明确标注的教师端本地演示数据：${err instanceof Error ? err.message : '未知错误'}`;
    profiles.value = [];
  } finally {
    loading.value = false;
    selectedId.value = selectedStudent.value?.id || null;
    taskForm.student_profile_id = selectedStudent.value?.id || 0;
    taskForm.course_id = selectedStudent.value?.course_id || courses.value[0]?.id || 0;
    await loadProfileVisualization(selectedId.value);
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

async function simulateProfileUpdate() {
  operationMessage.value = '';
  try {
    await api.post('/api/v1/profile-dialog/update-by-learning', {
      user_id: demoUserId.value,
      event_type: 'quiz',
      weak_point: simulateWeakPoint(),
      score: 52
    }).then((result) => {
      lastUpdateResult.value = result as ProfileUpdateResult;
    });
    operationMessage.value = '已模拟一次低分测试，画像更新时间和 change_log 已刷新。';
    await load();
  } catch (err) {
    operationMessage.value = err instanceof Error ? err.message : '模拟更新画像失败。';
  }
}

async function runDialogProfile() {
  operationMessage.value = '';
  try {
    const result = await api.post<typeof dialogProfile.value>('/api/v1/profile-dialog/run', {
      studentId: demoUserId.value,
      studentName: '李明',
      courseId: 'python-programming',
      courseName: 'Python 程序设计',
      answer: dialogInput.value,
      weakPoints: ['while 循环', '循环嵌套', 'break / continue']
    });
    dialogProfile.value = {
      ...dialogProfile.value,
      ...result,
      dimensions: result.dimensions?.length ? result.dimensions : dialogProfile.value.dimensions
    };
    operationMessage.value = '对话式画像已生成。';
  } catch (err) {
    operationMessage.value = `画像接口暂不可用，保留本地学习数据：${err instanceof Error ? err.message : '未知错误'}`;
  }
}

async function refreshDialogProfile() {
  try {
    dialogProfile.value = await api.post<typeof dialogProfile.value>('/api/v1/student-profile/refresh', {
      user_id: demoUserId.value,
      dialog: dialogInput.value
    });
    operationMessage.value = '画像已根据最新对话、学习历史、测验结果和 AI 问答记录刷新。';
  } catch (err) {
    operationMessage.value = `画像刷新接口暂不可用，保留本地学习数据：${err instanceof Error ? err.message : '未知错误'}`;
  }
}

async function loadProfileVisualization(id?: number | null) {
  if (!id) {
    visualizationMessage.value = '';
    return;
  }
  try {
    const data = await api.get<{ radar?: unknown[]; cognitive_state?: unknown }>(`/api/v1/profiles/${id}/visualization`);
    visualizationMessage.value = `画像可视化接口已返回：${data.radar?.length || 0} 个维度。`;
  } catch (err) {
    visualizationMessage.value = err instanceof Error ? err.message : '画像可视化接口暂不可用，保留本地图表。';
  }
}

function selectStudent(id: number) {
  selectedId.value = id;
  loadProfileVisualization(id);
  nextTick(renderCharts);
}

function resizeCharts() {
  radarChart?.resize();
  trendChart?.resize();
}

watch(selectedStudent, () => nextTick(renderCharts));
watch(demoUserId, () => {
  if (currentRole.value === 'teacher') load();
});

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
    <PageHeader :title="pageTitle" :description="pageDescription">
      <template #actions>
        <template v-if="currentRole === 'teacher'">
          <select :value="demoUserId" @change="setDemoUserId(($event.target as HTMLSelectElement).value)">
            <option v-for="user in demoUsers" :key="user.id" :value="user.id">{{ user.label }}</option>
          </select>
          <button type="button" class="secondary" @click="simulateProfileUpdate">模拟测试后更新画像</button>
          <RouterLink class="btn secondary" :to="reportCenterPath">报告中心</RouterLink>
          <button type="button" @click="assignTask">生成个性化学习报告</button>
        </template>
        <template v-else>
          <RouterLink class="btn secondary" to="/student/profile-dialog">对话式画像构建</RouterLink>
          <RouterLink class="btn secondary" :to="reportCenterPath">学习报告</RouterLink>
        </template>
      </template>
    </PageHeader>

    <p v-if="loading" class="panel muted">正在加载画像数据...</p>
    <p v-if="error" class="panel muted">{{ error }}</p>
    <p v-if="operationMessage" class="panel muted">{{ operationMessage }}</p>
    <p v-if="visualizationMessage" class="panel muted">{{ visualizationMessage }}</p>

    <div v-if="currentRole === 'teacher'" class="stat-grid">
      <StatCard v-for="item in statCards" :key="item.label" v-bind="item" />
    </div>

    <DataCard v-if="currentRole === 'teacher'" title="对话式画像构建" subtitle="从自然语言对话抽取 6 维画像，并支持随学更新、风险、薄弱知识点、资源偏好和画像来源展示。">
      <textarea v-model="dialogInput" class="dialog-profile-input" rows="4"></textarea>
      <div class="row-actions dialog-actions">
        <button type="button" @click="runDialogProfile">生成画像</button>
        <button type="button" class="secondary" @click="refreshDialogProfile">画像刷新</button>
      </div>
      <div class="profile-summary">
        <strong>{{ dialogProfile.summary }}</strong>
        <StatusBadge :label="dialogProfile.riskLevel" tone="warning" />
      </div>
      <div class="profile-dimension-list">
        <article v-for="item in dialogProfile.dimensions" :key="item.name">
          <span>{{ item.name }}</span>
          <strong>{{ item.value }}</strong>
        </article>
      </div>
      <div class="dialog-meta-grid">
        <article><span>薄弱知识点</span><strong>{{ dialogProfile.weakKnowledgePoints.join('、') }}</strong></article>
        <article><span>推荐资源偏好</span><strong>{{ dialogProfile.resourcePreference }}</strong></article>
        <article><span>画像来源说明</span><strong>{{ dialogProfile.sourceDescription }}</strong></article>
      </div>
    </DataCard>

    <DataCard v-if="currentRole === 'teacher'" title="学生画像闭环摘要" subtitle="面向教师干预展示基础水平、学习目标、学习偏好、课程进度、薄弱知识点、错题分布和风险等级。">
      <div class="profile-loop-grid">
        <section class="profile-loop-main">
          <article>
            <span>基础水平</span>
            <strong>中等偏弱</strong>
          </article>
          <article>
            <span>学习目标</span>
            <strong>两周内补齐 Python 循环结构</strong>
          </article>
          <article>
            <span>学习偏好</span>
            <strong>代码实操案例、变量变化图解、分层练习题</strong>
          </article>
          <article>
            <span>风险等级</span>
            <StatusBadge label="需关注" tone="warning" />
          </article>
        </section>
        <section class="profile-loop-side">
          <div>
            <span>课程进度 68%</span>
            <ProgressBar :value="68" tone="primary" />
          </div>
          <div class="chip-row">
            <span>while 循环</span>
            <span>循环嵌套</span>
            <span>break / continue</span>
          </div>
          <div class="wrong-grid">
            <article><strong>38%</strong><span>概念混淆</span></article>
            <article><strong>31%</strong><span>边界遗漏</span></article>
            <article><strong>18%</strong><span>代码规范</span></article>
            <article><strong>13%</strong><span>审题偏差</span></article>
          </div>
          <div class="intervention-note">教师干预建议：推送 Python 循环结构个性化补弱资源包，安排 10 分钟 while 循环代码讲解，布置 3 道 while 循环补全题，并课后查看形成性评价报告。</div>
        </section>
      </div>
    </DataCard>

    <EmptyState
      v-if="!loading && currentRole === 'student' && !selectedStudent"
      title="本人画像暂不可用"
      description="系统没有展示任何本地学生身份数据，请稍后重试或联系教师。"
    />

    <div :class="['profile-layout', { 'student-self-layout': currentRole === 'student' }]">
      <DataCard
        v-if="currentRole === 'teacher'"
        data-testid="teacher-student-list"
        title="学生列表"
        subtitle="按姓名、班级、学号搜索"
      >
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
        <DataCard :title="currentRole === 'teacher' ? '学生详情' : '本人画像'" subtitle="学习目标、能力状态和薄弱知识点">
          <template v-if="currentRole === 'teacher'" #action>
            <button class="secondary" @click="assignTask">生成个性化学习报告</button>
          </template>
          <div class="student-detail-head">
            <span class="student-avatar">{{ selectedStudent.name.slice(0, 1) }}</span>
            <div>
              <h2>{{ selectedStudent.name }}</h2>
              <p v-if="currentRole === 'teacher'">{{ selectedStudent.className }} | 学号：{{ selectedStudent.number }}</p>
              <p>学习目标：{{ selectedStudent.goal }}</p>
            </div>
            <div v-if="currentRole === 'teacher'" class="score-card">
              <span>综合评分</span>
              <strong>{{ selectedStudent.score }}</strong><small>/100</small>
            </div>
          </div>
          <div class="profile-dimension-list">
            <article><span>画像类型</span><strong>{{ selectedStudent.profileType }}</strong></article>
            <article v-if="currentRole === 'teacher'"><span>专业</span><strong>{{ selectedStudent.major }}</strong></article>
            <article><span>知识基础</span><strong>{{ selectedStudent.level }}</strong></article>
            <article><span>学习风格</span><strong>{{ selectedStudent.preference }}</strong></article>
            <article><span>易错模式</span><strong>{{ selectedStudent.mistakePattern }}</strong></article>
            <article><span>可用时间</span><strong>{{ selectedStudent.availableTime }}</strong></article>
            <article><span>资源偏好</span><strong>{{ selectedStudent.resourcePreference }}</strong></article>
            <article><span>更新时间</span><strong>{{ selectedStudent.updatedAt || '-' }}</strong></article>
          </div>
          <div v-if="currentRole === 'teacher'" class="change-log-box">
            <strong>change_log</strong>
            <p v-if="!selectedStudent.changeLog?.length">暂无变化记录</p>
            <p v-for="(item, index) in selectedStudent.changeLog" :key="index">{{ typeof item === 'string' ? item : JSON.stringify(item) }}</p>
          </div>
          <div v-if="currentRole === 'teacher' && lastUpdateResult" class="update-compare-box">
            <strong>动态更新前后对比</strong>
            <article>
              <span>更新前薄弱点</span>
              <p>{{ weakPointText(lastUpdateResult.before_profile) }}</p>
            </article>
            <article>
              <span>更新后薄弱点</span>
              <p>{{ weakPointText(lastUpdateResult.after_profile) }}</p>
            </article>
            <article>
              <span>更新时间</span>
              <p>{{ lastUpdateResult.after_profile?.updated_at || lastUpdateResult.updated_at || '-' }}</p>
            </article>
            <article>
              <span>更新原因</span>
              <p>{{ updateReason(lastUpdateResult) }}</p>
            </article>
          </div>
          <div class="evidence-box">
            <strong>画像依据</strong>
            <p v-if="!selectedStudent.evidenceItems?.length">暂无画像依据</p>
            <article v-for="item in selectedStudent.evidenceItems" :key="`${item.source_type}-${item.related_field}-${item.description}`">
              <span>{{ item.source_type }} · {{ item.related_field }} · 置信度 {{ Math.round(item.confidence * 100) }}%</span>
              <p>{{ item.description }}</p>
            </article>
          </div>
          <div v-if="currentRole === 'teacher' && selectedStudent.dialogExtraction" class="extraction-box">
            <strong>最近一次对话抽取过程</strong>
            <article>
              <span>{{ selectedStudent.dialogExtraction.mode || '规则抽取' }}</span>
              <p>学生原始回答：{{ selectedStudent.dialogExtraction.raw_answer }}</p>
              <p>抽取字段：{{ JSON.stringify(selectedStudent.dialogExtraction.extracted_fields) }}</p>
              <p>抽取置信度：{{ Math.round((selectedStudent.dialogExtraction.confidence || 0) * 100) }}%</p>
              <p>抽取依据：{{ selectedStudent.dialogExtraction.evidence_basis }}</p>
            </article>
          </div>
        </DataCard>

        <div class="two-column">
          <DataCard title="能力雷达图" subtitle="六维能力结构">
            <div ref="radarEl" class="chart-box"></div>
          </DataCard>

          <DataCard title="能力条" subtitle="关键学习能力评分">
            <ProfileRadarCard :dimensions="selectedStudent.abilities.map((item) => ({ name: item.name, value: item.value, label: item.value >= 80 ? '优势' : item.value >= 60 ? '稳定' : '需补强' }))" />
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

        <DataCard v-if="currentRole === 'teacher'" title="干预建议" subtitle="教师下一步行动">
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

.profile-layout.student-self-layout {
  grid-template-columns: minmax(0, 1fr);
}

.profile-main,
.student-list,
.ability-list,
.weak-list,
.suggestion-grid,
.profile-dimension-list,
.dialog-meta-grid {
  display: grid;
  gap: 12px;
}

.profile-dimension-list {
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  margin-top: 14px;
}

.dialog-meta-grid {
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  margin-top: 12px;
}

.profile-dimension-list article,
.dialog-meta-grid article,
.change-log-box,
.update-compare-box,
.evidence-box,
.extraction-box {
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 12px;
  background: #fff;
}

.profile-dimension-list span,
.dialog-meta-grid span,
.change-log-box p,
.update-compare-box span,
.evidence-box span,
.extraction-box span {
  color: var(--color-text-sub);
  font-size: 13px;
}

.profile-dimension-list strong,
.dialog-meta-grid strong {
  display: block;
  margin-top: 6px;
}

.dialog-profile-input {
  width: 100%;
  box-sizing: border-box;
  resize: vertical;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 12px;
  line-height: 1.7;
}

.dialog-actions {
  margin-top: 12px;
}

.change-log-box,
.update-compare-box,
.evidence-box,
.extraction-box {
  display: grid;
  gap: 8px;
  margin-top: 12px;
}

.update-compare-box article,
.evidence-box article,
.extraction-box article {
  border-top: 1px solid var(--color-border);
  padding-top: 8px;
}

.update-compare-box p,
.evidence-box p,
.extraction-box p {
  margin: 4px 0 0;
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

.profile-loop-grid {
  display: grid;
  grid-template-columns: minmax(0, 0.85fr) minmax(0, 1.15fr);
  gap: 14px;
}

.profile-loop-main,
.profile-loop-side {
  display: grid;
  gap: 12px;
}

.profile-loop-main article,
.wrong-grid article,
.intervention-note {
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 12px;
  background: #fff;
}

.profile-loop-main span,
.profile-loop-side span,
.wrong-grid span {
  color: var(--color-text-sub);
  font-size: 13px;
}

.profile-loop-main strong,
.wrong-grid strong {
  display: block;
  margin-top: 6px;
}

.chip-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chip-row span {
  border-radius: 999px;
  padding: 6px 10px;
  color: var(--color-primary-dark);
  background: var(--color-primary-light);
  font-weight: 700;
}

.wrong-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.wrong-grid strong {
  color: var(--color-primary-dark);
  font-size: 22px;
}

.intervention-note {
  border-color: #bfdbfe;
  background: var(--color-primary-light);
}

@media (max-width: 1180px) {
  .profile-layout,
  .profile-loop-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .student-detail-head,
  .suggestion-grid,
  .ability-row,
  .weak-item,
  .wrong-grid {
    display: grid;
    grid-template-columns: 1fr;
  }

  .score-card {
    margin-left: 0;
    text-align: left;
  }
}
</style>
