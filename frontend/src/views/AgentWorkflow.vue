<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { api } from '../api/client';
import DataCard from '../components/DataCard.vue';
import PageHeader from '../components/PageHeader.vue';
import ProgressBar from '../components/ProgressBar.vue';
import StatCard from '../components/StatCard.vue';
import StatusBadge from '../components/StatusBadge.vue';

interface WorkflowStep {
  key: string;
  name: string;
  input_summary?: string;
  output_summary?: string;
  duration_ms?: number;
  duration?: string;
  status: string;
}

interface WorkflowCenter {
  records?: Array<{ id: number; workflow_name: string; status: string; created_at?: string }>;
  steps?: WorkflowStep[];
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

const demoChain: WorkflowStep[] = [
  {
    key: 'profile',
    name: '画像构建',
    input_summary: '学生自然语言回答、课程、薄弱点、时间安排',
    output_summary: '生成学习目标、基础水平、薄弱知识点、偏好、风险和策略',
    duration_ms: 220,
    duration: '220ms',
    status: 'success'
  },
  {
    key: 'rag',
    name: '知识检索',
    input_summary: '学生问题、courseId、studentId',
    output_summary: '命中课程知识库片段、引用来源、可信度和推荐练习',
    duration_ms: 180,
    duration: '180ms',
    status: 'success'
  },
  {
    key: 'path',
    name: '路径规划',
    input_summary: '画像维度、薄弱点、课程章节',
    output_summary: '生成阶段目标、学习顺序和任务安排',
    duration_ms: 260,
    duration: '260ms',
    status: 'success'
  },
  {
    key: 'resource',
    name: '资源生成',
    input_summary: 'studentId、courseId、weakPoints',
    output_summary: '生成讲义、练习题、实验任务、思维导图、视频脚本/任务书',
    duration_ms: 340,
    duration: '340ms',
    status: 'success'
  },
  {
    key: 'review',
    name: '内容审核',
    input_summary: '生成内容、引用来源、课程 ID',
    output_summary: '输出风险等级、引用覆盖、防幻觉告警和修改建议',
    duration_ms: 160,
    duration: '160ms',
    status: 'success'
  },
  {
    key: 'report',
    name: '学习报告',
    input_summary: '画像、RAG 引用、资源包、审核结果、学习任务',
    output_summary: '汇总阶段学习报告和下一步建议',
    duration_ms: 300,
    duration: '300ms',
    status: 'success'
  }
];

const chain = computed(() => {
  const apiSteps = center.value.steps || [];
  return apiSteps.length >= 6 ? apiSteps : demoChain;
});

function statusTone(status: string) {
  if (status === 'success' || status === '成功' || status === '正常') return 'success';
  if (status === 'running' || status === '运行中') return 'purple';
  if (status === 'failed' || status === '失败') return 'danger';
  return 'warning';
}

async function loadCenter() {
  loading.value = true;
  error.value = '';
  try {
    center.value = await api.get<WorkflowCenter>('/api/v1/agent-workflow');
  } catch (err) {
    error.value = err instanceof Error ? err.message : '工作流接口暂不可用，当前显示演示链路。';
  } finally {
    loading.value = false;
  }
}

onMounted(loadCenter);
</script>

<template>
  <section class="page">
    <PageHeader title="Agent 工作流" description="展示从画像构建、知识检索、路径规划、资源生成、内容审核到学习报告的完整执行链路。">
      <template #actions>
        <button class="secondary" :disabled="loading" @click="loadCenter">{{ loading ? '刷新中...' : '刷新状态' }}</button>
      </template>
    </PageHeader>

    <p v-if="error" class="demo-banner">{{ error }}</p>

    <div class="stat-grid">
      <StatCard label="今日运行" :value="center.workflow_summary?.today_run_count || 6" unit="次" icon="流" />
      <StatCard label="成功率" :value="center.workflow_summary?.success_rate || 100" unit="%" icon="成" tone="green" />
      <StatCard label="平均耗时" :value="center.workflow_summary?.average_duration || '1.5s'" icon="耗" tone="orange" />
      <StatCard label="产物数量" :value="center.workflow_summary?.artifact_count || 12" unit="项" icon="产" tone="purple" />
    </div>

    <DataCard title="完整执行链路" subtitle="每一步展示输入、输出、耗时和状态，适合答辩说明 Agent 如何串起学习闭环。">
      <div class="agent-chain">
        <article v-for="(step, index) in chain" :key="step.key || step.name" class="agent-step">
          <div class="step-index">{{ index + 1 }}</div>
          <div class="step-body">
            <div class="step-head">
              <strong>{{ step.name }}</strong>
              <StatusBadge :label="step.status" :tone="statusTone(step.status)" />
            </div>
            <p><span>输入</span>{{ step.input_summary }}</p>
            <p><span>输出</span>{{ step.output_summary }}</p>
            <div class="step-foot">
              <span>{{ step.duration || `${step.duration_ms || 0}ms` }}</span>
              <ProgressBar :value="100" tone="success" />
            </div>
          </div>
        </article>
      </div>
    </DataCard>

    <DataCard title="最近运行记录" subtitle="来自后端 AgentRun 与业务事件，接口不可用时仍保留演示链路。">
      <table class="table">
        <thead>
          <tr>
            <th>工作流</th>
            <th>状态</th>
            <th>时间</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in center.records || []" :key="row.id">
            <td><strong>{{ row.workflow_name }}</strong></td>
            <td><StatusBadge :label="row.status" :tone="statusTone(row.status)" /></td>
            <td>{{ row.created_at || '-' }}</td>
          </tr>
          <tr v-if="!(center.records || []).length">
            <td><strong>software-cup-demo-chain</strong></td>
            <td><StatusBadge label="success" tone="success" /></td>
            <td>demo</td>
          </tr>
        </tbody>
      </table>
    </DataCard>
  </section>
</template>

<style scoped>
.agent-chain {
  display: grid;
  gap: 14px;
}

.agent-step {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 14px;
  border: 1px solid var(--border-light);
  border-radius: 16px;
  padding: 16px;
  background: #fbfdff;
}

.step-index {
  display: inline-grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border-radius: 14px;
  color: var(--text-light);
  background: linear-gradient(135deg, var(--color-primary-dark), var(--color-purple));
  font-weight: 800;
}

.step-body,
.step-foot {
  display: grid;
  gap: 10px;
}

.step-head,
.step-foot {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.step-body p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.65;
}

.step-body p span {
  display: inline-block;
  margin-right: 8px;
  color: var(--color-primary-dark);
  font-weight: 800;
}

.step-foot > span {
  color: var(--text-muted);
  font-size: 12px;
  font-weight: 800;
}
</style>
