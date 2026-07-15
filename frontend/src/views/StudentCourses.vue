<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { api } from '../api/client';
import DataCard from '../components/DataCard.vue';
import EmptyState from '../components/EmptyState.vue';
import PageHeader from '../components/PageHeader.vue';
import ProgressBar from '../components/ProgressBar.vue';
import StatusBadge from '../components/StatusBadge.vue';

interface StudentCourse {
  id: number;
  course_name: string;
  subject: string;
  teacher_name: string;
  current_chapter: string;
  progress: number;
  status: string;
  chapter_focus: string;
  accuracy: number;
  study_minutes: number;
  resource_count: number;
  report_count: number;
  recent_records: Array<{ title: string; time: string; type: string }>;
}

interface StudentCourseResponse {
  summary: {
    active_course_count: number;
    today_focus: string;
    average_accuracy: number;
    study_minutes: number;
  };
  courses: StudentCourse[];
}

const loading = ref(false);
const error = ref('');
const keyword = ref('');
const data = ref<StudentCourseResponse>({
  summary: { active_course_count: 0, today_focus: '循环结构', average_accuracy: 0, study_minutes: 0 },
  courses: []
});

const filteredCourses = computed(() => {
  const word = keyword.value.trim().toLowerCase();
  if (!word) return data.value.courses;
  return data.value.courses.filter((course) =>
    [
      course.course_name,
      course.subject,
      course.teacher_name,
      course.current_chapter,
      course.status,
      course.chapter_focus,
      course.recent_records.map((item) => `${item.title} ${item.type}`).join(' ')
    ]
      .join(' ')
      .toLowerCase()
      .includes(word)
  );
});

const stats = computed(() => [
  { label: '进行中课程', value: data.value.summary.active_course_count, unit: '门' },
  { label: '今日重点', value: data.value.summary.today_focus, unit: '' },
  { label: '平均正确率', value: data.value.summary.average_accuracy, unit: '%' },
  { label: '学习时长', value: Math.round(data.value.summary.study_minutes / 60), unit: '小时' }
]);

const recentRecords = computed(() => filteredCourses.value.flatMap((course) => course.recent_records.map((record) => ({ ...record, course: course.course_name }))));

async function loadCourses() {
  loading.value = true;
  error.value = '';
  try {
    data.value = await api.get<StudentCourseResponse>('/api/v1/student/courses?student_id=1');
  } catch (err) {
    error.value = err instanceof Error ? err.message : '学生课程加载失败。';
  } finally {
    loading.value = false;
  }
}

function clearSearch() {
  keyword.value = '';
}

onMounted(loadCourses);
</script>

<template>
  <section class="page student-courses-page">
    <PageHeader title="我的课程" description="查看已加入课程、当前章节、学习进度和最近学习记录。">
      <template #actions>
        <button class="secondary" type="button" @click="clearSearch">清空搜索</button>
        <button type="button" @click="loadCourses">刷新课程</button>
      </template>
    </PageHeader>

    <p v-if="error" class="panel error-text">{{ error }}</p>
    <p v-if="loading" class="panel muted">正在加载课程...</p>

    <div class="stat-grid">
      <article v-for="item in stats" :key="item.label" class="stat-card">
        <span>{{ item.label }}</span>
        <strong>{{ item.value }}</strong>
        <small>{{ item.unit }}</small>
      </article>
    </div>

    <DataCard title="搜索课程" subtitle="按课程、章节、教师、状态和学习记录过滤">
      <input v-model="keyword" placeholder="搜索课程、章节或知识点，例如：循环" @keyup.enter.prevent />
    </DataCard>

    <div class="student-course-layout">
      <DataCard title="课程列表" :subtitle="`${filteredCourses.length} 门课程`">
        <div v-if="filteredCourses.length" class="course-card-grid">
          <article v-for="course in filteredCourses" :key="course.id" class="course-card">
            <span class="course-icon">{{ course.course_name.slice(0, 1) }}</span>
            <div>
              <strong>{{ course.course_name }}</strong>
              <p>{{ course.teacher_name }} / {{ course.subject }} / 当前章节：{{ course.current_chapter }}</p>
              <p class="focus">{{ course.chapter_focus }}</p>
              <ProgressBar :value="course.progress" :tone="course.progress > 70 ? 'success' : 'primary'" />
            </div>
            <div class="course-meta">
              <span>{{ course.progress }}%</span>
              <StatusBadge :label="course.status" :tone="course.status.includes('重点') ? 'warning' : 'success'" />
              <small>{{ course.resource_count }} 个资源 / {{ course.report_count }} 份报告</small>
            </div>
          </article>
        </div>
        <EmptyState v-else title="未找到相关课程" description="请更换关键词，或清空搜索后查看全部课程。" />
      </DataCard>

      <DataCard title="章节重点" subtitle="当前学习关注点">
        <div class="chapter-list">
          <article v-for="course in filteredCourses" :key="course.id" class="chapter-row">
            <div>
              <strong>{{ course.current_chapter }}</strong>
              <StatusBadge :label="`${course.accuracy}% 正确率`" :tone="course.accuracy < 70 ? 'warning' : 'success'" />
            </div>
            <ProgressBar :value="course.accuracy" :tone="course.accuracy < 70 ? 'warning' : 'primary'" />
          </article>
        </div>
        <EmptyState v-if="!filteredCourses.length" title="暂无章节结果" description="搜索命中课程后会显示章节进度。" />
      </DataCard>
    </div>

    <DataCard title="最近学习记录" subtitle="根据课程数据和生成资源汇总">
      <div v-if="recentRecords.length" class="record-grid">
        <article v-for="item in recentRecords" :key="`${item.course}-${item.title}-${item.time}`" class="record-row">
          <div>
            <strong>{{ item.title }}</strong>
            <p>{{ item.course }} / {{ item.type }}</p>
          </div>
          <span class="muted">{{ item.time }}</span>
        </article>
      </div>
      <EmptyState v-else title="未找到相关学习记录" description="请清空搜索或更换关键词。" />
    </DataCard>
  </section>
</template>

<style scoped>
.stat-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.stat-card,
.course-card,
.record-row {
  border: 1px solid var(--border-light);
  border-radius: 14px;
  padding: 14px;
  background: #fff;
}

.stat-card strong {
  display: block;
  margin-top: 8px;
  color: var(--text-main);
  font-size: 26px;
}

.student-course-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(340px, 0.8fr);
  gap: 16px;
}

.course-card-grid,
.chapter-list,
.record-grid {
  display: grid;
  gap: 12px;
}

.course-card,
.record-row {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  gap: 12px;
  align-items: center;
}

.course-icon {
  display: grid;
  place-items: center;
  width: 52px;
  height: 52px;
  border-radius: 14px;
  color: #fff;
  background: var(--color-primary);
  font-weight: 900;
}

.course-card p,
.record-row p {
  margin: 5px 0;
  color: var(--text-secondary);
  font-size: 13px;
}

.focus {
  color: var(--color-primary-dark);
  font-weight: 800;
}

.course-meta {
  display: grid;
  justify-items: end;
  gap: 8px;
}

.course-meta > span {
  font-size: 22px;
  font-weight: 900;
}

.chapter-row {
  display: grid;
  gap: 8px;
}

.chapter-row > div {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: center;
}

.error-text {
  color: #b91c1c;
}

@media (max-width: 1080px) {
  .stat-grid,
  .student-course-layout,
  .course-card,
  .record-row {
    grid-template-columns: 1fr;
  }

  .course-meta {
    justify-items: start;
  }
}
</style>
