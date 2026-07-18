<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { api } from '../api/client';
import DataCard from '../components/DataCard.vue';
import EmptyState from '../components/EmptyState.vue';
import PageHeader from '../components/PageHeader.vue';
import ReportPreviewModal from '../components/ReportPreviewModal.vue';
import StatusBadge from '../components/StatusBadge.vue';

interface AdminReport {
  id: number;
  report_title: string;
  student_name: string;
  course_title: string;
  report_type: string;
  status: string;
  review_status: string;
  creator: string;
  quality_score?: number | null;
  created_at: string;
  summary: any;
}

const reports = ref<AdminReport[]>([]);
const loading = ref(false);
const processing = ref(false);
const error = ref('');
const success = ref('');
const keyword = ref('');
const typeFilter = ref('全部类型');
const statusFilter = ref('全部状态');
const selected = ref<AdminReport | null>(null);
const previewVisible = ref(false);

const typeOptions = computed(() => ['全部类型', ...Array.from(new Set(reports.value.map((item) => item.report_type)))]);
const filteredReports = computed(() => {
  const word = keyword.value.trim().toLowerCase();
  return reports.value.filter((report) => {
    const haystack = [
      report.report_title,
      report.student_name,
      report.course_title,
      report.report_type,
      report.status,
      report.review_status,
      report.creator,
      report.summary?.report_abstract,
      (report.summary?.weak_points || []).join(' ')
    ]
      .join(' ')
      .toLowerCase();
    const matchWord = !word || haystack.includes(word);
    const matchType = typeFilter.value === '全部类型' || report.report_type === typeFilter.value;
    const matchStatus = statusFilter.value === '全部状态' || report.review_status === statusFilter.value || report.status === statusFilter.value;
    return matchWord && matchType && matchStatus;
  });
});

const stats = computed(() => [
  { label: '报告总数', value: reports.value.length },
  { label: '待审核', value: reports.value.filter((item) => item.review_status === '待审核').length },
  { label: '当前结果', value: filteredReports.value.length },
  { label: '平均质量', value: averageQuality.value || '-' }
]);

const averageQuality = computed(() => {
  const values = reports.value.map((item) => item.quality_score).filter((item): item is number => typeof item === 'number');
  return values.length ? Math.round(values.reduce((sum, item) => sum + item, 0) / values.length) : 0;
});

async function loadReports() {
  loading.value = true;
  error.value = '';
  try {
    reports.value = await api.get<AdminReport[]>('/api/v1/admin/reports');
  } catch (err) {
    error.value = err instanceof Error ? err.message : '报告审核列表加载失败。';
  } finally {
    loading.value = false;
  }
}

function openPreview(report: AdminReport) {
  selected.value = report;
  previewVisible.value = true;
}

async function saveDownload(path: string, fallbackName: string, method = 'GET') {
  const result = await api.download(path, { method });
  const url = URL.createObjectURL(result.blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = result.filename === 'download.bin' ? fallbackName : result.filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  URL.revokeObjectURL(url);
}

async function download(report: AdminReport) {
  error.value = '';
  try {
    await saveDownload(`/api/v1/admin/reports/${report.id}/download`, `admin-report-${report.id}.docx`);
  } catch (err) {
    error.value = err instanceof Error ? err.message : '报告下载失败。';
  }
}

async function regenerate(report: AdminReport) {
  processing.value = true;
  error.value = '';
  success.value = '';
  try {
    await api.post(`/api/v1/admin/reports/${report.id}/regenerate`);
    success.value = '报告已重新生成。';
    await loadReports();
  } catch (err) {
    error.value = err instanceof Error ? err.message : '重新生成失败。';
  } finally {
    processing.value = false;
  }
}

async function updateStatus(report: AdminReport, status: string) {
  try {
    await api.patch(`/api/v1/admin/reports/${report.id}/status`, { status });
    report.review_status = status;
    success.value = '审核状态已更新。';
  } catch (err) {
    error.value = err instanceof Error ? err.message : '审核状态更新失败。';
  }
}

async function createMonthlyReport() {
  processing.value = true;
  error.value = '';
  success.value = '';
  try {
    await api.post('/api/v1/admin/reports/monthly');
    success.value = '平台运营月报已生成。';
    await loadReports();
  } catch (err) {
    error.value = err instanceof Error ? err.message : '月报生成失败。';
  } finally {
    processing.value = false;
  }
}

async function exportBatch() {
  error.value = '';
  try {
    await saveDownload('/api/v1/admin/reports/export', 'admin-reports-export.zip', 'POST');
  } catch (err) {
    error.value = err instanceof Error ? err.message : '报告批量导出失败。';
  }
}

function clearSearch() {
  keyword.value = '';
  typeFilter.value = '全部类型';
  statusFilter.value = '全部状态';
}

onMounted(loadReports);
</script>

<template>
  <section class="page admin-report-page">
    <PageHeader title="报告审核中心" description="管理学习诊断报告、平台运营报告和系统运行报告。">
      <template #actions>
        <button class="secondary" type="button" @click="exportBatch">批量导出</button>
        <button :disabled="processing" type="button" @click="createMonthlyReport">{{ processing ? '处理中...' : '生成月报' }}</button>
      </template>
    </PageHeader>

    <p v-if="error" class="panel error-text">{{ error }}</p>
    <p v-if="success" class="panel success-text">{{ success }}</p>
    <p v-if="loading" class="panel muted">正在加载报告...</p>

    <div class="stat-grid">
      <article v-for="item in stats" :key="item.label" class="stat-card">
        <span>{{ item.label }}</span>
        <strong>{{ item.value }}</strong>
      </article>
    </div>

    <DataCard title="搜索报告" subtitle="按学生、课程、章节、报告类型、状态和关键词过滤">
      <div class="filter-grid">
        <input v-model="keyword" placeholder="搜索报告，例如：循环、平台运营、系统运行" @keyup.enter.prevent />
        <select v-model="typeFilter">
          <option v-for="item in typeOptions" :key="item">{{ item }}</option>
        </select>
        <select v-model="statusFilter">
          <option>全部状态</option>
          <option>待审核</option>
          <option>已通过</option>
          <option>completed</option>
          <option>generating</option>
        </select>
        <button class="secondary" type="button" @click="clearSearch">清空</button>
      </div>
    </DataCard>

    <DataCard title="报告列表" :subtitle="`${filteredReports.length} 份报告`">
      <div v-if="filteredReports.length" class="report-list">
        <article v-for="report in filteredReports" :key="report.id" class="report-row">
          <div>
            <strong>{{ report.report_title }}</strong>
            <p>{{ report.course_title }} / {{ report.student_name }} / {{ report.report_type }}</p>
            <small>{{ report.creator }} / {{ report.created_at }}</small>
          </div>
          <StatusBadge :label="report.review_status" :tone="report.review_status === '已通过' ? 'success' : 'warning'" />
          <div class="row-actions">
            <button class="ghost" type="button" @click="openPreview(report)">查看预览</button>
            <button class="ghost" type="button" @click="download(report)">导出报告</button>
            <button class="ghost" type="button" @click="regenerate(report)">重新生成</button>
            <button class="ghost" type="button" @click="updateStatus(report, '已通过')">通过</button>
          </div>
        </article>
      </div>
      <EmptyState v-else title="未找到相关报告" description="请更换关键词，或清空搜索后查看全部报告。" />
    </DataCard>

    <ReportPreviewModal :visible="previewVisible" :report="selected" @close="previewVisible = false" @download="download" />
  </section>
</template>

<style scoped>
.stat-grid,
.filter-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.filter-grid {
  grid-template-columns: minmax(260px, 1fr) 170px 150px 110px;
}

.stat-card,
.report-row {
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

.report-list {
  display: grid;
  gap: 12px;
}

.report-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto auto;
  gap: 14px;
  align-items: center;
}

.report-row p {
  margin: 6px 0;
  color: var(--text-secondary);
}

.row-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.error-text {
  color: #b91c1c;
}

.success-text {
  color: #047857;
}

@media (max-width: 1100px) {
  .stat-grid,
  .filter-grid,
  .report-row {
    grid-template-columns: 1fr;
  }
}
</style>
