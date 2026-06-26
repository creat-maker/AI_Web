<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
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
  status?: string;
  file_path?: string;
  fallback_resources?: string[];
  tts_status?: { status?: string; message?: string };
  tts_result?: { status?: string; message?: string; audio_path?: string | null };
  difficulty?: string;
  recommend_reason?: string;
  recommendation_reason?: string;
  relatedKnowledgePoints?: string[];
  reviewStatus?: string;
  libraryStatus?: string;
  pushStatus?: string;
  created_at?: string;
}

const courses = ref<Course[]>([]);
const resources = ref<ResourceItem[]>([]);
const loading = ref(false);
const error = ref('');
const keyword = ref('');
const courseFilter = ref('全部课程');
const typeFilter = ref('全部类型');
const statusFilter = ref('全部状态');

const courseNameMap = computed(() => new Map(courses.value.map((course) => [String(course.id), course.title])));

const normalizedResources = computed(() =>
  resources.value.map((item) => {
    const type = item.resource_type || item.resourceType || '学习资源';
    const courseName = courseNameMap.value.get(String(item.course_id)) || 'Python 程序设计';
    const status = item.pushStatus || item.libraryStatus || item.reviewStatus || '可学习';
    const knowledge = item.relatedKnowledgePoints || inferKnowledge(item);
    return { ...item, type, courseName, status, knowledge };
  })
);

const typeOptions = computed(() => ['全部类型', ...Array.from(new Set(normalizedResources.value.map((item) => item.type)))]);
const courseOptions = computed(() => ['全部课程', ...Array.from(new Set(normalizedResources.value.map((item) => item.courseName)))]);

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
      item.recommendation_reason,
      item.knowledge.join(' ')
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

function inferKnowledge(item: ResourceItem) {
  const text = `${item.title} ${item.content || ''}`;
  const result = ['Python'];
  if (text.includes('循环') || text.toLowerCase().includes('while') || text.toLowerCase().includes('for')) result.push('循环结构');
  if (text.includes('break') || text.includes('continue')) result.push('break / continue');
  return result;
}

function isAnimation(item: ResourceItem) {
  return (item.resource_type || item.resourceType) === 'animation_html';
}

function isTts(item: ResourceItem) {
  return (item.resource_type || item.resourceType) === 'tts_audio';
}

function isVideoMp4(item: ResourceItem) {
  return (item.resource_type || item.resourceType) === 'video_mp4';
}

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
  } catch (err) {
    error.value = err instanceof Error ? err.message : '学习资源加载失败。';
  } finally {
    loading.value = false;
  }
}

function clearSearch() {
  keyword.value = '';
  courseFilter.value = '全部课程';
  typeFilter.value = '全部类型';
  statusFilter.value = '全部状态';
}

onMounted(loadData);
</script>

<template>
  <section class="page student-resources-page">
    <PageHeader title="学习资源" description="查看课程讲义、案例、测验、任务和思维导图资源。">
      <template #actions>
        <button class="secondary" type="button" @click="clearSearch">清空搜索</button>
        <button type="button" @click="loadData">刷新资源</button>
      </template>
    </PageHeader>

    <p v-if="error" class="panel error-text">{{ error }}</p>
    <p v-if="loading" class="panel muted">正在加载资源...</p>

    <DataCard title="搜索资源" subtitle="按课程、章节、资源类型、标题、知识点和状态过滤">
      <div class="filter-grid">
        <input v-model="keyword" placeholder="搜索资源，例如：循环、while、break" @keyup.enter.prevent />
        <select v-model="courseFilter">
          <option v-for="item in courseOptions" :key="item">{{ item }}</option>
        </select>
        <select v-model="typeFilter">
          <option v-for="item in typeOptions" :key="item">{{ item }}</option>
        </select>
        <select v-model="statusFilter">
          <option>全部状态</option>
          <option>可学习</option>
          <option>可推送</option>
          <option>已入库</option>
          <option>待推送</option>
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
          <p class="content">{{ item.content || item.recommend_reason || '该资源已进入学习资源库。' }}</p>
          <div v-if="isAnimation(item) && item.content" class="animation-preview">
            <iframe :srcdoc="item.content" sandbox="" title="动画资源预览"></iframe>
          </div>
          <p v-if="isTts(item)" class="tts-status">
            {{ item.tts_result?.message || item.tts_status?.message || '语音讲解文本已生成，科大讯飞 TTS 可按环境配置接入。' }}
          </p>
          <p v-if="isVideoMp4(item)" class="tts-status">
            {{ item.status === 'generated' ? `MP4 已生成：${item.file_path || '视频文件'}` : item.description || '配置 FFmpeg 后可合成 MP4，HTML 动画为当前稳定预览能力。' }}
          </p>
          <div class="tag-row">
            <span v-for="tag in item.knowledge" :key="tag">{{ tag }}</span>
          </div>
        </article>
      </div>
      <EmptyState
        v-else
        title="未找到相关资源"
        description="请更换关键词，或前往资源生成中心为该课程创建新的学习资源。"
      />
    </DataCard>
  </section>
</template>

<style scoped>
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

.content {
  min-height: 52px;
}

.tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
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

.tag-row span {
  border-radius: 999px;
  padding: 5px 9px;
  color: var(--color-primary-dark);
  background: var(--color-primary-light);
  font-size: 12px;
  font-weight: 800;
}

.error-text {
  color: #b91c1c;
}

@media (max-width: 980px) {
  .filter-grid,
  .resource-grid {
    grid-template-columns: 1fr;
  }
}
</style>
