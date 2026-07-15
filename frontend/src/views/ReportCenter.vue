<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { api, apiBase } from '../api/client';
import DataCard from '../components/DataCard.vue';
import EmptyState from '../components/EmptyState.vue';
import PageHeader from '../components/PageHeader.vue';
import ReportPreviewModal from '../components/ReportPreviewModal.vue';
import StatusBadge from '../components/StatusBadge.vue';

interface ReportRow {
  id: number;
  report_title: string;
  student_name: string;
  course_title: string;
  report_type: string;
  status: string;
  quality_score?: number | null;
  created_at: string;
  summary: any;
  download_enabled: boolean;
  student_profile_id: number;
  course_id: number;
}

const reports = ref<ReportRow[]>([]);
const loading = ref(false);
const error = ref('');
const success = ref('');
const keyword = ref('');
const typeFilter = ref('全部类型');
const selected = ref<ReportRow | null>(null);
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
      report.summary?.report_abstract,
      (report.summary?.weak_points || []).join(' ')
    ]
      .join(' ')
      .toLowerCase();
    const matchWord = !word || haystack.includes(word);
    const matchType = typeFilter.value === '全部类型' || report.report_type === typeFilter.value;
    return matchWord && matchType;
  });
});

const stats = computed(() => [
  { label: '报告总数', value: reports.value.length },
  { label: '已完成', value: reports.value.filter((item) => item.status === 'completed').length },
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
    reports.value = await api.get<ReportRow[]>('/api/v1/reports');
  } catch (err) {
    error.value = err instanceof Error ? err.message : '报告列表加载失败。';
  } finally {
    loading.value = false;
  }
}

function openPreview(report: ReportRow) {
  selected.value = report;
  previewVisible.value = true;
}

function download(report: ReportRow) {
  if (!report.download_enabled) {
    error.value = '报告文件暂不可下载，请先重新生成。';
    return;
  }
  window.open(`${apiBase}/api/v1/reports/${report.id}/download`, '_blank');
}

async function regenerate(report?: ReportRow) {
  const target = report || reports.value[0];
  if (!target) {
    error.value = '暂无可重新生成的报告。';
    return;
  }
  success.value = '';
  error.value = '';
  try {
    const row = await api.post<ReportRow>('/api/v1/reports/generate', {
      student_profile_id: target.student_profile_id,
      course_id: target.course_id,
      regenerate_reason: '教师在报告中心触发重新生成。'
    });
    success.value = '报告已重新生成。';
    selected.value = row;
    await loadReports();
  } catch (err) {
    error.value = err instanceof Error ? err.message : '重新生成失败。';
  }
}

function clearSearch() {
  keyword.value = '';
  typeFilter.value = '全部类型';
}

onMounted(loadReports);
</script>

<template>
  <section class="page report-page">
    <PageHeader title="报告中心" description="查看、预览、导出和重新生成学习诊断报告。">
      <template #actions>
        <button class="secondary" type="button" @click="clearSearch">清空搜索</button>
        <button type="button" @click="regenerate()">重新生成</button>
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

    <DataCard title="搜索报告" subtitle="按学生、课程、章节、报告类型和关键词过滤">
      <div class="filter-grid">
        <input v-model="keyword" placeholder="搜索学生、课程、报告或知识点，例如：循环" @keyup.enter.prevent />
        <select v-model="typeFilter">
          <option v-for="item in typeOptions" :key="item">{{ item }}</option>
        </select>
      </div>
    </DataCard>

    <DataCard title="报告列表" :subtitle="`${filteredReports.length} 份报告`">
      <div v-if="filteredReports.length" class="report-list">
        <article v-for="report in filteredReports" :key="report.id" class="report-row">
          <div>
            <strong>{{ report.report_title }}</strong>
            <p>{{ report.course_title }} / {{ report.student_name }} / {{ report.report_type }}</p>
            <small>{{ report.created_at }} / 质量评分 {{ report.quality_score ?? '-' }}</small>
          </div>
          <StatusBadge :label="report.status === 'completed' ? '已完成' : '生成中'" :tone="report.status === 'completed' ? 'success' : 'warning'" />
          <div class="row-actions">
            <button class="ghost" type="button" @click="openPreview(report)">查看预览</button>
            <button class="ghost" type="button" @click="download(report)">导出报告</button>
            <button class="ghost" type="button" @click="regenerate(report)">重新生成</button>
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
  grid-template-columns: minmax(260px, 1fr) 180px;
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

@media (max-width: 980px) {
  .stat-grid,
  .filter-grid,
  .report-row {
    grid-template-columns: 1fr;
  }
}
</style>
