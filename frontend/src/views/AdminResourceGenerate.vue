<script setup lang="ts">
import { computed, onMounted, reactive, ref } from 'vue';
import { api } from '../api/client';
import DataCard from '../components/DataCard.vue';
import EmptyState from '../components/EmptyState.vue';
import PageHeader from '../components/PageHeader.vue';
import StatusBadge from '../components/StatusBadge.vue';
import type { Course } from '../types';

interface ResourceItem {
  id: number | string;
  course_id: number | string;
  resource_type?: string;
  resourceType?: string;
  title: string;
  content?: string;
  description?: string;
  format?: string;
  tts_status?: { status?: string; message?: string };
  tts_result?: { status?: string; message?: string; audio_path?: string | null };
  difficulty?: string;
  recommend_reason?: string;
  recommendation_reason?: string;
  reviewStatus?: string;
  libraryStatus?: string;
  pushStatus?: string;
  created_at?: string;
}

const courses = ref<Course[]>([]);
const resources = ref<ResourceItem[]>([]);
const loading = ref(false);
const generating = ref(false);
const error = ref('');
const success = ref('');
const keyword = ref('');
const courseFilter = ref('全部课程');
const typeFilter = ref('全部类型');
const statusFilter = ref('全部状态');

const form = reactive({
  courseId: '',
  studentId: '1',
  courseName: 'Python 程序设计',
  studentLevel: '基础薄弱 + 代码实践偏好',
  learningGoal: '掌握 Python 循环结构',
  knowledgePointsText: 'for 循环, while 循环, break / continue',
  weakPointsText: 'while 条件更新, 循环嵌套变量变化'
});

const courseNameMap = computed(() => new Map(courses.value.map((course) => [String(course.id), course.title])));

const normalizedResources = computed(() =>
  resources.value.map((item) => {
    const type = item.resource_type || item.resourceType || '学习资源';
    const courseName = courseNameMap.value.get(String(item.course_id)) || form.courseName || 'Python 程序设计';
    const status = item.pushStatus || item.libraryStatus || item.reviewStatus || '已入库';
    return { ...item, type, courseName, status };
  })
);

const filteredResources = computed(() => {
  const word = keyword.value.trim().toLowerCase();
  return normalizedResources.value.filter((item) => {
    const haystack = [
      item.title,
      item.content,
      item.type,
      item.courseName,
      item.status,
      item.difficulty,
      item.recommend_reason,
      item.recommendation_reason
    ]
      .join(' ')
      .toLowerCase();
    const matchWord = !word || haystack.includes(word);
    const matchCourse = courseFilter.value === '全部课程' || item.courseName === courseFilter.value;
    const matchType = typeFilter.value === '全部类型' || item.type === typeFilter.value;
    const matchStatus = statusFilter.value === '全部状态' || item.status === statusFilter.value;
    return matchWord && matchCourse && matchType && matchStatus;
  });
});

const courseOptions = computed(() => ['全部课程', ...Array.from(new Set(normalizedResources.value.map((item) => item.courseName)))]);
const typeOptions = computed(() => ['全部类型', ...Array.from(new Set(normalizedResources.value.map((item) => item.type)))]);

async function loadData() {
  loading.value = true;
  error.value = '';
  try {
    const [courseRows, resourceRows] = await Promise.all([
      api.get<Course[]>('/api/v1/courses'),
      api.get<ResourceItem[]>('/api/v1/resources')
    ]);
    courses.value = courseRows;
    resources.value = resourceRows;
    if (!form.courseId && courseRows.length) {
      form.courseId = String(courseRows[0].id);
      form.courseName = courseRows[0].title;
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : '资源数据加载失败。';
  } finally {
    loading.value = false;
  }
}

function syncCourseName() {
  const course = courses.value.find((item) => String(item.id) === String(form.courseId));
  if (course) form.courseName = course.title;
}

async function generatePack() {
  success.value = '';
  error.value = '';
  if (!form.courseId) {
    error.value = '请先选择课程。';
    return;
  }
  generating.value = true;
  try {
    syncCourseName();
    await api.post('/api/v1/resources/generate-pack', {
      studentId: form.studentId,
      courseId: form.courseId,
      courseName: form.courseName,
      studentLevel: form.studentLevel,
      learningGoal: form.learningGoal,
      knowledgePoints: form.knowledgePointsText.split(/[、,，]/).map((item) => item.trim()).filter(Boolean),
      weakPoints: form.weakPointsText.split(/[、,，]/).map((item) => item.trim()).filter(Boolean)
    });
    success.value = '资源已生成并写入资源库。';
    await loadData();
  } catch (err) {
    error.value = err instanceof Error ? err.message : '资源生成失败。';
  } finally {
    generating.value = false;
  }
}

function clearSearch() {
  keyword.value = '';
  courseFilter.value = '全部课程';
  typeFilter.value = '全部类型';
  statusFilter.value = '全部状态';
}

function isAnimation(item: ResourceItem) {
  return (item.resource_type || item.resourceType) === 'animation_html';
}

function isTts(item: ResourceItem) {
  return (item.resource_type || item.resourceType) === 'tts_audio';
}

onMounted(loadData);
</script>

<template>
  <section class="page admin-resource-page">
    <PageHeader title="资源生成中心" description="选择课程和学生画像，生成讲义、案例、练习、任务和脚本资源。">
      <template #actions>
        <button class="secondary" type="button" @click="clearSearch">清空搜索</button>
        <button type="button" @click="loadData">刷新资源</button>
      </template>
    </PageHeader>

    <p v-if="error" class="panel error-text">{{ error }}</p>
    <p v-if="success" class="panel success-text">{{ success }}</p>
    <p v-if="loading" class="panel muted">正在加载课程与资源...</p>

    <DataCard title="生成资源包" subtitle="生成后写入资源库，并同步给学生资源页读取">
      <div class="generate-form">
        <label>课程
          <select v-model="form.courseId" @change="syncCourseName">
            <option v-for="course in courses" :key="course.id" :value="String(course.id)">{{ course.title }}</option>
          </select>
        </label>
        <label>学生画像<input v-model="form.studentLevel" /></label>
        <label>学习目标<input v-model="form.learningGoal" /></label>
        <label>知识点<input v-model="form.knowledgePointsText" /></label>
        <label class="wide">薄弱点<input v-model="form.weakPointsText" /></label>
        <button :disabled="generating" type="button" @click="generatePack">{{ generating ? '正在生成...' : '生成资源包' }}</button>
      </div>
    </DataCard>

    <DataCard title="搜索资源" subtitle="按课程、章节、资源类型、状态和关键词过滤">
      <div class="filter-grid">
        <input v-model="keyword" placeholder="搜索资源，例如：循环、while、测验" @keyup.enter.prevent />
        <select v-model="courseFilter">
          <option v-for="item in courseOptions" :key="item">{{ item }}</option>
        </select>
        <select v-model="typeFilter">
          <option v-for="item in typeOptions" :key="item">{{ item }}</option>
        </select>
        <select v-model="statusFilter">
          <option>全部状态</option>
          <option>已入库</option>
          <option>可推送</option>
          <option>待推送</option>
          <option>通过</option>
        </select>
      </div>
    </DataCard>

    <DataCard title="资源列表" :subtitle="`${filteredResources.length} 个资源`">
      <div v-if="filteredResources.length" class="resource-grid">
        <article v-for="item in filteredResources" :key="item.id" class="resource-card">
          <div class="resource-head">
            <div>
              <strong>{{ item.title }}</strong>
              <p>{{ item.courseName }} / {{ item.type }} / {{ item.difficulty || '基础' }}</p>
            </div>
            <StatusBadge :label="item.status" tone="success" />
          </div>
          <p>{{ item.content || item.recommend_reason || item.recommendation_reason || '该资源已写入资源库。' }}</p>
          <div v-if="isAnimation(item) && item.content" class="animation-preview">
            <iframe :srcdoc="item.content" sandbox="" title="动画资源预览"></iframe>
          </div>
          <p v-if="isTts(item)" class="tts-status">
            {{ item.tts_result?.message || item.tts_status?.message || '语音讲解文本已生成，科大讯飞 TTS 可按环境配置接入。' }}
          </p>
        </article>
      </div>
      <EmptyState v-else title="未找到相关资源" description="请更换关键词、清空搜索，或生成新的课程资源包。" />
    </DataCard>
  </section>
</template>

<style scoped>
.generate-form {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.generate-form label {
  display: grid;
  gap: 7px;
  color: var(--text-secondary);
  font-weight: 800;
}

.generate-form .wide {
  grid-column: 1 / -1;
}

.filter-grid {
  display: grid;
  grid-template-columns: minmax(260px, 1fr) 170px 160px 150px;
  gap: 12px;
}

.resource-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.resource-card {
  border: 1px solid var(--border-light);
  border-radius: 14px;
  padding: 16px;
  background: #fff;
}

.resource-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.resource-card p {
  margin: 7px 0 0;
  color: var(--text-secondary);
  line-height: 1.65;
}

.animation-preview {
  margin-top: 12px;
  border: 1px solid var(--border-light);
  border-radius: 8px;
  overflow: hidden;
}

.animation-preview iframe {
  display: block;
  width: 100%;
  min-height: 230px;
  border: 0;
}

.tts-status {
  border-radius: 8px;
  padding: 10px;
  background: var(--color-primary-light);
}

.error-text {
  color: #b91c1c;
}

.success-text {
  color: #047857;
}

@media (max-width: 980px) {
  .generate-form,
  .filter-grid,
  .resource-grid {
    grid-template-columns: 1fr;
  }
}
</style>
