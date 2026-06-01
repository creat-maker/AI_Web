<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { api } from '../api/client';
import { useRole } from '../composables/useRole';
import type { Course } from '../types';

interface CourseDocument {
  id: number;
  course_id: number;
  filename: string;
  file_type?: string;
  parse_status: string;
  document_status?: string;
  chunk_count?: number;
  chunk_preview?: Array<{ chunk_id: string; content: string; token_estimate?: number }>;
  citation_hit_rate?: number;
  quality_score?: number;
  covered_knowledge_points?: string[];
  failed_reason?: string;
  created_at?: string;
}

interface SearchResult {
  content: string;
  source_file?: string;
  document_id?: number;
  score?: number;
}

interface KnowledgeStats {
  document_count: number;
  indexed_document_count: number;
  failed_document_count: number;
  chunk_count: number;
  top_k: number;
  citation_hit_rate: number;
  quality_score: number;
  coverage_rate: number;
  covered_knowledge_points: Array<{ name: string; document_count: number }>;
}

interface RagDiagnostic {
  question: string;
  query_rewrite: string;
  retrieved_chunks: Array<{ rank: number; document_name: string; snippet: string; score: number }>;
  cited_chunks: Array<{ rank: number; document_name: string; snippet: string; score: number }>;
  unused_chunks: Array<{ rank: number; document_name: string; snippet: string; score: number }>;
  citation_confidence: number;
  unsupported_answer_risk: boolean;
  created_at?: string;
}

interface RagDiagnostics {
  document_count: number;
  chunk_count: number;
  average_chunk_length: number;
  top_k: number;
  retrieval_hit_rate: number;
  citation_coverage: number;
  unsupported_answer_rate: number;
  knowledge_quality_score: number;
  recent_retrieval_diagnostics: RagDiagnostic[];
  demo_fallback_note: string;
}

const courses = ref<Course[]>([]);
const { currentRole } = useRole();
const courseId = ref<number>();
const selectedFile = ref<File | null>(null);
const docs = ref<CourseDocument[]>([]);
const query = ref('Python 爬虫发送 HTTP 请求的基本步骤是什么？');
const results = ref<SearchResult[]>([]);
const stats = ref<KnowledgeStats | null>(null);
const ragDiagnostics = ref<RagDiagnostics | null>(null);
const docsLoading = ref(false);
const diagnosticsLoading = ref(false);
const uploading = ref(false);
const searching = ref(false);
const dragActive = ref(false);
const error = ref('');
const uploadMessage = ref('');
const searchMessage = ref('');
const operationMessage = ref('');
const topK = ref(5);

const selectedCourse = computed(() => courses.value.find((item) => item.id === courseId.value));
const canUpload = computed(() => currentRole.value !== 'student');
const showDiagnostics = computed(() => currentRole.value === 'admin');
const pageCopy = computed(() => {
  if (currentRole.value === 'student') {
    return {
      eyebrow: '学生端 · 知识库 / 课程资料',
      title: '课程资料与引用来源',
      description: '面向学生展示课程资料、推荐资料、最近学习、资料搜索和引用来源，弱化文档解析与向量化技术细节。',
      docTitle: '课程资料',
      searchTitle: '资料搜索',
      statsLabel: '可学习资料'
    };
  }
  if (currentRole.value === 'teacher') {
    return {
      eyebrow: '教师端 · 资源库',
      title: '课程资料上传与教学资源管理',
      description: '教师可上传课程资料、管理教学资源、分类标签、关联课程和学习路径，并推送给学生。',
      docTitle: '教学资源列表',
      searchTitle: '资源检索测试',
      statsLabel: '教学资料'
    };
  }
  return {
    eyebrow: '管理员端 · 知识库运营 / 文档解析',
    title: '文档解析、切片与 RAG 质量治理',
    description: '管理员关注文档解析状态、切片数量、向量化状态、失败原因、引用命中率、知识库质量评分和重新解析。',
    docTitle: '文档解析与运营列表',
    searchTitle: '检索与召回诊断',
    statsLabel: '运营文档'
  };
});
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
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '时间格式异常';
  return date.toLocaleString('zh-CN', {
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
    indexed: '已入库',
    parsing: '解析中',
    pending: '等待解析',
    failed: '解析失败'
  };
  return map[status || ''] || status || '未知';
}

function percent(value?: number | null) {
  const numeric = Number(value || 0);
  return Number.isFinite(numeric) ? Math.round(numeric * 100) : 0;
}

function shortText(value?: string, limit = 120) {
  const text = value?.trim() || '暂无片段内容';
  return text.length > limit ? `${text.slice(0, limit)}...` : text;
}

async function demoAction(label: string) {
  operationMessage.value = '';
  try {
    if (currentRole.value === 'admin' && ['重新解析', '查看解析日志'].includes(label)) {
      await api.post('/api/v1/events', {
        event_type: 'knowledge_base_reparsed',
        title: label,
        description: `${label} 已记录到知识库运营事件流。`,
        actor_role: 'admin',
        actor_name: 'demo_admin',
        target_type: 'knowledge_base',
        target_id: courseId.value || 'course-demo',
        related_course: selectedCourse.value?.title || '',
        status: 'success',
        metadata: { course_id: courseId.value, document_count: docs.value.length, demo: true }
      });
      operationMessage.value = `${label} 已写入事件日志。`;
      return;
    }
    operationMessage.value = `${label} 为 ${pageCopy.value.eyebrow} 演示操作，后续可接真实资源推送、收藏下载或重新解析任务。`;
  } catch (err) {
    operationMessage.value = err instanceof Error ? err.message : `${label} 记录失败。`;
  }
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
  diagnosticsLoading.value = true;
  error.value = '';
  try {
    const [docData, statData, diagnosticData] = await Promise.all([
      api.get<CourseDocument[]>(`/api/v1/knowledge-base/documents?course_id=${courseId.value}`),
      api.get<KnowledgeStats>(`/api/v1/knowledge-base/stats?course_id=${courseId.value}`),
      api.get<RagDiagnostics>(`/api/v1/knowledge-base/rag-diagnostics?course_id=${courseId.value}&top_k=${topK.value}`)
    ]);
    docs.value = docData;
    stats.value = statData;
    ragDiagnostics.value = diagnosticData;
  } catch (err) {
    error.value = err instanceof Error ? err.message : '文档列表加载失败';
  } finally {
    docsLoading.value = false;
    diagnosticsLoading.value = false;
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
    const data = await api.get<{ items: SearchResult[]; citation_hit_rate?: number }>(
      `/api/v1/knowledge-base/search?course_id=${courseId.value}&query=${encodeURIComponent(query.value.trim())}&top_k=${topK.value}`
    );
    results.value = data.items;
    if (typeof data.citation_hit_rate === 'number' && stats.value) {
      stats.value.citation_hit_rate = data.citation_hit_rate;
    }
    await loadDocs();
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
        <p class="eyebrow">{{ pageCopy.eyebrow }}</p>
        <h2>{{ pageCopy.title }}</h2>
        <p class="muted">{{ pageCopy.description }}</p>
        <p class="demo-note">质量评分、引用命中率和切片预览包含 demo/fallback 统计，真实 RAG 接入后可替换为检索服务指标。</p>
      </div>
      <label class="course-select">
        当前课程
        <select v-model.number="courseId" @change="loadDocs">
          <option v-for="course in courses" :key="course.id" :value="course.id">{{ course.title }}</option>
        </select>
      </label>
    </div>

    <p v-if="error" class="panel error-text">{{ error }}</p>
    <p v-if="operationMessage" class="panel muted">{{ operationMessage }}</p>

    <div class="overview-grid">
      <article class="stat overview-card">
        <span>{{ pageCopy.statsLabel }}</span>
        <strong>{{ docs.length }}</strong>
        <small>份</small>
      </article>
      <article class="stat overview-card">
        <span>{{ currentRole === 'student' ? '可引用资料' : '已解析文档' }}</span>
        <strong>{{ parsedCount }}</strong>
        <small>{{ docs.length ? `${Math.round((parsedCount / docs.length) * 100)}% 完成` : '等待上传' }}</small>
      </article>
      <article class="stat overview-card">
        <span>知识切片</span>
        <strong>{{ chunkCount }}</strong>
        <small>段</small>
      </article>
      <article class="stat overview-card">
        <span>覆盖率 / 质量分</span>
        <strong>{{ stats?.coverage_rate ?? 0 }}%</strong>
        <small>{{ stats?.quality_score ?? 0 }} 分</small>
      </article>
      <article class="stat overview-card">
        <span>引用命中率</span>
        <strong>{{ percent(stats?.citation_hit_rate) }}%</strong>
        <small>TopK {{ stats?.top_k ?? topK }}</small>
      </article>
      <article class="stat overview-card">
        <span>最近上传</span>
        <strong class="date-value">{{ latestUploadAt }}</strong>
        <small>{{ selectedCourse?.title || '未选择课程' }}</small>
      </article>
    </div>

    <div class="kb-layout">
      <section v-if="canUpload" class="panel">
        <div class="panel-title">
          <h2>{{ currentRole === 'teacher' ? '上传课程资料' : '文档上传与解析运营' }}</h2>
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
            {{ uploading ? '上传解析中...' : currentRole === 'teacher' ? '上传并关联课程' : '上传并构建知识库' }}
          </button>
          <span v-if="uploadMessage" class="success-text">{{ uploadMessage }}</span>
        </div>
      </section>
      <section v-else class="panel">
        <div class="panel-title">
          <h2>推荐资料</h2>
          <span class="muted">学习视角</span>
        </div>
        <div class="list">
          <div class="item compact">课程讲义与案例片段<span>可搜索</span></div>
          <div class="item compact">最近学习资料<span>{{ latestUploadAt }}</span></div>
          <div class="item compact">引用来源卡片<span>TutorChat 联动</span></div>
        </div>
        <div class="quick-grid">
          <button class="secondary" @click="demoAction('收藏资料')">收藏资料</button>
          <button class="secondary" @click="demoAction('模拟下载')">下载资料</button>
        </div>
      </section>

      <section class="panel">
        <div class="panel-title">
          <h2>{{ pageCopy.searchTitle }}</h2>
          <span class="muted">{{ currentRole === 'student' ? '查找课程资料和引用来源' : '验证知识库可用性' }}</span>
        </div>
        <div class="search-box">
          <label>
            TopK 参数
            <select v-model.number="topK">
              <option :value="3">3</option>
              <option :value="5">5</option>
              <option :value="8">8</option>
            </select>
          </label>
          <textarea v-model="query" />
          <button :disabled="searching || !courseId" @click="search">
            {{ searching ? '检索中...' : currentRole === 'student' ? '搜索课程资料' : '检索知识片段' }}
          </button>
        </div>
        <p v-if="searchMessage" class="muted">{{ searchMessage }}</p>
      </section>
    </div>

    <section v-if="showDiagnostics" class="panel">
      <div class="panel-title">
        <h2>可信 RAG 质量诊断</h2>
        <span class="muted">{{ diagnosticsLoading ? '诊断加载中...' : '启发式 demo/fallback 指标' }}</span>
      </div>
      <p class="demo-note">{{ ragDiagnostics?.demo_fallback_note || '当前指标基于本地记录和规则估计，不接入真实 RAGFlow。' }}</p>
      <div class="diagnostic-grid">
        <article class="stat overview-card">
          <span>文档 / Chunk</span>
          <strong>{{ ragDiagnostics?.document_count ?? docs.length }} / {{ ragDiagnostics?.chunk_count ?? chunkCount }}</strong>
          <small>平均 chunk {{ ragDiagnostics?.average_chunk_length ?? 0 }} 字符</small>
        </article>
        <article class="stat overview-card">
          <span>TopK 设置</span>
          <strong>{{ ragDiagnostics?.top_k ?? topK }}</strong>
          <small>检索片段数</small>
        </article>
        <article class="stat overview-card">
          <span>retrieval_hit_rate</span>
          <strong>{{ percent(ragDiagnostics?.retrieval_hit_rate) }}%</strong>
          <small>问题命中率</small>
        </article>
        <article class="stat overview-card">
          <span>citation_coverage</span>
          <strong>{{ percent(ragDiagnostics?.citation_coverage) }}%</strong>
          <small>引用覆盖</small>
        </article>
        <article class="stat overview-card">
          <span>unsupported_answer_rate</span>
          <strong>{{ percent(ragDiagnostics?.unsupported_answer_rate) }}%</strong>
          <small>无依据风险</small>
        </article>
        <article class="stat overview-card">
          <span>knowledge_quality_score</span>
          <strong>{{ ragDiagnostics?.knowledge_quality_score ?? 0 }}</strong>
          <small>启发式评分</small>
        </article>
      </div>
      <div class="diagnostic-list">
        <article v-for="item in ragDiagnostics?.recent_retrieval_diagnostics || []" :key="`${item.question}-${item.created_at}`" class="diagnostic-card">
          <div class="diagnostic-head">
            <div>
              <strong>{{ item.question }}</strong>
              <p>query rewrite：{{ item.query_rewrite }}</p>
            </div>
            <span :class="['risk-badge', { risk: item.unsupported_answer_risk }]">
              {{ item.unsupported_answer_risk ? '有无依据风险' : '引用可解释' }}
            </span>
          </div>
          <p class="muted">引用置信度 {{ item.citation_confidence }} · TopK {{ item.retrieved_chunks.length }}</p>
          <div class="chunk-columns">
            <div>
              <h3>TopK 检索片段</h3>
              <p v-for="chunk in item.retrieved_chunks" :key="`r-${chunk.rank}-${chunk.snippet}`">
                #{{ chunk.rank }} {{ chunk.document_name }}：{{ shortText(chunk.snippet) }}
              </p>
            </div>
            <div>
              <h3>最终引用片段</h3>
              <p v-for="chunk in item.cited_chunks" :key="`c-${chunk.rank}-${chunk.snippet}`">
                #{{ chunk.rank }} {{ chunk.document_name }}：{{ shortText(chunk.snippet) }}
              </p>
              <p v-if="!item.cited_chunks.length" class="muted">暂无最终引用片段。</p>
            </div>
            <div>
              <h3>未采用片段</h3>
              <p v-for="chunk in item.unused_chunks" :key="`u-${chunk.rank}-${chunk.snippet}`">
                #{{ chunk.rank }} {{ chunk.document_name }}：{{ shortText(chunk.snippet) }}
              </p>
              <p v-if="!item.unused_chunks.length" class="muted">暂无未采用片段。</p>
            </div>
          </div>
        </article>
        <p v-if="!diagnosticsLoading && !ragDiagnostics?.recent_retrieval_diagnostics?.length" class="empty-state">
          暂无检索诊断记录。先在 TutorChat 提问或运行演示数据脚本后，这里会显示最近检索链路。
        </p>
      </div>
    </section>
    <section v-else class="panel">
      <div class="panel-title">
        <h2>{{ currentRole === 'student' ? '引用来源说明' : '资源库质量摘要' }}</h2>
        <span class="muted">demo/fallback 边界</span>
      </div>
      <p class="demo-note">学生端和教师端默认弱化 RAG 技术指标；管理员端会展示完整可信 RAG 质量诊断。</p>
      <div class="role-grid">
        <article class="stat overview-card">
          <span>引用命中率</span>
          <strong>{{ percent(stats?.citation_hit_rate) }}%</strong>
          <small>用于说明回答依据</small>
        </article>
        <article class="stat overview-card">
          <span>知识库质量</span>
          <strong>{{ stats?.quality_score ?? 0 }}</strong>
          <small>演示评分</small>
        </article>
        <article class="stat overview-card">
          <span>推荐资料</span>
          <strong>{{ docs.length }}</strong>
          <small>可进入课程学习</small>
        </article>
      </div>
    </section>

    <section class="panel">
      <div class="panel-title">
        <h2>{{ pageCopy.docTitle }}</h2>
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
            <span v-if="currentRole !== 'student'">{{ doc.chunk_count ?? 0 }} 个切片</span>
            <span v-if="currentRole !== 'student'">质量 {{ doc.quality_score ?? '-' }}</span>
            <span>命中 {{ percent(doc.citation_hit_rate) }}%</span>
            <span>{{ formatDate(doc.created_at) }}</span>
          </div>
          <p v-if="doc.failed_reason" class="error-text">{{ doc.failed_reason }}</p>
          <div class="reference-list">
            <small v-for="point in doc.covered_knowledge_points || []" :key="point">{{ point }}</small>
          </div>
          <details v-if="doc.chunk_preview?.length">
            <summary>{{ currentRole === 'student' ? '引用片段预览' : '切片预览' }}</summary>
            <p v-for="chunk in doc.chunk_preview" :key="chunk.chunk_id">{{ chunk.content }}</p>
          </details>
          <div class="quick-grid doc-actions">
            <button v-if="currentRole === 'student'" class="secondary" @click="demoAction('收藏资料')">收藏</button>
            <button v-if="currentRole === 'student'" class="secondary" @click="demoAction('模拟下载资料')">下载</button>
            <button v-if="currentRole === 'teacher'" class="secondary" @click="demoAction('推送给学生')">推送给学生</button>
            <button v-if="currentRole === 'teacher'" class="secondary" @click="demoAction('关联学习路径')">关联路径</button>
            <button v-if="currentRole === 'admin'" class="secondary" @click="demoAction('重新解析')">重新解析</button>
            <button v-if="currentRole === 'admin'" class="secondary" @click="demoAction('查看解析日志')">解析日志</button>
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

.demo-note {
  margin: 8px 0 0;
  color: #955600;
  font-size: 13px;
}

.course-select {
  min-width: 260px;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}

.diagnostic-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
  margin-top: 12px;
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
.result-grid,
.diagnostic-list {
  display: grid;
  gap: 12px;
}

.doc-card,
.result-card,
.diagnostic-card {
  border: 1px solid #e4e9f1;
  border-radius: 8px;
  padding: 12px;
  background: #fbfcff;
}

.diagnostic-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.diagnostic-head p {
  margin: 6px 0 0;
  color: #66758a;
}

.chunk-columns {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
  margin-top: 12px;
}

.chunk-columns h3 {
  margin: 0 0 8px;
  font-size: 14px;
}

.chunk-columns p {
  margin: 6px 0;
  color: #39475a;
  line-height: 1.5;
}

.risk-badge {
  align-self: flex-start;
  white-space: nowrap;
  border-radius: 999px;
  padding: 5px 8px;
  color: #1f7a45;
  background: #effaf4;
  font-size: 12px;
}

.risk-badge.risk {
  color: #b42318;
  background: #fff0f0;
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

.reference-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.reference-list small {
  border-radius: 999px;
  padding: 5px 8px;
  color: #1453aa;
  background: #edf4ff;
}

details {
  margin-top: 10px;
  color: #39475a;
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
