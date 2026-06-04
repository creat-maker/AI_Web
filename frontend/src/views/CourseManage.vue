<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { RouterLink } from 'vue-router';
import { api } from '../api/client';
import DataCard from '../components/DataCard.vue';
import EmptyState from '../components/EmptyState.vue';
import PageHeader from '../components/PageHeader.vue';
import ProgressBar from '../components/ProgressBar.vue';
import StatCard from '../components/StatCard.vue';
import StatusBadge from '../components/StatusBadge.vue';
import { useRole } from '../composables/useRole';
import type { Course } from '../types';

type CourseStatus = '进行中' | '即将开始' | '已结束' | '草稿';

interface CourseRow {
  id: number;
  title: string;
  subject: string;
  teacher_name: string;
  description?: string;
  className: string;
  students: number;
  progress: number;
  completion: number;
  status: CourseStatus;
  updatedAt: string;
  type: string;
}

const { currentRole } = useRole();
const courses = ref<Course[]>([]);
const loading = ref(true);
const error = ref('');
const operationMessage = ref('');
const keyword = ref('');
const typeFilter = ref('全部类型');
const statusFilter = ref('全部状态');
const classFilter = ref('全部班级');
const form = reactive({
  title: 'Python 爬虫基础与实践',
  subject: '计算机',
  teacher_name: '王老师',
  description: '面向计科大三的项目实践课程'
});

const fallbackRows: CourseRow[] = [
  { id: 1, title: 'Python 爬虫基础与实践', subject: '计算机', teacher_name: '王老师', className: '计科大三 1 班', students: 32, progress: 72, completion: 68, status: '进行中', updatedAt: '今天 10:20', type: '技术课程' },
  { id: 2, title: '人工智能导论', subject: '人工智能', teacher_name: '张老师', className: '计科大三 2 班', students: 48, progress: 65, completion: 61, status: '进行中', updatedAt: '昨天 18:40', type: '基础课程' },
  { id: 3, title: '数据结构与算法', subject: '计算机', teacher_name: '陈老师', className: '计科大二 1 班', students: 38, progress: 58, completion: 55, status: '进行中', updatedAt: '05-29 21:15', type: '基础课程' },
  { id: 4, title: 'Web 开发技术', subject: '软件工程', teacher_name: '李老师', className: '计科大二 2 班', students: 30, progress: 41, completion: 36, status: '即将开始', updatedAt: '05-28 09:30', type: '技术课程' },
  { id: 5, title: '机器学习与数据挖掘', subject: '人工智能', teacher_name: '刘老师', className: '计科大三 3 班', students: 44, progress: 100, completion: 94, status: '已结束', updatedAt: '05-20 16:00', type: '进阶课程' },
  { id: 6, title: '计算机网络原理', subject: '计算机', teacher_name: '赵老师', className: '计科大二 3 班', students: 35, progress: 12, completion: 0, status: '草稿', updatedAt: '05-18 12:10', type: '基础课程' }
];

function cleanText(value: string | undefined, fallback: string) {
  if (!value || /[?]{2,}|�/.test(value)) return fallback;
  return value;
}

const courseRows = computed<CourseRow[]>(() => {
  if (!courses.value.length) return fallbackRows;
  return courses.value.map((course, index) => {
    const fallback = fallbackRows[index % fallbackRows.length];
    return {
      id: course.id,
      title: cleanText(course.title, fallback.title),
      subject: cleanText(course.subject, fallback.subject),
      teacher_name: cleanText(course.teacher_name, fallback.teacher_name),
      description: cleanText(course.description, fallback.description || ''),
      className: fallback.className,
      students: fallback.students,
      progress: fallback.progress,
      completion: fallback.completion,
      status: fallback.status,
      updatedAt: fallback.updatedAt,
      type: fallback.type
    };
  });
});

const filteredRows = computed(() => {
  const word = keyword.value.trim().toLowerCase();
  return courseRows.value.filter((course) => {
    const matchWord = !word || `${course.title}${course.className}${course.teacher_name}`.toLowerCase().includes(word);
    const matchType = typeFilter.value === '全部类型' || course.type === typeFilter.value;
    const matchStatus = statusFilter.value === '全部状态' || course.status === statusFilter.value;
    const matchClass = classFilter.value === '全部班级' || course.className === classFilter.value;
    return matchWord && matchType && matchStatus && matchClass;
  });
});

const typeOptions = computed(() => ['全部类型', ...Array.from(new Set(courseRows.value.map((item) => item.type)))]);
const classOptions = computed(() => ['全部班级', ...Array.from(new Set(courseRows.value.map((item) => item.className)))]);

const statCards = computed(() => {
  const rows = courseRows.value;
  const active = rows.filter((item) => item.status === '进行中').length;
  const students = rows.reduce((sum, item) => sum + item.students, 0);
  const average = rows.length ? Math.round(rows.reduce((sum, item) => sum + item.completion, 0) / rows.length) : 0;
  return [
    { label: '课程总数', value: rows.length, unit: '门', hint: '当前教师课程池', icon: '课' },
    { label: '进行中课程', value: active, unit: '门', hint: '正常推进', icon: '行', tone: 'green' as const },
    { label: '学生总数', value: students, unit: '人', hint: '覆盖班级人数', icon: '学', tone: 'purple' as const },
    { label: '平均完成率', value: average, unit: '%', hint: '按课程完成率估算', icon: '率', tone: 'cyan' as const },
    { label: '待批改作业', value: 18, unit: '份', hint: '需本周处理', icon: '批', tone: 'orange' as const }
  ];
});

function badgeTone(status: CourseStatus) {
  if (status === '进行中') return 'success';
  if (status === '即将开始') return 'info';
  if (status === '已结束') return 'neutral';
  return 'warning';
}

async function load() {
  loading.value = true;
  error.value = '';
  try {
    courses.value = await api.get<Course[]>('/api/v1/courses');
  } catch (err) {
    error.value = err instanceof Error ? err.message : '课程接口暂不可用，当前显示演示数据。';
    courses.value = [];
  } finally {
    loading.value = false;
  }
}

async function createCourse() {
  operationMessage.value = '';
  try {
    await api.post<Course>('/api/v1/courses', form);
    operationMessage.value = '课程已保存。';
    await load();
  } catch (err) {
    operationMessage.value = err instanceof Error ? err.message : '保存课程失败，演示数据保持可用。';
  }
}

function demoAction(label: string) {
  operationMessage.value = `${label} 为演示操作，后续可接章节、任务和班级管理流程。`;
}

onMounted(load);
</script>

<template>
  <section class="page course-page">
    <PageHeader title="课程管理" description="统一管理课程、班级、学习进度和任务完成情况。">
      <template #actions>
        <RouterLink class="btn secondary" to="/teacher">返回概览</RouterLink>
        <button type="button" @click="createCourse">新建课程</button>
      </template>
    </PageHeader>

    <p v-if="loading" class="panel muted">正在加载课程数据...</p>
    <p v-if="operationMessage" class="panel muted">{{ operationMessage }}</p>

    <div class="stat-grid">
      <StatCard v-for="item in statCards" :key="item.label" v-bind="item" />
    </div>

    <DataCard title="筛选课程" subtitle="按课程名称、状态、类型和班级快速定位">
      <div class="filter-grid">
        <input v-model="keyword" placeholder="搜索课程名称、教师、班级..." />
        <select v-model="typeFilter">
          <option v-for="item in typeOptions" :key="item">{{ item }}</option>
        </select>
        <select v-model="statusFilter">
          <option>全部状态</option>
          <option>进行中</option>
          <option>即将开始</option>
          <option>已结束</option>
          <option>草稿</option>
        </select>
        <select v-model="classFilter">
          <option v-for="item in classOptions" :key="item">{{ item }}</option>
        </select>
      </div>
    </DataCard>

    <DataCard v-if="currentRole !== 'student'" title="新建课程" subtitle="保留现有课程创建接口，提交后刷新课程列表">
      <div class="form-grid">
        <label>课程名称<input v-model="form.title" /></label>
        <label>学科<input v-model="form.subject" /></label>
        <label>教师<input v-model="form.teacher_name" /></label>
        <label>简介<input v-model="form.description" /></label>
        <button @click="createCourse">保存课程</button>
      </div>
    </DataCard>

    <DataCard title="课程列表" :subtitle="`${filteredRows.length} 门课程`">
      <template #action>
        <StatusBadge v-if="error" label="演示数据" tone="warning" />
      </template>
      <div class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>课程名称</th>
              <th>班级</th>
              <th>学生数</th>
              <th>学习进度</th>
              <th>完成率</th>
              <th>状态</th>
              <th>最近更新</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="course in filteredRows" :key="course.id">
              <td>
                <strong>{{ course.title }}</strong>
                <span class="table-sub">{{ course.subject }} · {{ course.teacher_name }}</span>
              </td>
              <td>{{ course.className }}</td>
              <td>{{ course.students }}</td>
              <td>
                <div class="table-progress">
                  <span>{{ course.progress }}%</span>
                  <ProgressBar :value="course.progress" :tone="course.progress > 70 ? 'success' : course.progress < 45 ? 'warning' : 'primary'" />
                </div>
              </td>
              <td>{{ course.completion }}%</td>
              <td><StatusBadge :label="course.status" :tone="badgeTone(course.status)" /></td>
              <td>{{ course.updatedAt }}</td>
              <td>
                <div class="row-actions">
                  <button class="ghost" @click="demoAction('课程详情')">详情</button>
                  <button class="secondary" @click="demoAction('布置任务')">任务</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <EmptyState v-if="!filteredRows.length" title="暂无课程" description="调整筛选条件或新建课程后会显示。" />
    </DataCard>
  </section>
</template>

<style scoped>
.filter-grid {
  display: grid;
  grid-template-columns: minmax(260px, 1fr) 160px 160px 160px;
  gap: 12px;
}

.table-wrap {
  overflow-x: auto;
}

.table-sub {
  display: block;
  margin-top: 4px;
  color: var(--color-text-sub);
  font-size: 12px;
}

.table-progress {
  display: grid;
  grid-template-columns: 42px minmax(120px, 1fr);
  gap: 8px;
  align-items: center;
  min-width: 170px;
}

.row-actions {
  display: flex;
  gap: 8px;
}

@media (max-width: 980px) {
  .filter-grid {
    grid-template-columns: 1fr;
  }
}
</style>
