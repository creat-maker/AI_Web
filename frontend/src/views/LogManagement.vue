<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { api } from '../api/client';
import DataCard from '../components/DataCard.vue';
import PageHeader from '../components/PageHeader.vue';
import StatCard from '../components/StatCard.vue';
import StatusBadge from '../components/StatusBadge.vue';

interface LogItem {
  id: string;
  time: string;
  level: string;
  module: string;
  action: string;
  summary: string;
  status: string;
  user?: string;
  actor_name?: string;
  actor_role?: string;
  target_type?: string;
  target_id?: string;
  detail?: string;
  error_message?: string;
  source?: string;
  ip_address?: string;
}

interface LogSummary {
  today_log_count: number;
  error_log_count: number;
  agent_run_count: number;
  denied_count: number;
  audit_count: number;
  total_count: number;
}

const logs = ref<LogItem[]>([]);
const summary = ref<LogSummary | null>(null);
const error = ref('');
const loading = ref(true);
const filters = ref({ actor_role: 'all', status: 'all', action: 'all', keyword: '' });

const fallbackLogs: LogItem[] = [
  { id: 'audit-1', time: new Date().toISOString(), level: 'INFO', module: 'AuditCenter', action: 'review_approved', summary: '资源包审核通过，已发布到学生端。', status: 'success', actor_name: '管理员', actor_role: 'admin', target_type: 'resource_pack', target_id: '1', source: 'local' },
  { id: 'audit-2', time: new Date().toISOString(), level: 'WARNING', module: 'AuditCenter', action: 'task_failed_rollback', summary: '生成失败，当前仍使用上一版内容。', status: 'failed', actor_name: '系统治理', actor_role: 'admin', target_type: 'learning_report', target_id: '2', source: 'local' }
];

const actionOptions = computed(() => ['all', ...Array.from(new Set(logs.value.map((item) => item.action).filter(Boolean)))]);

function levelTone(level: string, status?: string) {
  if (status === 'denied' || status === 'failed' || level === 'ERROR') return 'danger';
  if (level === 'WARNING') return 'warning';
  if (level === 'SUCCESS' || status === 'success') return 'success';
  return 'info';
}

function roleLabel(role?: string) {
  const map: Record<string, string> = { student: '学生', teacher: '教师', admin: '管理员', guest: '访客' };
  return map[role || ''] || role || 'system';
}

async function loadLogs() {
  loading.value = true;
  error.value = '';
  try {
    const params = new URLSearchParams();
    Object.entries(filters.value).forEach(([key, value]) => {
      if (value && value !== 'all') params.set(key, value);
    });
    const query = params.toString() ? `?${params.toString()}` : '';
    const [rows, stat] = await Promise.all([
      api.get<LogItem[]>(`/api/v1/logs${query}`),
      api.get<LogSummary>('/api/v1/logs/summary')
    ]);
    logs.value = rows;
    summary.value = stat;
  } catch (err) {
    error.value = err instanceof Error ? err.message : '日志接口暂不可用，当前显示本地审计摘要。';
    logs.value = fallbackLogs;
    summary.value = { today_log_count: 2, error_log_count: 1, agent_run_count: 0, denied_count: 0, audit_count: 2, total_count: 2 };
  } finally {
    loading.value = false;
  }
}

function clearFilters() {
  filters.value = { actor_role: 'all', status: 'all', action: 'all', keyword: '' };
  loadLogs();
}

onMounted(loadLogs);
</script>

<template>
  <section class="page">
    <PageHeader title="操作审计" description="集中查看权限、AI 任务、人工复核、失败回滚和系统运行日志。">
      <template #actions>
        <button class="secondary" type="button" @click="clearFilters">清空筛选</button>
        <button :disabled="loading" type="button" @click="loadLogs">{{ loading ? '刷新中' : '刷新日志' }}</button>
      </template>
    </PageHeader>

    <p v-if="error" class="panel warning-text">{{ error }}</p>

    <div class="stat-grid">
      <StatCard label="今日日志" :value="summary?.today_log_count || 0" unit="条" icon="志" />
      <StatCard label="审计事件" :value="summary?.audit_count || 0" unit="条" icon="审" tone="purple" />
      <StatCard label="权限拒绝" :value="summary?.denied_count || 0" unit="次" icon="拒" tone="orange" />
      <StatCard label="失败事件" :value="summary?.error_log_count || 0" unit="条" icon="错" tone="red" />
    </div>

    <DataCard title="日志筛选" subtitle="按角色、状态、操作类型和关键词定位事件">
      <div class="filter-row log-filter">
        <select v-model="filters.actor_role" @change="loadLogs">
          <option value="all">全部角色</option>
          <option value="student">学生</option>
          <option value="teacher">教师</option>
          <option value="admin">管理员</option>
          <option value="guest">访客</option>
        </select>
        <select v-model="filters.status" @change="loadLogs">
          <option value="all">全部状态</option>
          <option value="success">success</option>
          <option value="failed">failed</option>
          <option value="denied">denied</option>
        </select>
        <select v-model="filters.action" @change="loadLogs">
          <option v-for="item in actionOptions" :key="item" :value="item">{{ item === 'all' ? '全部操作' : item }}</option>
        </select>
        <input v-model="filters.keyword" placeholder="搜索详情、对象、用户..." @keyup.enter="loadLogs" />
      </div>
    </DataCard>

    <DataCard title="审计日志列表" subtitle="展示时间、操作者、角色、操作、对象、状态、详情和失败原因">
      <div class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>时间</th>
              <th>操作者</th>
              <th>角色</th>
              <th>操作类型</th>
              <th>操作对象</th>
              <th>状态</th>
              <th>详情</th>
              <th>失败原因</th>
              <th>来源</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in logs" :key="item.id">
              <td>{{ item.time }}</td>
              <td>{{ item.actor_name || item.user || 'system' }}</td>
              <td>{{ roleLabel(item.actor_role) }}</td>
              <td><strong>{{ item.action }}</strong><p>{{ item.module }}</p></td>
              <td>{{ item.target_type || item.module }}<p>{{ item.target_id || '-' }}</p></td>
              <td><StatusBadge :label="item.status || item.level" :tone="levelTone(item.level, item.status)" /></td>
              <td>{{ item.detail || item.summary }}</td>
              <td>{{ item.error_message || (item.status === 'failed' ? item.summary : '-') }}</td>
              <td>{{ item.ip_address || item.source || 'local' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </DataCard>
  </section>
</template>

<style scoped>
.log-filter {
  grid-template-columns: 150px 150px 220px minmax(240px, 1fr);
}

.table-wrap {
  overflow-x: auto;
}

td p {
  margin: 5px 0 0;
  color: var(--text-muted);
  font-size: 12px;
}

@media (max-width: 900px) {
  .log-filter {
    grid-template-columns: 1fr;
  }
}
</style>
