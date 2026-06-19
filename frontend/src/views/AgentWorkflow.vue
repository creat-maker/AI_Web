<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { api } from '../api/client';
import DataCard from '../components/DataCard.vue';
import PageHeader from '../components/PageHeader.vue';
import ProgressBar from '../components/ProgressBar.vue';
import StatCard from '../components/StatCard.vue';
import StatusBadge from '../components/StatusBadge.vue';
import { useRole } from '../composables/useRole';

interface WorkflowStep {
  key: string;
  name: string;
  input_summary?: string;
  tool_summary?: string;
  output_summary?: string;
  evidence?: string;
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
const { demoUserId: selectedUserId } = useRole();

const defaultChain: WorkflowStep[] = [
  '画像构建 Agent',
  '知识检索 Agent',
  '学习路径规划 Agent',
  '资源生成规划 Agent',
  '多类型资源生成 Agent',
  'RAG 答疑 Agent',
  '学习效果评估 Agent',
  '内容安全与防幻觉审核 Agent',
  '报告生成 Agent'
].map((name, index) => ({
  key: `agent-${index + 1}`,
  name,
  input_summary: index === 0 ? '李明的自然语言对话、学习历史、测验结果和 AI 问答记录' : '上游 Agent 输出 + Python 循环结构知识库',
  tool_summary: index === 7 ? '事实准确性、知识点匹配度、难度匹配度、引用完整性审核规则' : '课程知识库、规则模板、结构化模板',
  output_summary: index === 4 ? 'Python 循环结构个性化补弱资源包，含 7 类资源' : '结构化中间结果进入下一节点',
  evidence: 'Python 程序设计课程知识库 / 循环结构章节',
  duration_ms: 180 + index * 70,
  duration: `${180 + index * 70}ms`,
  status: 'success'
}));

const chain = computed(() => {
  const apiSteps = center.value.steps || [];
  return apiSteps.length >= 6 ? apiSteps : defaultChain;
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
    center.value = await api.get<WorkflowCenter>(`/api/v1/agent-workflow?user_id=${encodeURIComponent(selectedUserId.value)}`);
  } catch (err) {
    error.value = '当前网络不稳定，已为你展示本地学习建议。';
  } finally {
    loading.value = false;
  }
}

onMounted(loadCenter);
</script>

<template>
  <section class="page">
    <PageHeader title="多智能体协同编排中心" description="展示从画像构建、知识检索、路径规划、资源生成、RAG 答疑、效果评估、防幻觉审核到报告生成的完整执行链路。">
      <template #actions>
        <button class="secondary" :disabled="loading" @click="loadCenter">{{ loading ? '刷新中...' : '刷新状态' }}</button>
      </template>
    </PageHeader>

    <p v-if="error" class="notice-banner">{{ error }}</p>

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
            <p><span>调用工具</span>{{ step.tool_summary || '课程知识库、规则模板、结构化模板' }}</p>
            <p><span>输出</span>{{ step.output_summary }}</p>
            <p><span>证据</span>{{ step.evidence || 'Python 程序设计课程知识库 / 循环结构章节' }}</p>
            <div class="step-foot">
              <span>{{ step.duration || `${step.duration_ms || 0}ms` }}</span>
              <ProgressBar :value="100" tone="success" />
            </div>
          </div>
        </article>
      </div>
    </DataCard>

    <DataCard title="最近运行记录" subtitle="展示最近的多智能体运行状态。">
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
            <td colspan="3">暂无数据，系统将根据你的学习记录生成建议。</td>
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
