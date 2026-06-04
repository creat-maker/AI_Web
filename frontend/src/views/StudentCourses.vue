<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue';
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
import type { Course } from '../types';

echarts.use([LineChart, GridComponent, TooltipComponent, CanvasRenderer]);

const courses = ref<Course[]>([]);
const loading = ref(true);
const error = ref('');
const chartEl = ref<HTMLDivElement | null>(null);
let chart: echarts.ECharts | null = null;

const fallbackCourses = [
  { id: 1, title: 'Python 爬虫基础与实践', subject: 'Python', teacher_name: '王老师', progress: 75, status: '进行中', last: '今天 10:24', hours: '18h 20m' },
  { id: 2, title: '数据结构与算法', subject: '算法', teacher_name: '陈老师', progress: 60, status: '进行中', last: '昨天 19:40', hours: '15h 05m' },
  { id: 3, title: '人工智能导论', subject: 'AI', teacher_name: '张老师', progress: 40, status: '进行中', last: '05-29 16:20', hours: '9h 30m' },
  { id: 4, title: '计算机网络原理', subject: '网络', teacher_name: '李老师', progress: 100, status: '已完成', last: '05-20 21:10', hours: '24h 15m' }
];

function cleanText(value: string | undefined, fallback: string) {
  if (!value || /[?]{2,}|�/.test(value)) return fallback;
  return value;
}

const courseRows = computed(() => {
  const source = courses.value.length ? courses.value.slice(0, 4) : fallbackCourses;
  return source.map((course, index) => {
    const fallback = fallbackCourses[index % fallbackCourses.length];
    return {
      id: course.id,
      title: cleanText(course.title, fallback.title),
      subject: cleanText(course.subject, fallback.subject),
      teacher_name: cleanText(course.teacher_name, fallback.teacher_name),
      progress: fallback.progress,
      status: fallback.status,
      last: fallback.last,
      hours: fallback.hours
    };
  });
});

const statCards = computed(() => [
  { label: '进行中课程', value: courseRows.value.filter((item) => item.status === '进行中').length, unit: '门', hint: '持续学习', icon: '课' },
  { label: '已完成课程', value: courseRows.value.filter((item) => item.status === '已完成').length, unit: '门', hint: '获得结课记录', icon: '完', tone: 'green' as const },
  { label: '累计学习时长', value: '128h', unit: '36m', hint: '本周 +12h', icon: '时', tone: 'purple' as const },
  { label: '平均进度', value: Math.round(courseRows.value.reduce((sum, item) => sum + item.progress, 0) / courseRows.value.length), unit: '%', hint: '较上周 +8%', icon: '进', tone: 'cyan' as const }
]);

const recentRecords = [
  { title: '完成 HTTP 请求章节练习', course: 'Python 爬虫基础与实践', time: '今天 10:24' },
  { title: '阅读栈与队列章节资料', course: '数据结构与算法', time: '昨天 19:40' },
  { title: '观看 RAG 系统导论视频', course: '人工智能导论', time: '05-29 16:20' }
];

function renderChart() {
  if (!chartEl.value) return;
  chart = chart || echarts.init(chartEl.value);
  chart.setOption({
    color: ['#2f6bff', '#22c55e'],
    tooltip: { trigger: 'axis' },
    grid: { left: 34, right: 16, top: 28, bottom: 28 },
    xAxis: { type: 'category', boundaryGap: false, data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'] },
    yAxis: { type: 'value', splitLine: { lineStyle: { color: '#edf2f8' } } },
    series: [{ type: 'line', smooth: true, areaStyle: { opacity: 0.08 }, data: [35, 42, 48, 56, 61, 66, 72] }]
  });
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
    await nextTick();
    renderChart();
  }
}

function resizeChart() {
  chart?.resize();
}

onMounted(() => {
  load();
  window.addEventListener('resize', resizeChart);
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeChart);
  chart?.dispose();
});
</script>

<template>
  <section class="page student-courses-page">
    <PageHeader title="我的课程" description="查看已加入课程、学习进度、最近学习和继续学习入口。">
      <template #actions>
        <button class="secondary">筛选课程</button>
        <button>继续学习</button>
      </template>
    </PageHeader>

    <p v-if="loading" class="panel muted">正在加载我的课程...</p>

    <div class="stat-grid">
      <StatCard v-for="item in statCards" :key="item.label" v-bind="item" />
    </div>

    <div class="student-course-layout">
      <DataCard title="课程列表" subtitle="课程进度、学习时长和状态">
        <div class="course-card-grid">
          <article v-for="course in courseRows" :key="course.id" class="course-card">
            <span class="course-icon">{{ course.subject.slice(0, 1) }}</span>
            <div>
              <strong>{{ course.title }}</strong>
              <p>{{ course.teacher_name }} · 最近学习 {{ course.last }}</p>
              <ProgressBar :value="course.progress" :tone="course.status === '已完成' ? 'success' : 'primary'" />
            </div>
            <div class="course-meta">
              <span>{{ course.progress }}%</span>
              <StatusBadge :label="course.status" :tone="course.status === '已完成' ? 'success' : 'purple'" />
              <button class="secondary">继续学习</button>
            </div>
          </article>
        </div>
        <EmptyState v-if="!courseRows.length" title="暂无课程" description="加入课程后会显示在这里。" />
      </DataCard>

      <DataCard title="学习统计" subtitle="近 7 天课程进度变化">
        <div ref="chartEl" class="chart-box"></div>
      </DataCard>
    </div>

    <DataCard title="最近学习记录" subtitle="按时间展示课程学习动作">
      <div class="record-grid">
        <article v-for="item in recentRecords" :key="`${item.title}-${item.time}`" class="item compact">
          <div>
            <strong>{{ item.title }}</strong>
            <p>{{ item.course }}</p>
          </div>
          <span class="muted">{{ item.time }}</span>
        </article>
      </div>
    </DataCard>
  </section>
</template>

<style scoped>
.student-course-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(360px, 0.8fr);
  gap: 16px;
}

.course-card-grid,
.record-grid {
  display: grid;
  gap: 12px;
}

.course-card {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  gap: 12px;
  align-items: center;
  border: 1px solid var(--color-border);
  border-radius: 16px;
  padding: 14px;
  background: #fbfdff;
}

.course-icon {
  display: inline-grid;
  place-items: center;
  width: 52px;
  height: 52px;
  border-radius: 16px;
  color: #fff;
  font-weight: 800;
  background: linear-gradient(135deg, var(--color-primary), var(--color-purple));
}

.course-card p {
  margin: 6px 0 10px;
  font-size: 13px;
}

.course-meta {
  display: grid;
  justify-items: end;
  gap: 8px;
}

.course-meta > span {
  font-size: 22px;
  font-weight: 800;
}

@media (max-width: 1180px) {
  .student-course-layout,
  .course-card {
    grid-template-columns: 1fr;
  }

  .course-meta {
    justify-items: start;
  }
}
</style>
