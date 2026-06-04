<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { api, apiBase } from '../api/client';
import DataCard from '../components/DataCard.vue';
import EmptyState from '../components/EmptyState.vue';
import PageHeader from '../components/PageHeader.vue';
import StatCard from '../components/StatCard.vue';
import StatusBadge from '../components/StatusBadge.vue';
import { useRole } from '../composables/useRole';
import type { Course } from '../types';

type ReportStatus = 'generating' | 'completed' | 'failed' | string;

interface ReportSummary {
  report_abstract?: string;
  key_conclusions?: string[];
  evidence_chain?: Array<{
    conclusion: string;
    evidence_type: string;
    source_title: string;
    source_excerpt: string;
    confidence: number;
    related_knowledge_point: string;
  }>;
  learning_performance_summary?: string;
  weak_points?: string | string[];
  recommended_path?: Array<{ name?: string; target?: string }>;
  teaching_suggestions?: Array<{ title?: string; content?: string }> | string;
  references?: string[];
  citation_snippets?: Array<{ document: string; content: string; confidence?: number }>;
  regenerate_reason?: string;
  generated_at?: string;
}

interface ReportItem {
  id: number;
  course_id: number;
  student_profile_id?: number;
  report_title: string;
  report_path: string;
  created_at?: string;
  course_title?: string;
  student_name?: string;
  target_scope?: string;
  report_type?: string;
  status?: ReportStatus;
  report_status?: ReportStatus;
  quality_score?: number | null;
  citation_document_count?: number;
  report_url?: string;
  download_url?: string;
  summary?: ReportSummary;
}

interface ReportStats {
  report_count: number;
  weekly_new_count: number;
  completed_count: number;
  average_quality_score?: number | null;
}

const { currentRole } = useRole();
const reports = ref<ReportItem[]>([]);
const courses = ref<Course[]>([]);
const selectedReportId = ref<number | null>(null);
const statusFilter = ref('全部状态');
const typeFilter = ref('全部类型');
const keyword = ref('');
const loading = ref(true);
const error = ref('');
const operationMessage = ref('');
const stats = ref<ReportStats | null>(null);
const refreshing = ref(false);

const templates = [
  { title: '班级学习报告', desc: '汇总班级趋势、任务完成、薄弱知识点和干预建议', type: '班级报告', icon: '班' },
  { title: '学生画像报告', desc: '聚合单个学生画像、能力雷达、薄弱点和成长建议', type: '学生报告', icon: '像' },
  { title: '课程效果报告', desc: '分析课程进度、资源使用、测验表现和完成率', type: '课程报告', icon: '课' },
  { title: '教学改进报告', desc: '根据测评结果生成下一轮教学优化建议', type: '教学报告', icon: '改' }
];

const fallbackReports: ReportItem[] = [
  { id: 1, course_id: 1, student_profile_id: 1, report_title: '计科大三 1 班学习报告', report_path: 'reports/class-python.pdf', created_at: '2026-05-31T09:20:00', course_title: 'Python 爬虫基础与实践', student_name: '计科大三 1 班', report_type: '班级报告', report_status: 'completed', quality_score: 92, citation_document_count: 6, summary: { report_abstract: '班级整体进度稳定，HTTP 请求和异常处理仍是主要薄弱点。', key_conclusions: ['平均完成率 68%', '18 份作业待批改', '需关注 3 名学生'], weak_points: ['HTTP 请求', '异常处理'], teaching_suggestions: [{ title: '分层练习', content: '为低进度学生推送基础任务。' }] } },
  { id: 2, course_id: 1, student_profile_id: 1, report_title: '张三学生画像报告', report_path: 'reports/student-zhangsan.pdf', created_at: '2026-05-30T15:10:00', course_title: 'Python 爬虫基础与实践', student_name: '张三', report_type: '学生报告', report_status: 'completed', quality_score: 88, citation_document_count: 4, summary: { report_abstract: '张三综合评分 86，问题解决能力突出，工程实践仍需加强。', weak_points: ['数据存储', '工程实践'], teaching_suggestions: [{ title: '项目任务', content: '建议追加一个 CSV/SQLite 小项目。' }] } },
  { id: 3, course_id: 2, report_title: '人工智能导论课程效果报告', report_path: 'reports/course-ai.pdf', created_at: '2026-05-29T11:00:00', course_title: '人工智能导论', target_scope: '计科大三 2 班', report_type: '课程报告', report_status: 'generating', quality_score: null, citation_document_count: 3, summary: { report_abstract: '报告正在生成中。' } },
  { id: 4, course_id: 3, report_title: '数据结构教学改进报告', report_path: 'reports/teaching-ds.pdf', created_at: '2026-05-28T16:40:00', course_title: '数据结构与算法', target_scope: '计科大二 1 班', report_type: '教学报告', report_status: 'failed', quality_score: null, citation_document_count: 0, summary: { report_abstract: '上次生成失败，可重新生成。', regenerate_reason: '测验数据缺失。' } }
];

const reportRows = computed(() => reports.value.length ? reports.value : fallbackReports);
const statusOptions = ['全部状态', '生成中', '已完成', '失败'];
const typeOptions = computed(() => ['全部类型', ...Array.from(new Set(reportRows.value.map((item) => item.report_type || '学习报告')))]);

const filteredReports = computed(() => {
  const word = keyword.value.trim().toLowerCase();
  return reportRows.value.filter((report) => {
    const status = statusText(report.report_status || report.status);
    const matchStatus = statusFilter.value === '全部状态' || status === statusFilter.value;
    const matchType = typeFilter.value === '全部类型' || (report.report_type || '学习报告') === typeFilter.value;
    const matchWord = !word || `${report.report_title}${report.course_title || ''}${report.student_name || ''}`.toLowerCase().includes(word);
    return matchStatus && matchType && matchWord;
  });
});

const selectedReport = computed(() => reportRows.value.find((item) => item.id === selectedReportId.value) || filteredReports.value[0] || reportRows.value[0]);

const overview = computed(() => {
  const rows = reportRows.value;
  const completed = rows.filter((item) => statusText(item.report_status || item.status) === '已完成').length;
  const scores = rows.map((item) => item.quality_score).filter((item): item is number => typeof item === 'number');
  return {
    total: stats.value?.report_count ?? rows.length,
    weekly: stats.value?.weekly_new_count ?? rows.filter((item) => isRecent(item.created_at)).length,
    completed: stats.value?.completed_count ?? completed,
    quality: stats.value?.average_quality_score ?? (scores.length ? Math.round(scores.reduce((sum, item) => sum + item, 0) / scores.length) : 90),
    failed: rows.filter((item) => statusText(item.report_status || item.status) === '失败').length
  };
});

const statCards = computed(() => [
  { label: '报告总数', value: overview.value.total, unit: '份', hint: '全部报告', icon: '报' },
  { label: '本周新增', value: overview.value.weekly, unit: '份', hint: '近 7 天生成', icon: '周', tone: 'green' as const },
  { label: '已完成', value: overview.value.completed, unit: '份', hint: '可下载预览', icon: '完', tone: 'purple' as const },
  { label: '平均质量评分', value: overview.value.quality, unit: '分', hint: '引用与证据链质量', icon: '质', tone: 'cyan' as const },
  { label: '失败报告', value: overview.value.failed, unit: '份', hint: '可重新生成', icon: '失', tone: 'red' as const }
]);

function isRecent(value?: string) {
  if (!value) return false;
  const date = new Date(value).getTime();
  return Number.isFinite(date) && Date.now() - date <= 7 * 24 * 60 * 60 * 1000;
}

function formatDate(value?: string) {
  if (!value) return '暂无时间';
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString('zh-CN', { month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' });
}

function statusText(status?: ReportStatus) {
  const map: Record<string, string> = {
    generating: '生成中',
    completed: '已完成',
    success: '已完成',
    failed: '失败'
  };
  return map[status || ''] || status || '已完成';
}

function statusTone(status?: ReportStatus) {
  const text = statusText(status);
  if (text === '已完成') return 'success';
  if (text === '生成中') return 'warning';
  if (text === '失败') return 'danger';
  return 'neutral';
}

function courseTitle(report: ReportItem) {
  return report.course_title || courses.value.find((item) => item.id === report.course_id)?.title || `课程 #${report.course_id}`;
}

function suggestions(report: ReportItem) {
  const value = report.summary?.teaching_suggestions;
  if (Array.isArray(value)) return value;
  if (typeof value === 'string' && value.trim()) return [{ title: '教学建议', content: value }];
  return [{ title: '教学建议', content: '建议结合学习路径继续安排分层练习和针对性讲解。' }];
}

function weakPointText(report: ReportItem) {
  const value = report.summary?.weak_points;
  if (Array.isArray(value)) return value.join('、');
  return value || '暂无薄弱知识点摘要。';
}

function downloadHref(report: ReportItem) {
  const path = report.download_url || report.report_url || `/api/v1/reports/${report.id}/download`;
  return `${apiBase}${path}`;
}

function selectReport(report: ReportItem) {
  selectedReportId.value = report.id;
}

function demoAction(label: string) {
  operationMessage.value = `${label} 为演示操作，后续可接真实报告生成、预览、下载和审核流程。`;
}

async function regenerate(report?: ReportItem) {
  const target = report || selectedReport.value;
  if (!target?.student_profile_id) {
    operationMessage.value = '当前报告缺少学生画像 ID，已模拟触发重新生成。';
    return;
  }
  refreshing.value = true;
  operationMessage.value = '';
  try {
    await api.post<ReportItem>('/api/v1/reports/generate', {
      student_profile_id: target.student_profile_id,
      course_id: target.course_id,
      regenerate_reason: '教师端报告中心手动重新生成'
    });
    operationMessage.value = '已重新生成报告。';
    await loadReports();
  } catch (err) {
    operationMessage.value = err instanceof Error ? err.message : '重新生成失败，当前保留演示数据。';
  } finally {
    refreshing.value = false;
  }
}

function handleDownload(report: ReportItem, event: MouseEvent) {
  if (statusText(report.report_status || report.status) !== '已完成') {
    event.preventDefault();
    operationMessage.value = '报告尚未完成，暂不能下载。';
    return;
  }
  operationMessage.value = '正在打开报告下载链接。';
}

async function loadReports() {
  const [reportData, courseData, statData] = await Promise.all([
    api.get<ReportItem[]>('/api/v1/reports'),
    api.get<Course[]>('/api/v1/courses').catch(() => []),
    api.get<ReportStats>('/api/v1/reports/summary').catch(() => null)
  ]);
  reports.value = reportData;
  courses.value = courseData;
  stats.value = statData;
  selectedReportId.value = reportRows.value[0]?.id || null;
}

async function loadPage() {
  loading.value = true;
  error.value = '';
  try {
    await loadReports();
  } catch (err) {
    error.value = err instanceof Error ? err.message : '报告接口暂不可用，当前显示演示数据。';
    reports.value = [];
    stats.value = null;
    selectedReportId.value = fallbackReports[0].id;
  } finally {
    loading.value = false;
  }
}

onMounted(loadPage);
</script>

<template>
  <section class="page report-page">
    <PageHeader title="报告中心" description="生成、预览、下载和重新生成班级、学生、课程与教学改进报告。">
      <template #actions>
        <button class="secondary" @click="demoAction('批量导出')">批量导出</button>
        <button @click="regenerate()">一键生成报告</button>
      </template>
    </PageHeader>

    <p v-if="loading" class="panel muted">正在加载报告中心数据...</p>
    <p v-if="operationMessage" class="panel muted">{{ operationMessage }}</p>

    <div class="stat-grid">
      <StatCard v-for="item in statCards" :key="item.label" v-bind="item" />
    </div>

    <DataCard title="报告模板" subtitle="选择模板生成对应教学报告">
      <div class="template-grid">
        <article v-for="template in templates" :key="template.title" class="template-card">
          <span>{{ template.icon }}</span>
          <div>
            <strong>{{ template.title }}</strong>
            <p>{{ template.desc }}</p>
            <StatusBadge :label="template.type" tone="purple" />
          </div>
          <button class="secondary" @click="demoAction(`生成${template.title}`)">生成</button>
        </article>
      </div>
    </DataCard>

    <DataCard title="筛选报告" subtitle="按状态、类型和关键词筛选最近生成报告">
      <div class="filter-grid">
        <input v-model="keyword" placeholder="搜索报告标题、课程、学生..." />
        <select v-model="typeFilter">
          <option v-for="item in typeOptions" :key="item">{{ item }}</option>
        </select>
        <select v-model="statusFilter">
          <option v-for="item in statusOptions" :key="item">{{ item }}</option>
        </select>
      </div>
    </DataCard>

    <div class="report-layout">
      <DataCard title="最近生成报告" :subtitle="`${filteredReports.length} 份报告`">
        <template #action>
          <StatusBadge v-if="error" label="演示数据" tone="warning" />
        </template>
        <div class="report-list">
          <article v-for="report in filteredReports" :key="report.id" :class="['report-row', { active: selectedReport?.id === report.id }]">
            <button class="report-main" type="button" @click="selectReport(report)">
              <strong>{{ report.report_title }}</strong>
              <span>{{ courseTitle(report) }} · {{ report.student_name || report.target_scope || '班级范围' }}</span>
              <small>{{ formatDate(report.created_at) }} · 质量评分 {{ report.quality_score ?? '-' }}</small>
            </button>
            <StatusBadge :label="statusText(report.report_status || report.status)" :tone="statusTone(report.report_status || report.status)" />
            <div class="row-actions">
              <button class="ghost" @click="selectReport(report)">预览</button>
              <a class="download-link" :href="downloadHref(report)" target="_blank" @click="handleDownload(report, $event)">下载</a>
              <button class="secondary" :disabled="refreshing" @click="regenerate(report)">重新生成</button>
            </div>
          </article>
          <EmptyState v-if="!filteredReports.length" title="暂无报告" description="调整筛选条件或生成报告后会显示。" />
        </div>
      </DataCard>

      <DataCard title="报告预览" :subtitle="selectedReport ? statusText(selectedReport.report_status || selectedReport.status) : '暂无报告'">
        <template #action>
          <button class="secondary" @click="demoAction('打开预览')">打开预览</button>
        </template>
        <div v-if="selectedReport" class="preview-grid">
          <article class="preview-card wide">
            <span>报告摘要</span>
            <p>{{ selectedReport.summary?.report_abstract || selectedReport.summary?.learning_performance_summary || '暂无报告摘要。' }}</p>
          </article>
          <article class="preview-card">
            <span>报告类型</span>
            <p>{{ selectedReport.report_type || '学习报告' }}</p>
          </article>
          <article class="preview-card">
            <span>薄弱知识点</span>
            <p>{{ weakPointText(selectedReport) }}</p>
          </article>
          <article class="preview-card wide">
            <span>关键结论</span>
            <p v-for="item in selectedReport.summary?.key_conclusions || ['报告生成后会展示关键结论。']" :key="item">{{ item }}</p>
          </article>
          <article class="preview-card wide">
            <span>教学建议</span>
            <p v-for="item in suggestions(selectedReport)" :key="`${item.title}-${item.content}`"><strong>{{ item.title || '建议' }}</strong>：{{ item.content }}</p>
          </article>
          <article class="preview-card wide">
            <span>证据链</span>
            <div class="evidence-list">
              <p v-for="item in selectedReport.summary?.evidence_chain || []" :key="`${item.conclusion}-${item.source_title}`">
                <strong>{{ item.conclusion }}</strong> · {{ item.source_title }} · 置信度 {{ item.confidence }}
              </p>
              <p v-if="!selectedReport.summary?.evidence_chain?.length" class="muted">暂无证据链，重新生成报告后会补充引用来源。</p>
            </div>
          </article>
          <article class="preview-card wide">
            <span>推荐路径</span>
            <p v-for="stage in selectedReport.summary?.recommended_path || []" :key="`${stage.name}-${stage.target}`">
              <strong>{{ stage.name || '学习阶段' }}</strong>：{{ stage.target || '继续完成当前目标。' }}
            </p>
            <p v-if="!selectedReport.summary?.recommended_path?.length" class="muted">暂无推荐路径。</p>
          </article>
          <article class="preview-card wide">
            <span>报告文件</span>
            <p>{{ selectedReport.report_path }}</p>
          </article>
        </div>
        <EmptyState v-else title="暂无报告可预览" description="生成报告后会显示预览。" />
      </DataCard>
    </div>
  </section>
</template>

<style scoped>
.template-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.template-card {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 12px;
  border: 1px solid var(--color-border);
  border-radius: 16px;
  padding: 14px;
  background: #fbfdff;
}

.template-card > span {
  display: inline-grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border-radius: 14px;
  color: #fff;
  font-weight: 800;
  background: linear-gradient(135deg, var(--color-primary), var(--color-purple));
}

.template-card button {
  grid-column: 1 / -1;
}

.template-card p {
  margin: 6px 0 10px;
  font-size: 13px;
}

.filter-grid {
  display: grid;
  grid-template-columns: minmax(260px, 1fr) 180px 160px;
  gap: 12px;
}

.report-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(420px, 0.9fr);
  gap: 16px;
  align-items: start;
}

.report-list,
.preview-grid,
.evidence-list {
  display: grid;
  gap: 12px;
}

.report-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto auto;
  gap: 12px;
  align-items: center;
  border: 1px solid var(--color-border);
  border-radius: 16px;
  padding: 12px;
  background: #fbfdff;
}

.report-row.active {
  border-color: rgba(47, 107, 255, 0.55);
  background: var(--color-primary-light);
}

.report-main {
  display: grid;
  gap: 4px;
  padding: 0;
  color: var(--color-text-main);
  text-align: left;
  background: transparent;
  box-shadow: none;
}

.report-main span,
.report-main small {
  color: var(--color-text-sub);
}

.row-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.download-link {
  display: inline-flex;
  align-items: center;
  border-radius: 12px;
  padding: 9px 12px;
  color: var(--color-primary-dark);
  background: var(--color-primary-light);
  text-decoration: none;
  font-weight: 700;
}

.preview-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.preview-card {
  display: grid;
  gap: 8px;
  border: 1px solid var(--color-border);
  border-radius: 14px;
  padding: 12px;
  background: #fbfdff;
}

.preview-card.wide {
  grid-column: 1 / -1;
}

.preview-card span {
  color: var(--color-text-sub);
  font-size: 13px;
}

.preview-card p {
  margin: 0;
  line-height: 1.65;
}

@media (max-width: 1280px) {
  .template-grid,
  .report-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .filter-grid,
  .report-row,
  .preview-grid {
    grid-template-columns: 1fr;
  }
}
</style>
