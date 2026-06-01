<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { api } from '../api/client';
import DataCard from '../components/DataCard.vue';
import PageHeader from '../components/PageHeader.vue';
import ProgressBar from '../components/ProgressBar.vue';
import StatCard from '../components/StatCard.vue';
import StatusBadge from '../components/StatusBadge.vue';

interface WorkflowRecord {
  id: number;
  workflow_name: string;
  task_name?: string;
  status: string;
  created_at?: string;
  trigger_source?: string;
}

interface WorkflowCenter {
  records?: WorkflowRecord[];
  workflow_summary?: {
    today_run_count: number;
    success_rate: number;
    average_duration: string;
    artifact_count: number;
  };
}

const center = ref<WorkflowCenter>({});
const error = ref('');
const loading = ref(true);

const workflows = [
  { name: '学习路径推荐', status: '运行中', lastRun: '10 分钟前', success: 96, trigger: '学生画像更新' },
  { name: '资源生成', status: '正常', lastRun: '18 分钟前', success: 94, trigger: '教师手动触发' },
  { name: '报告生成', status: '正常', lastRun: '32 分钟前', success: 98, trigger: '定时任务' },
  { name: '知识点诊断', status: '待配置', lastRun: '1 小时前', success: 89, trigger: '测验提交' },
  { name: '智能答疑', status: '正常', lastRun: '刚刚', success: 97, trigger: '学生提问' }
];

const records = [
  { name: '学习路径推荐', run: 'run-20240531-1020', status: '成功', time: '05-31 10:20', duration: '16s' },
  { name: '资源生成', run: 'run-20240531-1012', status: '运行中', time: '05-31 10:12', duration: '32s' },
  { name: '报告生成', run: 'run-20240530-2040', status: '失败', time: '05-30 20:40', duration: '9s' },
  { name: '知识点诊断', run: 'run-20240530-1810', status: '成功', time: '05-30 18:10', duration: '12s' }
];

const nodes = ['任务触发', '数据采集', '知识检索', 'Agent 编排', '结果审核', '业务写回'];

function statusTone(status: string) {
  if (status === '正常' || status === '成功') return 'success';
  if (status === '运行中') return 'purple';
  if (status === '失败') return 'danger';
  return 'warning';
}

async function loadCenter() {
  loading.value = true;
  error.value = '';
  try {
    center.value = await api.get<WorkflowCenter>('/api/v1/agent-workflow');
  } catch (err) {
    error.value = err instanceof Error ? err.message : '工作流接口暂不可用，当前显示演示数据。';
  } finally {
    loading.value = false;
  }
}

onMounted(loadCenter);
</script>

<template>
  <section class="page">
    <PageHeader title="Agent 工作流" description="管理学习路径推荐、资源生成、报告生成、知识点诊断和智能答疑工作流。">
      <template #actions>
        <button>新建工作流</button>
        <button class="secondary" :disabled="loading" @click="loadCenter">{{ loading ? '刷新中' : '刷新状态' }}</button>
      </template>
    </PageHeader>

    <p v-if="error" class="demo-banner">{{ error }}</p>

    <div class="stat-grid">
      <StatCard label="总工作流" value="12" unit="条" icon="流" />
      <StatCard label="运行中" value="3" unit="条" icon="行" tone="purple" />
      <StatCard label="成功次数" :value="center.workflow_summary?.today_run_count || 186" unit="次" icon="成" tone="green" />
      <StatCard label="失败次数" value="7" unit="次" icon="错" tone="red" />
      <StatCard label="平均耗时" :value="center.workflow_summary?.average_duration || '18s'" icon="耗" tone="orange" />
    </div>

    <div class="workflow-card-grid">
      <DataCard v-for="item in workflows" :key="item.name">
        <div class="workflow-card">
          <div class="workflow-title">
            <strong>{{ item.name }}</strong>
            <StatusBadge :label="item.status" :tone="statusTone(item.status)" />
          </div>
          <p>最近运行：{{ item.lastRun }} · 触发方式：{{ item.trigger }}</p>
          <div class="metric-line">
            <span>成功率 {{ item.success }}%</span>
            <ProgressBar :value="item.success" :tone="item.success > 95 ? 'success' : 'primary'" />
          </div>
          <div class="row-actions">
            <button class="ghost">运行</button>
            <button class="ghost">暂停</button>
            <button class="ghost">日志</button>
            <button class="ghost">配置</button>
          </div>
        </div>
      </DataCard>
    </div>

    <div class="content-with-aside">
      <DataCard title="工作流节点可视化" subtitle="平台任务从触发到业务写回的治理链路">
        <div class="node-flow">
          <template v-for="(node, index) in nodes" :key="node">
            <div class="node-card">{{ node }}</div>
            <span v-if="index < nodes.length - 1" class="arrow">→</span>
          </template>
        </div>
      </DataCard>

      <DataCard title="执行健康度" subtitle="成功率、失败重试和审核队列">
        <div class="list">
          <div class="item compact"><strong>成功率</strong><StatusBadge label="96.8%" tone="success" /></div>
          <div class="item compact"><strong>失败重试</strong><StatusBadge label="2 次" tone="warning" /></div>
          <div class="item compact"><strong>待人工审核</strong><StatusBadge label="8 条" tone="purple" /></div>
        </div>
      </DataCard>
    </div>

    <DataCard title="最近执行记录" subtitle="运行状态、耗时与操作">
      <table class="table">
        <thead>
          <tr>
            <th>工作流</th>
            <th>Run ID</th>
            <th>状态</th>
            <th>执行时间</th>
            <th>耗时</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in records" :key="row.run">
            <td><strong>{{ row.name }}</strong></td>
            <td>{{ row.run }}</td>
            <td><StatusBadge :label="row.status" :tone="statusTone(row.status)" /></td>
            <td>{{ row.time }}</td>
            <td>{{ row.duration }}</td>
            <td>
              <div class="row-actions">
                <button class="ghost">查看日志</button>
                <button class="ghost">重跑</button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </DataCard>
  </section>
</template>

<style scoped>
.workflow-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 14px;
}

.workflow-card,
.metric-line {
  display: grid;
  gap: 10px;
}

.workflow-title,
.row-actions {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  align-items: center;
}

.workflow-card p {
  min-height: 44px;
  margin: 0;
  line-height: 1.6;
}

.row-actions {
  justify-content: flex-start;
  flex-wrap: wrap;
}

.node-flow {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
}

.node-card {
  border: 1px solid #dbe7ff;
  border-radius: 16px;
  padding: 14px 16px;
  color: var(--color-primary-dark);
  background: var(--color-primary-light);
  font-weight: 800;
}

.arrow {
  color: var(--color-primary);
  font-weight: 900;
}
</style>
