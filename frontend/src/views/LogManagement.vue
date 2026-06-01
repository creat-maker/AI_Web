<script setup lang="ts">
import { onMounted, ref } from 'vue';
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
  user?: string;
  source?: string;
}

const logs = ref<LogItem[]>([]);
const error = ref('');
const loading = ref(true);

const fallbackLogs: LogItem[] = [
  { id: 'log-1', time: '05-31 10:25:18', level: 'WARNING', module: 'AI 服务', action: '调用延迟', summary: '模型服务平均响应超过 2 秒，已进入观察队列。', user: 'system', source: '10.0.0.8' },
  { id: 'log-2', time: '05-31 10:12:06', level: 'ERROR', module: '资源生成', action: '任务失败', summary: 'Web 前端课件提纲生成失败，原因：引用资源缺失。', user: 'Admin', source: '10.0.0.12' },
  { id: 'log-3', time: '05-31 09:48:30', level: 'INFO', module: '用户权限', action: '角色分配', summary: '已为李助教分配 Python 课程组助教权限。', user: '赵管理员', source: '10.0.0.21' },
  { id: 'log-4', time: '05-31 09:20:11', level: 'SUCCESS', module: 'Agent 工作流', action: '运行完成', summary: '学习路径推荐工作流运行成功，写回 3 个推荐节点。', user: 'system', source: '10.0.0.8' }
];

const alerts = [
  { title: 'AI 服务响应延迟较高', level: '警告', module: 'AI 服务', time: '5 分钟前' },
  { title: '资源生成失败率升高', level: '错误', module: '资源生成', time: '18 分钟前' },
  { title: '知识库解析队列积压', level: '警告', module: '知识库', time: '32 分钟前' }
];

function levelTone(level: string) {
  if (level === 'ERROR' || level === '错误') return 'danger';
  if (level === 'WARNING' || level === '警告') return 'warning';
  if (level === 'SUCCESS') return 'success';
  return 'info';
}

async function loadLogs() {
  loading.value = true;
  error.value = '';
  try {
    logs.value = await api.get<LogItem[]>('/api/v1/logs');
  } catch (err) {
    error.value = err instanceof Error ? err.message : '日志接口暂不可用，当前显示演示日志。';
    logs.value = fallbackLogs;
  } finally {
    loading.value = false;
  }
}

onMounted(loadLogs);
</script>

<template>
  <section class="page">
    <PageHeader title="日志管理" description="集中查看系统日志、AI 调用、接口异常和平台告警。">
      <template #actions>
        <button>导出日志</button>
        <button class="secondary" :disabled="loading" @click="loadLogs">{{ loading ? '刷新中' : '刷新日志' }}</button>
      </template>
    </PageHeader>

    <p v-if="error" class="demo-banner">{{ error }}</p>

    <div class="stat-grid">
      <StatCard label="今日日志" value="1,286" unit="条" icon="志" />
      <StatCard label="警告数" value="36" unit="条" icon="警" tone="orange" />
      <StatCard label="错误数" value="8" unit="条" icon="错" tone="red" />
      <StatCard label="AI 调用次数" value="18,620" unit="次" icon="AI" tone="purple" />
      <StatCard label="接口异常" value="5" unit="次" icon="异" tone="cyan" />
    </div>

    <DataCard title="日志筛选" subtitle="按级别、模块和时间范围定位问题">
      <div class="filter-row log-filter">
        <select><option>全部级别</option><option>INFO</option><option>WARNING</option><option>ERROR</option><option>SUCCESS</option></select>
        <select><option>全部模块</option><option>AI 服务</option><option>资源生成</option><option>Agent 工作流</option><option>用户权限</option></select>
        <input type="date" />
        <input placeholder="搜索内容、用户、IP..." />
      </div>
    </DataCard>

    <div class="content-with-aside">
      <DataCard title="日志列表" subtitle="时间、级别、模块、用户、内容和 IP">
        <table class="table">
          <thead>
            <tr>
              <th>时间</th>
              <th>级别</th>
              <th>模块</th>
              <th>用户</th>
              <th>内容</th>
              <th>IP</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in logs" :key="item.id">
              <td>{{ item.time }}</td>
              <td><StatusBadge :label="item.level" :tone="levelTone(item.level)" /></td>
              <td><strong>{{ item.module }}</strong></td>
              <td>{{ item.user || 'system' }}</td>
              <td>{{ item.summary || item.action }}</td>
              <td>{{ item.source || '10.0.0.8' }}</td>
              <td>
                <div class="row-actions">
                  <button class="ghost">详情</button>
                  <button class="ghost">已处理</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </DataCard>

      <DataCard title="系统告警" subtitle="需要管理员关注的风险事件">
        <div class="list">
          <article v-for="item in alerts" :key="item.title" class="alert-row">
            <div>
              <strong>{{ item.title }}</strong>
              <p>{{ item.module }} · {{ item.time }}</p>
            </div>
            <StatusBadge :label="item.level" :tone="levelTone(item.level)" />
          </article>
        </div>
      </DataCard>
    </div>
  </section>
</template>

<style scoped>
.log-filter {
  grid-template-columns: 160px 180px 180px minmax(240px, 1fr);
}

.row-actions,
.alert-row {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  align-items: center;
}

.row-actions {
  justify-content: flex-start;
  flex-wrap: wrap;
}

.alert-row {
  border: 1px solid var(--color-border);
  border-radius: 14px;
  padding: 12px;
  background: #fbfdff;
}

.alert-row p {
  margin: 4px 0 0;
}

@media (max-width: 900px) {
  .log-filter {
    grid-template-columns: 1fr;
  }
}
</style>
