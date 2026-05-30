<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import { api, apiBase } from '../api/client';
import { useRole } from '../composables/useRole';
import type { Course } from '../types';

type ReportStatus = 'generating' | 'completed' | 'failed' | string;

interface ReportSummary {
  report_abstract?: string;
  generation_basis?: string[];
  key_conclusions?: string[];
  evidence_chain?: Array<{
    conclusion: string;
    evidence_type: 'document' | 'quiz' | 'chat' | 'mastery' | 'agent_run' | string;
    source_title: string;
    source_excerpt: string;
    confidence: number;
    related_knowledge_point: string;
  }>;
  learning_performance_summary?: string;
  weak_points?: string | string[];
  recommended_path?: Array<{ name?: string; target?: string }>;
  learning_path?: Array<{ step?: string; goal?: string }>;
  teaching_suggestions?: Array<{ title?: string; content?: string }> | string;
  learning_suggestions?: string[];
  references?: string[];
  citation_documents?: Array<{ name: string; type?: string; hit_count?: number }>;
  citation_snippets?: Array<{ document: string; content: string; confidence?: number }>;
  regenerate_reason?: string;
  generated_at?: string;
}

interface ReportItem {
  id: number;
  report_id?: number;
  course_id: number;
  student_profile_id?: number;
  report_title: string;
  report_path: string;
  report_json?: Record<string, unknown>;
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

const route = useRoute();
const { currentRole } = useRole();
const reports = ref<ReportItem[]>([]);
const courses = ref<Course[]>([]);
const selectedReportId = ref<number | null>(null);
const courseFilter = ref<number | 'all'>('all');
const statusFilter = ref<string>('all');
const keyword = ref('');
const loading = ref(true);
const refreshing = ref(false);
const error = ref('');
const fallbackActive = ref(false);
const operationMessage = ref('');
const stats = ref<ReportStats | null>(null);
const events = ref<Array<{ id: number; event_type: string; title: string; description: string; metadata?: Record<string, any> }>>([]);

const fallbackReports: ReportItem[] = [];

const pageCopy = computed(() => {
  if (currentRole.value === 'student') {
    return {
      eyebrow: '学生端 · 学习报告',
      title: '我的学习总结与下一步建议',
      description: '查看学习时长、任务完成率、知识点掌握度、薄弱点、推荐资源和学习路径调整建议。',
      listTitle: '我的学习报告',
      detailTitle: '学习报告详情',
      actionHint: '学生端关注学习建议和证据来源'
    };
  }
  if (currentRole.value === 'teacher') {
    return {
      eyebrow: '教师端 · 报告中心',
      title: '学生、班级、课程与测验报告',
      description: '查看学生报告、班级报告、课程报告、测验报告、风险学生报告、证据链和干预建议。',
      listTitle: '教学报告列表',
      detailTitle: '报告证据与干预建议',
      actionHint: '教师端关注下载、分享和重新生成'
    };
  }
  return {
    eyebrow: '管理员端 · 报告审核中心',
    title: 'AI 生成报告审核与治理',
    description: '审核 AI 生成报告的内容安全、引用来源、证据链和质量评分，支持通过、驳回重生成和查看审核日志。',
    listTitle: '待审核与历史报告',
    detailTitle: '审核详情与证据链',
    actionHint: '管理员端关注内容安全和引用合规'
  };
});

const filteredReports = computed(() => {
  const word = keyword.value.trim().toLowerCase();
  return reports.value.filter((item) => {
    const status = item.report_status || item.status || 'completed';
    const matchCourse = courseFilter.value === 'all' || item.course_id === courseFilter.value;
    const matchStatus = statusFilter.value === 'all' || status === statusFilter.value;
    const matchKeyword = !word || item.report_title.toLowerCase().includes(word);
    return matchCourse && matchStatus && matchKeyword;
  });
});

const selectedReport = computed(() => {
  return reports.value.find((item) => item.id === selectedReportId.value) || filteredReports.value[0] || null;
});
const answerImpacts = computed(() => events.value.filter((item) => item.event_type === 'question_answered').slice(0, 3));

const overview = computed(() => {
  const completed = reports.value.filter((item) => (item.report_status || item.status || 'completed') === 'completed').length;
  const qualityScores = reports.value
    .map((item) => item.quality_score)
    .filter((value): value is number => typeof value === 'number');
  return {
    report_count: stats.value?.report_count ?? reports.value.length,
    weekly_new_count: stats.value?.weekly_new_count ?? reports.value.filter((item) => isRecent(item.created_at)).length,
    completed_count: stats.value?.completed_count ?? completed,
    average_quality_score:
      stats.value?.average_quality_score ?? (qualityScores.length ? Number((qualityScores.reduce((sum, item) => sum + item, 0) / qualityScores.length).toFixed(1)) : null)
  };
});

const summaryCards = computed(() => [
  { label: currentRole.value === 'student' ? '我的报告' : currentRole.value === 'teacher' ? '教学报告' : '报告总数', value: overview.value.report_count, unit: '份' },
  { label: '本周新增报告', value: overview.value.weekly_new_count, unit: '份' },
  { label: '已完成报告', value: overview.value.completed_count, unit: '份' },
  {
    label: '平均质量评分',
    value: overview.value.average_quality_score ?? '暂无',
    unit: overview.value.average_quality_score == null ? '' : '分'
  }
]);

function isRecent(value?: string) {
  if (!value) return false;
  const date = new Date(value).getTime();
  return Number.isFinite(date) && Date.now() - date <= 7 * 24 * 60 * 60 * 1000;
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

function statusText(status?: ReportStatus) {
  const map: Record<string, string> = {
    generating: '生成中',
    completed: '已完成',
    failed: '失败',
    success: '已完成'
  };
  return map[status || ''] || status || '已完成';
}

function courseTitle(report: ReportItem) {
  return report.course_title || courses.value.find((item) => item.id === report.course_id)?.title || `课程 #${report.course_id}`;
}

function weakPointText(report: ReportItem) {
  const value = report.summary?.weak_points;
  if (Array.isArray(value)) return value.join('、');
  return value || '暂无薄弱知识点摘要。';
}

function suggestions(report: ReportItem) {
  const value = report.summary?.teaching_suggestions;
  if (Array.isArray(value)) return value;
  if (typeof value === 'string' && value.trim()) return [{ title: '教学建议', content: value }];
  return [{ title: '教学建议', content: '建议结合学习路径继续安排分层练习和针对性讲解。' }];
}

function downloadHref(report: ReportItem) {
  const path = report.download_url || report.report_url || `/api/v1/reports/${report.id}/download`;
  return `${apiBase}${path}`;
}

function selectReport(report: ReportItem) {
  selectedReportId.value = report.id;
  operationMessage.value = '';
}

function handleDownload(report: ReportItem, event: MouseEvent) {
  if ((report.report_status || report.status) !== 'completed') {
    event.preventDefault();
    operationMessage.value = '报告尚未完成，暂不能下载。';
    return;
  }
  operationMessage.value = '正在打开报告下载链接。';
}

async function demoAction(label: string) {
  operationMessage.value = '';
  try {
    if (currentRole.value === 'admin' && ['批量通过', '内容安全检查', '审核日志', '审核通过'].includes(label)) {
      await api.post('/api/v1/events/admin-review', {
        event_type: 'admin_review_completed',
        title: label,
        description: `${label} 已记录，报告审核中心完成一次 demo/fallback 审核动作。`,
        actor_role: 'admin',
        actor_name: 'demo_admin',
        target_type: 'learning_report',
        target_id: selectedReport.value?.id || 'report-demo',
        status: 'success',
        metadata: { report_title: selectedReport.value?.report_title, demo: true }
      });
      operationMessage.value = `${label} 已写入管理员审核事件。`;
      await loadEvents();
      return;
    }
    operationMessage.value = `${label} 为 ${pageCopy.value.eyebrow} 演示操作，后续可接真实审批、分享或通知流程。`;
  } catch (err) {
    operationMessage.value = err instanceof Error ? err.message : `${label} 记录失败。`;
  }
}

async function loadEvents() {
  events.value = await api.get<Array<{ id: number; event_type: string; title: string; description: string; metadata?: Record<string, any> }>>('/api/v1/events?limit=30').catch(() => []);
}

async function regenerate(report: ReportItem) {
  if (!report.student_profile_id) {
    operationMessage.value = '当前报告缺少学生画像 ID，暂不能自动重新生成。';
    return;
  }
  refreshing.value = true;
  operationMessage.value = '';
  try {
    const nextReport = await api.post<ReportItem>('/api/v1/reports/generate', {
      student_profile_id: report.student_profile_id,
      course_id: report.course_id,
      regenerate_reason: '比赛演示手动模拟重新生成'
    });
    operationMessage.value = '已重新生成报告。';
    await loadReports(nextReport.id);
  } catch (err) {
    operationMessage.value = err instanceof Error ? err.message : '重新生成失败，请稍后重试。';
  } finally {
    refreshing.value = false;
  }
}

async function loadReports(preferredId?: number) {
  const [reportData, courseData, statData, eventData] = await Promise.all([
    api.get<ReportItem[]>('/api/v1/reports'),
    api.get<Course[]>('/api/v1/courses').catch(() => []),
    api.get<ReportStats>('/api/v1/reports/summary').catch(() => null),
    api.get<Array<{ id: number; event_type: string; title: string; description: string; metadata?: Record<string, any> }>>('/api/v1/events?limit=30').catch(() => [])
  ]);
  reports.value = reportData;
  courses.value = courseData;
  stats.value = statData;
  events.value = eventData;

  const queryReportId = Number(route.query.report_id || 0);
  const targetId = preferredId || queryReportId || selectedReportId.value || reports.value[0]?.id || null;
  selectedReportId.value = reports.value.some((item) => item.id === targetId) ? targetId : reports.value[0]?.id || null;
}

async function loadPage() {
  loading.value = true;
  error.value = '';
  fallbackActive.value = false;
  try {
    await loadReports();
  } catch (err) {
    error.value = err instanceof Error ? err.message : '报告中心数据加载失败';
    fallbackActive.value = true;
    reports.value = fallbackReports;
    stats.value = null;
  } finally {
    loading.value = false;
  }
}

onMounted(loadPage);
</script>

<template>
  <section class="page report-page">
    <div class="panel report-hero">
      <div>
        <p class="eyebrow">{{ pageCopy.eyebrow }}</p>
        <h2>{{ pageCopy.title }}</h2>
        <p class="muted">{{ pageCopy.description }}</p>
        <p class="demo-note">引用片段和质量评分包含 demo/fallback 统计，后续可替换为真实评估器与引用追踪。</p>
      </div>
      <div class="hero-action">
        <span>当前预览</span>
        <strong>{{ selectedReport?.report_title || '暂无报告' }}</strong>
      </div>
    </div>

    <p v-if="error" class="panel error-text">{{ error }}</p>
    <p v-if="fallbackActive" class="panel muted">接口暂不可用，页面已保留 fallback 展示，避免白屏。</p>
    <p v-else-if="loading" class="panel muted">正在加载报告中心数据...</p>
    <p v-if="operationMessage" class="panel muted">{{ operationMessage }}</p>

    <section v-if="!loading" class="panel role-action-panel">
      <div class="panel-title">
        <h2>角色操作重点</h2>
        <span class="muted">{{ pageCopy.actionHint }}</span>
      </div>
      <div class="quick-grid">
        <button v-if="currentRole === 'student'" class="secondary" @click="demoAction('查看下一步建议')">下一步建议</button>
        <button v-if="currentRole === 'student'" class="secondary" @click="demoAction('加入学习路径调整')">调整学习路径</button>
        <button v-if="currentRole === 'student'" class="secondary" @click="demoAction('查看推荐资源')">推荐资源</button>
        <button v-if="currentRole === 'teacher'" class="secondary" @click="demoAction('生成班级报告')">班级报告</button>
        <button v-if="currentRole === 'teacher'" class="secondary" @click="demoAction('分享给学生')">分享给学生</button>
        <button v-if="currentRole === 'teacher'" class="secondary" @click="demoAction('添加干预建议')">干预建议</button>
        <button v-if="currentRole === 'admin'" class="secondary" @click="demoAction('批量通过')">批量通过</button>
        <button v-if="currentRole === 'admin'" class="secondary" @click="demoAction('内容安全检查')">安全检查</button>
        <button v-if="currentRole === 'admin'" class="secondary" @click="demoAction('审核日志')">审核日志</button>
      </div>
    </section>

    <div class="overview-grid">
      <article v-for="item in summaryCards" :key="item.label" class="stat overview-card">
        <span>{{ item.label }}</span>
        <strong>{{ item.value }}</strong>
        <small>{{ item.unit || ' ' }}</small>
      </article>
    </div>

    <section class="panel">
      <div class="panel-title">
        <h2>筛选与搜索</h2>
        <span class="muted">按课程、状态和报告标题定位</span>
      </div>
      <div class="filter-grid">
        <label>
          课程
          <select v-model="courseFilter">
            <option value="all">全部课程</option>
            <option v-for="course in courses" :key="course.id" :value="course.id">{{ course.title }}</option>
          </select>
        </label>
        <label>
          状态
          <select v-model="statusFilter">
            <option value="all">全部状态</option>
            <option value="generating">生成中</option>
            <option value="completed">已完成</option>
            <option value="failed">失败</option>
          </select>
        </label>
        <label>
          关键词
          <input v-model="keyword" placeholder="搜索报告标题" />
        </label>
      </div>
    </section>

    <div class="report-layout">
      <section class="panel">
        <div class="panel-title">
          <h2>{{ pageCopy.listTitle }}</h2>
          <span class="muted">{{ filteredReports.length }} / {{ reports.length }} 份</span>
        </div>
        <div class="report-list">
          <article
            v-for="report in filteredReports"
            :key="report.id"
            class="report-card"
            :class="{ active: selectedReport?.id === report.id }"
          >
            <button class="card-main" type="button" @click="selectReport(report)">
              <strong>{{ report.report_title }}</strong>
              <span>{{ courseTitle(report) }} · {{ report.student_name || report.target_scope || '未绑定学生' }} · {{ report.report_type || '学习报告' }}</span>
              <span>引用文档 {{ report.citation_document_count ?? report.summary?.citation_documents?.length ?? 0 }} 份</span>
              <small>{{ formatDate(report.created_at) }}</small>
            </button>
            <div class="card-actions">
              <span :class="['status-pill', report.report_status || report.status || 'completed']">
                {{ statusText(report.report_status || report.status) }}
              </span>
              <button class="secondary" type="button" @click="selectReport(report)">{{ currentRole === 'admin' ? '审核详情' : '查看' }}</button>
              <a v-if="currentRole !== 'admin'" :href="downloadHref(report)" target="_blank" @click="handleDownload(report, $event)">{{ currentRole === 'student' ? '下载报告' : '下载/分享' }}</a>
              <button v-if="currentRole === 'teacher'" class="secondary" type="button" :disabled="refreshing" @click="regenerate(report)">
                {{ refreshing ? '处理中...' : '重新生成' }}
              </button>
              <button v-if="currentRole === 'admin'" class="secondary" type="button" @click="demoAction('审核通过')">通过</button>
              <button v-if="currentRole === 'admin'" class="secondary" type="button" :disabled="refreshing" @click="regenerate(report)">
                {{ refreshing ? '处理中...' : '驳回重生成' }}
              </button>
            </div>
          </article>
          <p v-if="!filteredReports.length && !loading" class="empty-state">暂无符合条件的报告。</p>
        </div>
      </section>

      <section class="panel preview-panel">
        <div class="panel-title">
          <h2>{{ pageCopy.detailTitle }}</h2>
          <span class="muted">{{ selectedReport ? formatDate(selectedReport.summary?.generated_at || selectedReport.created_at) : '暂无时间' }}</span>
        </div>

        <div v-if="selectedReport" class="preview-grid">
          <article class="preview-card wide">
            <span>报告摘要</span>
            <p>{{ selectedReport.summary?.report_abstract || selectedReport.summary?.learning_performance_summary || '暂无报告摘要。' }}</p>
          </article>
          <article class="preview-card wide">
            <span>关键结论</span>
            <div class="conclusion-list">
              <p v-for="item in selectedReport.summary?.key_conclusions || []" :key="item">{{ item }}</p>
              <p v-if="!selectedReport.summary?.key_conclusions?.length" class="muted">暂无关键结论，报告生成后会自动补齐。</p>
            </div>
          </article>
          <article class="preview-card wide">
            <span>Evidence Chain / 证据链</span>
            <div class="evidence-list">
              <article v-for="item in selectedReport.summary?.evidence_chain || []" :key="`${item.conclusion}-${item.source_title}`" class="evidence-card">
                <strong>{{ item.conclusion }}</strong>
                <p>{{ item.evidence_type }} · {{ item.source_title }} · 置信度 {{ item.confidence }}</p>
                <p>{{ item.source_excerpt }}</p>
                <small>关联知识点：{{ item.related_knowledge_point }}</small>
              </article>
              <p v-if="!selectedReport.summary?.evidence_chain?.length" class="muted">暂无证据链。当前报告需要重新生成或补充演示数据。</p>
            </div>
          </article>
          <article class="preview-card wide">
            <span>{{ currentRole === 'student' ? '我的学习总结' : '学习表现摘要' }}</span>
            <p>{{ selectedReport.summary?.learning_performance_summary || '暂无学习表现摘要。' }}</p>
          </article>
          <article class="preview-card">
            <span>薄弱知识点</span>
            <p>{{ weakPointText(selectedReport) }}</p>
          </article>
          <article class="preview-card">
            <span>报告状态</span>
            <p>{{ statusText(selectedReport.report_status || selectedReport.status) }}{{ selectedReport.quality_score !== null && selectedReport.quality_score !== undefined ? ` · ${selectedReport.quality_score} 分` : '' }}</p>
          </article>
          <article class="preview-card wide">
            <span>生成依据</span>
            <div class="reference-list">
              <small v-for="item in selectedReport.summary?.generation_basis || []" :key="item">{{ item }}</small>
            </div>
          </article>
          <article class="preview-card wide">
            <span>推荐学习路径</span>
            <div v-if="selectedReport.summary?.recommended_path?.length" class="path-list">
              <p v-for="stage in selectedReport.summary.recommended_path" :key="`${stage.name}-${stage.target}`">
                <strong>{{ stage.name || '学习阶段' }}</strong>：{{ stage.target || '继续完成当前学习目标。' }}
              </p>
            </div>
            <p v-else>暂无推荐学习路径。</p>
          </article>
          <article class="preview-card wide">
            <span>{{ currentRole === 'student' ? '下一步建议 / 推荐资源' : currentRole === 'teacher' ? '干预建议' : '审核关注点' }}</span>
            <div class="suggestion-list">
              <p v-for="item in suggestions(selectedReport)" :key="`${item.title}-${item.content}`">
                <strong>{{ item.title || '教学建议' }}</strong>：{{ item.content || '建议补充针对性练习。' }}
              </p>
            </div>
          </article>
          <article class="preview-card wide">
            <span>引用来源 / 生成依据</span>
            <div class="reference-list">
              <small v-for="item in selectedReport.summary?.references || ['学生画像', '学习路径', '测评反馈']" :key="item">{{ item }}</small>
            </div>
          </article>
          <article class="preview-card wide">
            <span>引用文档与片段</span>
            <div class="suggestion-list">
              <p v-for="item in selectedReport.summary?.citation_snippets || []" :key="`${item.document}-${item.content}`">
                <strong>{{ item.document }}</strong>：{{ item.content }}（相关度 {{ item.confidence ?? '-' }}）
              </p>
              <p v-if="!selectedReport.summary?.citation_snippets?.length" class="muted">暂无引用片段，生成报告后会展示依据来源。</p>
            </div>
          </article>
          <article v-if="currentRole === 'student'" class="preview-card wide">
            <span>最近答疑影响</span>
            <div class="suggestion-list">
              <p v-for="item in answerImpacts" :key="item.id">
                <strong>{{ item.metadata?.weak_point_impact || '答疑影响' }}</strong>：{{ item.metadata?.path_suggestion || item.description }}；推荐资源 {{ item.metadata?.recommended_resource || '分层练习题' }}
              </p>
              <p v-if="!answerImpacts.length" class="muted">暂无最近答疑影响，当前区域使用 demo/fallback 说明：答疑记录会影响薄弱点、资源推荐和路径建议。</p>
            </div>
          </article>
          <article class="preview-card wide">
            <span>重新生成原因</span>
            <p>{{ selectedReport.summary?.regenerate_reason || '当测评、问答或知识库资料更新后可模拟重新生成。' }}</p>
          </article>
          <article class="preview-card wide">
            <span>报告文件</span>
            <p>{{ selectedReport.report_path || '暂无文件路径。' }}</p>
          </article>
        </div>

        <p v-else-if="!loading" class="empty-state">暂无报告可预览。可先在 AgentWorkflow 页面运行完整学习流生成报告。</p>
      </section>
    </div>
  </section>
</template>

<style scoped>
.report-page {
  gap: 18px;
}

.report-hero,
.panel-title,
.report-layout {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.report-hero {
  align-items: center;
}

.report-hero h2 {
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

.hero-action {
  width: 320px;
  border: 1px solid #d9e0ea;
  border-radius: 8px;
  padding: 14px;
  background: #f8fbff;
}

.hero-action span,
.overview-card small,
.preview-card span {
  display: block;
  color: #66758a;
}

.hero-action strong {
  display: block;
  margin-top: 6px;
  line-height: 1.4;
}

.overview-grid,
.filter-grid,
.preview-grid {
  display: grid;
  gap: 12px;
}

.overview-grid {
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
}

.overview-card {
  min-height: 112px;
}

.filter-grid {
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  align-items: end;
}

.report-layout {
  align-items: flex-start;
}

.report-layout > .panel:first-child {
  flex: 1.05;
}

.preview-panel {
  flex: 1;
}

.report-list,
.path-list,
.suggestion-list,
.conclusion-list,
.evidence-list {
  display: grid;
  gap: 10px;
}

.report-card,
.preview-card {
  border: 1px solid #e4e9f1;
  border-radius: 8px;
  padding: 12px;
  background: #fbfcff;
}

.report-card {
  display: grid;
  gap: 12px;
}

.report-card.active {
  border-color: #2264d1;
  background: #f8fbff;
}

.card-main {
  display: grid;
  gap: 6px;
  width: 100%;
  padding: 0;
  color: #1c2430;
  text-align: left;
  background: transparent;
}

.card-main span,
.card-main small,
.preview-card p,
.path-list p,
.suggestion-list p {
  margin: 0;
  color: #66758a;
  line-height: 1.55;
}

.card-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.card-actions a {
  border-radius: 6px;
  padding: 9px 14px;
  color: #2264d1;
  background: #edf4ff;
  text-decoration: none;
}

.status-pill {
  border-radius: 999px;
  padding: 5px 8px;
  font-size: 12px;
  color: #1453aa;
  background: #edf4ff;
}

.status-pill.completed,
.status-pill.success {
  color: #1f7a45;
  background: #effaf4;
}

.status-pill.generating {
  color: #955600;
  background: #fff7e8;
}

.status-pill.failed {
  color: #b42318;
  background: #fff0f0;
}

.preview-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.preview-card {
  display: grid;
  gap: 8px;
}

.evidence-card {
  border: 1px solid #e4e9f1;
  border-radius: 8px;
  padding: 10px;
  background: #fff;
}

.evidence-card p {
  margin: 6px 0 0;
}

.evidence-card small {
  color: #66758a;
}

.preview-card.wide {
  grid-column: 1 / -1;
}

.reference-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.reference-list small {
  border-radius: 999px;
  padding: 6px 9px;
  color: #1453aa;
  background: #edf4ff;
}

.empty-state {
  margin: 0;
  color: #66758a;
}

.error-text {
  color: #b42318;
}

@media (max-width: 1080px) {
  .report-layout,
  .report-hero,
  .panel-title {
    display: grid;
  }

  .hero-action {
    width: auto;
  }
}

@media (max-width: 720px) {
  .preview-grid {
    grid-template-columns: 1fr;
  }
}
</style>
