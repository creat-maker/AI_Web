<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { api } from '../api/client';

type LogLevel = 'INFO' | 'WARNING' | 'ERROR' | 'SUCCESS' | string;
type LogCategory = 'all' | 'system' | 'qa' | 'knowledge' | 'agent' | 'report' | 'error';

interface LogItem {
  id: string;
  type?: string;
  time: string;
  created_at?: string;
  level: LogLevel;
  category: string;
  title?: string;
  content?: string;
  module: string;
  action: string;
  summary: string;
  status: string;
  source: string;
  course_id?: number | null;
  course_title?: string;
  related_id?: number | null;
  related_type?: string | null;
  error_message?: string;
  suggestion?: string;
  user?: string;
  duration_ms?: number;
  metadata?: Record<string, unknown>;
}

interface LogSummary {
  today_log_count: number;
  error_log_count: number;
  agent_run_count: number;
  question_count: number;
  total_count?: number;
}

const fallbackLogs: LogItem[] = [
  {
    id: 'local-system',
    time: new Date().toISOString(),
    level: 'INFO',
    category: 'system',
    module: 'Dashboard',
    action: '读取运行状态',
    summary: '日志接口暂不可用，页面已切换到本地兼容展示。',
    status: '演示',
    source: '前端 fallback',
    course_title: '暂无关联课程',
    related_type: 'system',
    suggestion: '确认后端服务已启动，并访问 /api/v1/logs 验证接口。'
  },
  {
    id: 'local-agent',
    time: new Date().toISOString(),
    level: 'WARNING',
    category: 'agent',
    module: 'AgentWorkflow',
    action: '运行工作流',
    summary: '暂无可读取的 Agent 运行日志，等待后端恢复或生成真实记录。',
    status: '待同步',
    source: '前端 fallback',
    course_title: '暂无关联课程',
    related_type: 'agent_run',
    suggestion: '进入 Agent 工作流页面运行一次完整学习流。'
  }
];

const categoryTabs: Array<{ label: string; value: LogCategory }> = [
  { label: '全部', value: 'all' },
  { label: '系统日志', value: 'system' },
  { label: '问答日志', value: 'qa' },
  { label: '知识库日志', value: 'knowledge' },
  { label: 'Agent 日志', value: 'agent' },
  { label: '报告日志', value: 'report' },
  { label: '错误日志', value: 'error' }
];

const levels = ['all', 'INFO', 'WARNING', 'ERROR', 'SUCCESS'];
const modules = ['all', 'Dashboard', 'TutorChat', 'KnowledgeBase', 'AgentWorkflow', 'ReportCenter', 'Settings'];

const logs = ref<LogItem[]>([]);
const summary = ref<LogSummary | null>(null);
const activeCategory = ref<LogCategory>('all');
const levelFilter = ref('all');
const moduleFilter = ref('all');
const keyword = ref('');
const startTime = ref('');
const endTime = ref('');
const sortOrder = ref<'desc' | 'asc'>('desc');
const selectedId = ref<string>('');
const loading = ref(true);
const refreshing = ref(false);
const error = ref('');
const fallbackActive = ref(false);

const filteredLogs = computed(() => {
  const word = keyword.value.trim().toLowerCase();
  const rows = logs.value.filter((item) => {
    const matchCategory =
      activeCategory.value === 'all'
      || (activeCategory.value === 'error' ? item.level === 'ERROR' : item.category === activeCategory.value);
    const matchLevel = levelFilter.value === 'all' || item.level === levelFilter.value;
    const matchModule = moduleFilter.value === 'all' || item.module === moduleFilter.value;
    const matchKeyword =
      !word
      || (item.title || '').toLowerCase().includes(word)
      || (item.content || '').toLowerCase().includes(word)
      || item.summary.toLowerCase().includes(word)
      || item.action.toLowerCase().includes(word)
      || item.module.toLowerCase().includes(word)
      || (item.type || '').toLowerCase().includes(word)
      || (item.status || '').toLowerCase().includes(word)
      || (item.error_message || '').toLowerCase().includes(word)
      || (item.course_title || '').toLowerCase().includes(word);
    const itemTime = new Date(item.created_at || item.time).getTime();
    const matchStart = !startTime.value || itemTime >= new Date(startTime.value).getTime();
    const matchEnd = !endTime.value || itemTime <= new Date(endTime.value).getTime();
    return matchCategory && matchLevel && matchModule && matchKeyword && matchStart && matchEnd;
  });
  return [...rows].sort((a, b) => {
    const left = new Date(a.created_at || a.time).getTime();
    const right = new Date(b.created_at || b.time).getTime();
    return sortOrder.value === 'desc' ? right - left : left - right;
  });
});

const selectedLog = computed(() => {
  return logs.value.find((item) => item.id === selectedId.value) || filteredLogs.value[0] || null;
});

const overviewCards = computed(() => {
  const today = new Date().toDateString();
  const todayCount = logs.value.filter((item) => new Date(item.time).toDateString() === today).length;
  return [
    { label: '今日日志数', value: summary.value?.today_log_count ?? todayCount, unit: '条' },
    { label: '错误日志数', value: summary.value?.error_log_count ?? logs.value.filter((item) => item.level === 'ERROR').length, unit: '条' },
    { label: 'Agent 运行次数', value: summary.value?.agent_run_count ?? logs.value.filter((item) => item.category === 'agent').length, unit: '次' },
    { label: '问答记录数', value: summary.value?.question_count ?? logs.value.filter((item) => item.category === 'qa').length, unit: '条' }
  ];
});

function formatDate(value?: string) {
  if (!value) return '暂无时间';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return '时间格式异常';
  return date.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  });
}

function durationText(value?: number) {
  const duration = Number(value || 0);
  if (!Number.isFinite(duration) || duration <= 0) return '暂无耗时';
  return duration >= 1000 ? `${(duration / 1000).toFixed(1)}s` : `${duration}ms`;
}

function levelText(level: LogLevel) {
  const map: Record<string, string> = {
    INFO: 'INFO',
    WARNING: 'WARNING',
    ERROR: 'ERROR',
    SUCCESS: 'SUCCESS'
  };
  return map[level] || level || 'INFO';
}

function moduleText(module: string) {
  const map: Record<string, string> = {
    Dashboard: 'Dashboard',
    TutorChat: 'TutorChat',
    KnowledgeBase: 'KnowledgeBase',
    AgentWorkflow: 'AgentWorkflow',
    ReportCenter: 'ReportCenter',
    Settings: 'Settings'
  };
  return map[module] || module || 'Unknown';
}

function relatedText(item: LogItem) {
  if (!item.related_id) return '暂无关联 ID';
  const map: Record<string, string> = {
    qa: '问答',
    report: '报告',
    agent_run: 'Agent 运行',
    document: '知识库文档',
    system: '系统'
  };
  return `${map[item.related_type || ''] || item.related_type || '记录'} #${item.related_id}`;
}

function selectLog(item: LogItem) {
  selectedId.value = item.id;
}

async function loadLogs() {
  const [logData, summaryData] = await Promise.all([
    api.get<LogItem[]>('/api/v1/logs'),
    api.get<LogSummary>('/api/v1/logs/summary').catch(() => null)
  ]);
  logs.value = logData;
  summary.value = summaryData;
  selectedId.value = logs.value.some((item) => item.id === selectedId.value) ? selectedId.value : logs.value[0]?.id || '';
}

async function loadPage() {
  loading.value = true;
  refreshing.value = true;
  error.value = '';
  fallbackActive.value = false;
  try {
    await loadLogs();
  } catch (err) {
    error.value = err instanceof Error ? err.message : '日志中心数据加载失败';
    fallbackActive.value = true;
    logs.value = fallbackLogs;
    summary.value = {
      today_log_count: fallbackLogs.length,
      error_log_count: fallbackLogs.filter((item) => item.level === 'ERROR').length,
      agent_run_count: fallbackLogs.filter((item) => item.category === 'agent').length,
      question_count: fallbackLogs.filter((item) => item.category === 'qa').length,
      total_count: fallbackLogs.length
    };
    selectedId.value = fallbackLogs[0]?.id || '';
  } finally {
    loading.value = false;
    refreshing.value = false;
  }
}

onMounted(loadPage);
</script>

<template>
  <section class="page logs-page">
    <div class="panel logs-hero">
      <div>
        <p class="eyebrow">日志管理中心</p>
        <h2>系统运行、问答、知识库、Agent 与报告生成追踪</h2>
        <p class="muted">聚合已有业务记录形成兼容日志视图，用于演示运行链路和问题定位，不暴露敏感信息。</p>
      </div>
      <div class="hero-action">
        <span>当前日志</span>
        <strong>{{ selectedLog ? moduleText(selectedLog.module) : '暂无日志' }}</strong>
        <small>{{ selectedLog ? formatDate(selectedLog.time) : '等待加载' }}</small>
      </div>
    </div>

    <p v-if="error" class="panel error-text">{{ error }}</p>
    <p v-if="fallbackActive" class="panel muted">接口暂不可用，页面已保留 fallback 展示，避免白屏。</p>
    <p v-else-if="loading" class="panel muted">正在加载日志中心数据...</p>

    <div class="overview-grid">
      <article v-for="item in overviewCards" :key="item.label" class="stat overview-card">
        <span>{{ item.label }}</span>
        <strong>{{ item.value }}</strong>
        <small>{{ item.unit }}</small>
      </article>
    </div>

    <section class="panel">
      <div class="panel-title">
        <h2>日志分类</h2>
        <span class="muted">{{ filteredLogs.length }} / {{ logs.length }} 条</span>
      </div>
      <div class="tabs">
        <button
          v-for="tab in categoryTabs"
          :key="tab.value"
          type="button"
          class="secondary tab-button"
          :class="{ active: activeCategory === tab.value }"
          @click="activeCategory = tab.value"
        >
          {{ tab.label }}
        </button>
      </div>
      <div class="filter-grid">
        <label>
          日志级别
          <select v-model="levelFilter">
            <option v-for="item in levels" :key="item" :value="item">{{ item === 'all' ? '全部级别' : item }}</option>
          </select>
        </label>
        <label>
          模块来源
          <select v-model="moduleFilter">
            <option v-for="item in modules" :key="item" :value="item">{{ item === 'all' ? '全部模块' : item }}</option>
          </select>
        </label>
        <label>
          关键词
          <input v-model="keyword" placeholder="搜索内容、操作、模块或课程" />
        </label>
        <label>
          开始时间
          <input v-model="startTime" type="datetime-local" />
        </label>
        <label>
          结束时间
          <input v-model="endTime" type="datetime-local" />
        </label>
        <label>
          时间排序
          <select v-model="sortOrder">
            <option value="desc">最新在前</option>
            <option value="asc">最早在前</option>
          </select>
        </label>
        <button type="button" :disabled="refreshing" @click="loadPage">
          {{ refreshing ? '刷新中...' : '刷新日志' }}
        </button>
      </div>
    </section>

    <div class="logs-layout">
      <section class="panel">
        <div class="panel-title">
          <h2>日志列表</h2>
          <span class="muted">按分类、级别和关键词定位</span>
        </div>
        <div class="log-list">
          <article v-for="item in filteredLogs" :key="item.id" class="log-card" :class="{ active: selectedLog?.id === item.id }">
            <button class="log-main" type="button" @click="selectLog(item)">
              <div class="log-head">
                <span :class="['level-pill', item.level]">{{ levelText(item.level) }}</span>
                <strong>{{ moduleText(item.module) }} · {{ item.action }}</strong>
                <small>{{ formatDate(item.time) }}</small>
              </div>
              <p>{{ item.content || item.summary }}</p>
              <div class="log-meta">
                <span>{{ item.course_title || '暂无关联课程' }}</span>
                <span>{{ item.status }}</span>
                <span>{{ item.type || item.category }}</span>
                <span>{{ durationText(item.duration_ms) }}</span>
                <span>{{ relatedText(item) }}</span>
              </div>
            </button>
            <button type="button" class="secondary detail-button" @click="selectLog(item)">详情</button>
          </article>
          <p v-if="!filteredLogs.length && !loading" class="empty-state">暂无符合条件的日志。可调整筛选条件或先运行问答、知识库上传、Agent 工作流。</p>
        </div>
      </section>

      <section class="panel detail-panel">
        <div class="panel-title">
          <h2>日志详情预览</h2>
          <span class="muted">{{ selectedLog ? levelText(selectedLog.level) : '暂无' }}</span>
        </div>
        <div v-if="selectedLog" class="detail-grid">
          <article class="detail-block">
            <span>日志标题</span>
            <p>{{ selectedLog.title || selectedLog.action || '暂无标题' }}</p>
          </article>
          <article class="detail-block">
            <span>日志类型 / 用户 / 耗时</span>
            <p>{{ selectedLog.type || selectedLog.category }} / {{ selectedLog.user || 'demo_teacher' }} / {{ durationText(selectedLog.duration_ms) }}</p>
          </article>
          <article class="detail-block">
            <span>请求来源</span>
            <p>{{ selectedLog.source || '暂无来源' }}</p>
          </article>
          <article class="detail-block">
            <span>执行摘要</span>
            <p>{{ selectedLog.content || selectedLog.summary }}</p>
          </article>
          <article class="detail-block">
            <span>关联课程</span>
            <p>{{ selectedLog.course_title || '暂无关联课程' }}</p>
          </article>
          <article class="detail-block">
            <span>关联报告或问答 ID</span>
            <p>{{ relatedText(selectedLog) }}</p>
          </article>
          <article class="detail-block">
            <span>错误信息</span>
            <p :class="{ 'error-text': selectedLog.error_message }">{{ selectedLog.error_message || '暂无错误信息' }}</p>
          </article>
          <article class="detail-block">
            <span>建议处理方式</span>
            <p>{{ selectedLog.suggestion || '当前日志无需额外处理。' }}</p>
          </article>
          <article class="detail-block">
            <span>Metadata</span>
            <pre>{{ JSON.stringify(selectedLog.metadata || {}, null, 2) }}</pre>
          </article>
        </div>
        <p v-else-if="!loading" class="empty-state">暂无日志可预览。</p>
      </section>
    </div>
  </section>
</template>

<style scoped>
.logs-page {
  gap: 18px;
}

.logs-hero,
.panel-title,
.log-head,
.log-meta {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.logs-hero {
  align-items: center;
}

.logs-hero h2 {
  margin: 0 0 8px;
  font-size: 24px;
}

.eyebrow {
  margin: 0 0 6px;
  color: #2264d1;
  font-size: 13px;
  font-weight: 700;
}

.hero-action {
  width: 300px;
  border: 1px solid #d9e0ea;
  border-radius: 8px;
  padding: 14px;
  background: #f8fbff;
}

.hero-action span,
.hero-action small,
.overview-card small,
.detail-block span {
  display: block;
  color: #66758a;
}

.hero-action strong {
  display: block;
  margin: 6px 0;
}

.overview-grid,
.filter-grid,
.detail-grid {
  display: grid;
  gap: 12px;
}

.overview-grid {
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
}

.overview-card {
  min-height: 112px;
}

.tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 14px;
}

.tab-button.active {
  color: #fff;
  background: #2264d1;
}

.filter-grid {
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  align-items: end;
}

.logs-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(320px, 0.85fr);
  gap: 16px;
  align-items: start;
}

.log-list {
  display: grid;
  gap: 10px;
}

.log-card,
.detail-block {
  border: 1px solid #e4e9f1;
  border-radius: 8px;
  padding: 12px;
  background: #fbfcff;
}

.log-card {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 10px;
  align-items: center;
}

.log-card.active {
  border-color: #2264d1;
  background: #f8fbff;
}

.log-main {
  width: 100%;
  padding: 0;
  color: #1c2430;
  text-align: left;
  background: transparent;
}

.log-head {
  align-items: center;
}

.log-head strong {
  flex: 1;
}

.log-head small {
  color: #66758a;
  white-space: nowrap;
}

.log-main p,
.detail-block p {
  margin: 8px 0 0;
  color: #39475a;
  line-height: 1.55;
}

.log-meta {
  flex-wrap: wrap;
  justify-content: flex-start;
  margin-top: 10px;
  color: #66758a;
  font-size: 13px;
}

.level-pill {
  border-radius: 999px;
  padding: 5px 8px;
  font-size: 12px;
  color: #1453aa;
  background: #edf4ff;
}

.level-pill.SUCCESS {
  color: #1f7a45;
  background: #effaf4;
}

.level-pill.WARNING {
  color: #955600;
  background: #fff7e8;
}

.level-pill.ERROR {
  color: #b42318;
  background: #fff0f0;
}

.detail-button {
  white-space: nowrap;
}

.detail-grid {
  grid-template-columns: 1fr;
}

.detail-block pre {
  max-height: 260px;
  overflow: auto;
  margin: 8px 0 0;
}

.empty-state {
  margin: 0;
  color: #66758a;
}

.error-text {
  color: #b42318;
}

button:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

@media (max-width: 1080px) {
  .logs-layout,
  .logs-hero,
  .panel-title,
  .log-head {
    display: grid;
  }

  .hero-action {
    width: auto;
  }
}

@media (max-width: 720px) {
  .log-card {
    grid-template-columns: 1fr;
  }
}
</style>
