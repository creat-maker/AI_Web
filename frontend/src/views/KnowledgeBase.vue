<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { api } from '../api/client';
import type { Course } from '../types';

interface CourseDocument {
  id: number;
  course_id: number;
  filename: string;
  file_type?: string;
  parse_status: string;
  chunk_count?: number;
  created_at?: string;
}

interface SearchResult {
  content: string;
  source_file?: string;
  document_id?: number;
  score?: number;
}

const courses = ref<Course[]>([]);
const courseId = ref<number>();
const selectedFile = ref<File | null>(null);
const docs = ref<CourseDocument[]>([]);
const query = ref('Python 爬虫发送 HTTP 请求的基本步骤是什么？');
const results = ref<SearchResult[]>([]);
const docsLoading = ref(false);
const uploading = ref(false);
const searching = ref(false);
const dragActive = ref(false);
const error = ref('');
const uploadMessage = ref('');
const searchMessage = ref('');

const selectedCourse = computed(() => courses.value.find((item) => item.id === courseId.value));
const parsedCount = computed(() => docs.value.filter((item) => item.parse_status === 'parsed').length);
const chunkCount = computed(() => docs.value.reduce((sum, item) => sum + Number(item.chunk_count || 0), 0));
const latestUploadAt = computed(() => {
  const sortedDates = docs.value
    .map((item) => item.created_at)
    .filter(Boolean)
    .sort()
  const latest = sortedDates[sortedDates.length - 1];
  return latest ? formatDate(latest) : '暂无上传';
});

function courseTitle(course_id: number) {
  return courses.value.find((item) => item.id === course_id)?.title || `课程 #${course_id}`;
}

function formatDate(value?: string) {
  if (!value) return '暂无时间';
  return new Date(value).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
}

function formatSize(size?: number) {
  if (!size && size !== 0) return '-';
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${(size / 1024 / 1024).toFixed(1)} MB`;
}

function statusText(status?: string) {
  const map: Record<string, string> = {
    parsed: '已解析',
    parsing: '解析中',
    pending: '等待解析',
    failed: '解析失败'
  };
  return map[status || ''] || status || '未知';
}

function pickFile(file?: File | null) {
  if (!file) return;
  selectedFile.value = file;
  uploadMessage.value = '';
  error.value = '';
}

function handleFileChange(event: Event) {
  const input = event.target as HTMLInputElement;
  pickFile(input.files?.[0] || null);
}

function handleDrop(event: DragEvent) {
  dragActive.value = false;
  pickFile(event.dataTransfer?.files?.[0] || null);
}

async function loadCourses() {
  courses.value = await api.get<Course[]>('/api/v1/courses');
  courseId.value = courseId.value || courses.value[0]?.id;
  await loadDocs();
}

async function loadDocs() {
  if (!courseId.value) {
    docs.value = [];
    return;
  }
  docsLoading.value = true;
  error.value = '';
  try {
    docs.value = await api.get<CourseDocument[]>(`/api/v1/knowledge-base/documents?course_id=${courseId.value}`);
  } catch (err) {
    error.value = err instanceof Error ? err.message : '文档列表加载失败';
  } finally {
    docsLoading.value = false;
  }
}

async function upload() {
  if (!courseId.value || !selectedFile.value) return;
  uploading.value = true;
  uploadMessage.value = '';
  error.value = '';
  try {
    const form = new FormData();
    form.append('file', selectedFile.value);
    await api.upload(`/api/v1/knowledge-base/upload?course_id=${courseId.value}`, form);
    uploadMessage.value = '上传成功，知识库已完成解析。';
    selectedFile.value = null;
    await loadDocs();
  } catch (err) {
    error.value = err instanceof Error ? err.message : '上传失败，请检查文件类型或后端服务。';
  } finally {
    uploading.value = false;
  }
}

async function search() {
  if (!courseId.value || !query.value.trim()) return;
  searching.value = true;
  searchMessage.value = '';
  error.value = '';
  try {
    const data = await api.get<{ items: SearchResult[] }>(
      `/api/v1/knowledge-base/search?course_id=${courseId.value}&query=${encodeURIComponent(query.value.trim())}&top_k=5`
    );
    results.value = data.items;
    if (!results.value.length) {
      searchMessage.value = '没有找到相关知识片段，请尝试换一个关键词。';
    }
  } catch (err) {
    error.value = err instanceof Error ? err.message : '检索失败，请确认知识库已构建。';
  } finally {
    searching.value = false;
  }
}

onMounted(loadCourses);
</script>

<template>
  <section class="page kb-page">
    <div class="panel kb-hero">
      <div>
        <p class="eyebrow">课程知识库</p>
        <h2>知识库管理</h2>
        <p class="muted">上传课程资料，系统会解析为知识片段，用于 Dashboard 统计和智能答疑引用。</p>
      </div>
      <label class="course-select">
        当前课程
        <select v-model.number="courseId" @change="loadDocs">
          <option v-for="course in courses" :key="course.id" :value="course.id">{{ course.title }}</option>
        </select>
      </label>
    </div>

    <p v-if="error" class="panel error-text">{{ error }}</p>

    <div class="overview-grid">
      <article class="stat overview-card">
        <span>文档总数</span>
        <strong>{{ docs.length }}</strong>
        <small>份</small>
      </article>
      <article class="stat overview-card">
        <span>已解析文档</span>
        <strong>{{ parsedCount }}</strong>
        <small>{{ docs.length ? `${Math.round((parsedCount / docs.length) * 100)}% 完成` : '等待上传' }}</small>
      </article>
      <article class="stat overview-card">
        <span>知识切片</span>
        <strong>{{ chunkCount }}</strong>
        <small>段</small>
      </article>
      <article class="stat overview-card">
        <span>最近上传</span>
        <strong class="date-value">{{ latestUploadAt }}</strong>
        <small>{{ selectedCourse?.title || '未选择课程' }}</small>
      </article>
    </div>

    <div class="kb-layout">
      <section class="panel">
        <div class="panel-title">
          <h2>资料上传与解析</h2>
          <span class="muted">PDF / Word / PPT / TXT / Markdown</span>
        </div>
        <label
          class="drop-zone"
          :class="{ active: dragActive, ready: selectedFile }"
          @dragover.prevent="dragActive = true"
          @dragleave.prevent="dragActive = false"
          @drop.prevent="handleDrop"
        >
          <input type="file" @change="handleFileChange" />
          <strong>{{ selectedFile ? selectedFile.name : '拖拽文件到这里，或点击选择文件' }}</strong>
          <span v-if="selectedFile">{{ formatSize(selectedFile.size) }} · {{ selectedFile.type || '未知类型' }}</span>
          <span v-else>选择课程资料后，点击上传即可写入知识库。</span>
        </label>
        <div class="upload-actions">
          <button :disabled="uploading || !selectedFile || !courseId" @click="upload">
            {{ uploading ? '上传解析中...' : '上传并构建知识库' }}
          </button>
          <span v-if="uploadMessage" class="success-text">{{ uploadMessage }}</span>
        </div>
      </section>

      <section class="panel">
        <div class="panel-title">
          <h2>检索测试</h2>
          <span class="muted">验证知识库可用性</span>
        </div>
        <div class="search-box">
          <textarea v-model="query" />
          <button :disabled="searching || !courseId" @click="search">
            {{ searching ? '检索中...' : '检索知识片段' }}
          </button>
        </div>
        <p v-if="searchMessage" class="muted">{{ searchMessage }}</p>
      </section>
    </div>

    <section class="panel">
      <div class="panel-title">
        <h2>文档列表</h2>
        <span class="muted">{{ docsLoading ? '加载中...' : `${docs.length} 份资料` }}</span>
      </div>
      <div class="doc-grid">
        <article v-for="doc in docs" :key="doc.id" class="doc-card">
          <div class="doc-card-head">
            <strong>{{ doc.filename }}</strong>
            <span :class="['status-pill', doc.parse_status]">{{ statusText(doc.parse_status) }}</span>
          </div>
          <p>{{ courseTitle(doc.course_id) }}</p>
          <div class="doc-meta">
            <span>{{ doc.file_type || 'file' }}</span>
            <span>{{ doc.chunk_count ?? 0 }} 个切片</span>
            <span>{{ formatDate(doc.created_at) }}</span>
          </div>
        </article>
        <p v-if="!docsLoading && !docs.length" class="empty-state">暂无文档，请先上传课程资料。</p>
      </div>
    </section>

    <section class="panel">
      <div class="panel-title">
        <h2>检索结果</h2>
        <span class="muted">{{ results.length ? `${results.length} 条匹配` : '等待检索' }}</span>
      </div>
      <div class="result-grid">
        <article v-for="item in results" :key="`${item.document_id}-${item.content}`" class="result-card">
          <div class="result-head">
            <strong>{{ item.source_file || '未知来源' }}</strong>
            <span>score {{ item.score ?? '-' }}</span>
          </div>
          <p>{{ item.content }}</p>
        </article>
        <p v-if="!results.length" class="empty-state">输入关键词并点击检索后，这里会展示来源文档和知识片段。</p>
      </div>
    </section>
  </section>
</template>

<style scoped>
.kb-page {
  gap: 18px;
}

.kb-hero,
.panel-title,
.doc-card-head,
.result-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.kb-hero {
  align-items: center;
}

.kb-hero h2 {
  margin: 0 0 8px;
  font-size: 24px;
}

.eyebrow {
  margin: 0 0 6px;
  color: #2264d1;
  font-size: 13px;
  font-weight: 700;
}

.course-select {
  min-width: 260px;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}

.overview-card {
  min-height: 112px;
}

.overview-card small {
  display: block;
  color: #66758a;
}

.date-value {
  font-size: 18px;
  line-height: 1.3;
}

.kb-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(320px, 0.9fr);
  gap: 16px;
}

.drop-zone {
  display: grid;
  place-items: center;
  gap: 8px;
  min-height: 170px;
  border: 1px dashed #b9c7da;
  border-radius: 8px;
  background: #fbfcff;
  color: #39475a;
  text-align: center;
  cursor: pointer;
  padding: 18px;
}

.drop-zone.active,
.drop-zone.ready {
  border-color: #2264d1;
  background: #f1f6ff;
}

.drop-zone input {
  display: none;
}

.drop-zone span {
  color: #66758a;
}

.upload-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
  margin-top: 12px;
}

.search-box {
  display: grid;
  gap: 12px;
}

.search-box textarea {
  min-height: 116px;
}

.doc-grid,
.result-grid {
  display: grid;
  gap: 12px;
}

.doc-card,
.result-card {
  border: 1px solid #e4e9f1;
  border-radius: 8px;
  padding: 12px;
  background: #fbfcff;
}

.doc-card p,
.result-card p {
  margin: 8px 0 0;
  color: #39475a;
}

.doc-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
  color: #66758a;
  font-size: 13px;
}

.status-pill,
.result-head span {
  white-space: nowrap;
  color: #1453aa;
  background: #edf4ff;
  border-radius: 999px;
  padding: 5px 8px;
  font-size: 12px;
}

.status-pill.parsed {
  color: #1f7a45;
  background: #effaf4;
}

.status-pill.parsing,
.status-pill.pending {
  color: #955600;
  background: #fff7e8;
}

.empty-state {
  margin: 0;
  color: #66758a;
}

.success-text {
  color: #1f7a45;
}

.error-text {
  color: #b42318;
}

button:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

@media (max-width: 980px) {
  .kb-layout,
  .kb-hero,
  .panel-title {
    display: grid;
  }

  .course-select {
    min-width: 0;
  }
}
</style>
