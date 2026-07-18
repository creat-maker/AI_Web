<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import { api } from '../api/client';
import DataCard from '../components/DataCard.vue';
import PageHeader from '../components/PageHeader.vue';
import StatusBadge from '../components/StatusBadge.vue';

interface ArbitrationTask {
  id: string;
  agent_run_id?: number;
  arbitration_item_id: string;
  student_name: string;
  course: string;
  topic: string;
  risk_level: 'low' | 'medium' | 'high' | string;
  trigger_reason: string;
  original_content: string;
  suggested_content: string;
  review_result: string;
  retry_count: number;
  rag_citations: string[];
  profile_risk_evidence: string[];
  recommended_action: 'approve' | 'revise' | 'reject' | string;
  teacher_comment?: string;
  status: string;
}

const tasks = ref<ArbitrationTask[]>([]);
const loading = ref(false);
const message = ref('');
const comments = reactive<Record<string, string>>({});
const revisedContent = reactive<Record<string, string>>({});
const suggestedActions = reactive<Record<string, string>>({});
const submitting = reactive<Record<string, boolean>>({});
const decisionRequestIds = reactive<Record<string, string>>({});
const decisionInFlight = ref(false);
const pageFrozen = ref(false);

function decisionRequestKey(task: ArbitrationTask, decision: 'approve' | 'revise' | 'reject') {
  return `${task.id}:${task.arbitration_item_id}:${decision}`;
}

function newDecisionRequestId() {
  if (typeof crypto.randomUUID === 'function') return crypto.randomUUID();
  return `decision-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function clearTaskState(taskId: string, arbitrationItemId: string) {
  delete comments[taskId];
  delete revisedContent[taskId];
  delete suggestedActions[taskId];
  Object.keys(decisionRequestIds)
    .filter((key) => key.startsWith(`${taskId}:${arbitrationItemId}:`))
    .forEach((key) => delete decisionRequestIds[key]);
}

function riskTone(risk: string) {
  if (risk === 'high') return 'danger';
  if (risk === 'medium') return 'warning';
  return 'success';
}

function statusTone(status: string) {
  if (['approved', 'passed', 'success'].includes(status)) return 'success';
  if (['rejected', 'blocked'].includes(status)) return 'danger';
  if (['revised', 'needs_review'].includes(status)) return 'warning';
  return 'info';
}

async function load() {
  loading.value = true;
  message.value = '正在刷新教师仲裁队列...';
  tasks.value = [];
  Object.keys(comments).forEach((key) => delete comments[key]);
  Object.keys(revisedContent).forEach((key) => delete revisedContent[key]);
  Object.keys(suggestedActions).forEach((key) => delete suggestedActions[key]);
  Object.keys(submitting).forEach((key) => delete submitting[key]);
  Object.keys(decisionRequestIds).forEach((key) => delete decisionRequestIds[key]);
  try {
    const result = await api.get<ArbitrationTask[]>('/api/v1/teacher-arbitrations');
    tasks.value = result;
    message.value = result.length ? '教师仲裁队列已刷新。' : '当前授权课程暂无待仲裁任务。';
    return true;
  } catch (err) {
    tasks.value = [];
    message.value = err instanceof Error ? `教师仲裁队列加载失败：${err.message}` : '教师仲裁队列加载失败。';
    return false;
  } finally {
    loading.value = false;
  }
}

async function refreshQueue() {
  if (decisionInFlight.value || loading.value) return;
  const loaded = await load();
  if (loaded) pageFrozen.value = false;
}

async function decide(task: ArbitrationTask, decision: 'approve' | 'revise' | 'reject') {
  if (decisionInFlight.value || pageFrozen.value) return;
  decisionInFlight.value = true;
  submitting[task.id] = true;
  const requestKey = decisionRequestKey(task, decision);
  const decisionRequestId = decisionRequestIds[requestKey] || newDecisionRequestId();
  decisionRequestIds[requestKey] = decisionRequestId;
  const teacherComment = comments[task.id] || (
    decision === 'approve' ? '内容可发布，保留引用证据。' :
    decision === 'revise' ? '请按教师意见修改后重新生成。' :
    '超出课程范围，拒绝发布。'
  );
  const target = Object.freeze({
    taskId: task.id,
    agentRunId: task.agent_run_id || task.id,
    arbitrationItemId: task.arbitration_item_id,
    decision,
    decisionRequestId,
    teacherComment,
    revisedContent: decision === 'revise' ? (revisedContent[task.id] || task.suggested_content) : undefined,
    suggestedAction: suggestedActions[task.id] || task.recommended_action
  });
  try {
    const result = await api.post<{ status: string; message?: string }>(`/api/v1/teacher-arbitration/${target.agentRunId}/decision`, {
      decision: target.decision,
      arbitration_item_id: target.arbitrationItemId,
      decision_request_id: target.decisionRequestId,
      teacher_comment: target.teacherComment,
      comment: target.teacherComment,
      revised_content: target.revisedContent,
      suggested_action: target.suggestedAction
    });
    pageFrozen.value = true;
    const taskIndex = tasks.value.findIndex(
      (item) => item.id === target.taskId && item.arbitration_item_id === target.arbitrationItemId
    );
    if (taskIndex >= 0) tasks.value.splice(taskIndex, 1);
    clearTaskState(target.taskId, target.arbitrationItemId);
    message.value = `${result.message || '教师仲裁结果已提交。'} 本次操作已完成，请手动刷新后继续。`;
  } catch (err) {
    message.value = err instanceof Error ? err.message : '教师仲裁提交失败。';
  } finally {
    submitting[target.taskId] = false;
    decisionInFlight.value = false;
  }
}

onMounted(load);
</script>

<template>
  <section class="page decision-center-page">
    <PageHeader title="教师仲裁中心" description="复核高风险或多次审核未通过的路径、资源与报告，形成 approve / revise / reject 闭环。">
      <template #actions>
        <button type="button" class="secondary" :disabled="loading || decisionInFlight" @click="refreshQueue">{{ loading ? '刷新中...' : '刷新' }}</button>
      </template>
    </PageHeader>

    <p v-if="message" class="panel muted">{{ message }}</p>

    <div class="arbitration-list">
      <DataCard v-for="task in tasks" :key="`${task.id}:${task.arbitration_item_id}`" :title="`${task.student_name} · ${task.topic}`" :subtitle="`${task.course} · retry ${task.retry_count}`">
        <div class="task-head">
          <StatusBadge :label="`风险：${task.risk_level}`" :tone="riskTone(task.risk_level)" />
          <StatusBadge :label="`状态：${task.status}`" :tone="statusTone(task.status)" />
          <StatusBadge :label="`建议：${task.recommended_action}`" tone="info" />
        </div>

        <div class="task-grid">
          <section>
            <strong>触发原因</strong>
            <p>{{ task.trigger_reason }}</p>
          </section>
          <section>
            <strong>原始资源 / 建议内容</strong>
            <p>{{ task.original_content }}</p>
            <p>{{ task.suggested_content }}</p>
          </section>
          <section>
            <strong>审核结果</strong>
            <p>{{ task.review_result }}</p>
          </section>
          <section>
            <strong>RAG 引用证据</strong>
            <p>{{ task.rag_citations.length ? task.rag_citations.join('、') : '暂无引用，需教师复核。' }}</p>
          </section>
          <section>
            <strong>画像风险证据</strong>
            <p>{{ task.profile_risk_evidence.length ? task.profile_risk_evidence.join('、') : '暂无画像风险。' }}</p>
          </section>
        </div>

        <div class="decision-form">
          <label>
            teacher_comment
            <textarea v-model="comments[task.id]" placeholder="填写教师仲裁意见" />
          </label>
          <label>
            revised_content
            <textarea v-model="revisedContent[task.id]" placeholder="revise 时填写修改后的内容或生成要求" />
          </label>
          <label>
            suggested_action
            <input v-model="suggestedActions[task.id]" :placeholder="task.recommended_action" />
          </label>
        </div>

        <div class="action-row">
          <button type="button" :disabled="decisionInFlight || pageFrozen || submitting[task.id] || task.status !== 'pending'" @click.stop.prevent="decide(task, 'approve')">通过</button>
          <button type="button" class="secondary" :disabled="decisionInFlight || pageFrozen || submitting[task.id] || task.status !== 'pending'" @click.stop.prevent="decide(task, 'revise')">修改</button>
          <button type="button" class="danger" :disabled="decisionInFlight || pageFrozen || submitting[task.id] || task.status !== 'pending'" @click.stop.prevent="decide(task, 'reject')">拒绝</button>
        </div>
      </DataCard>
    </div>
  </section>
</template>

<style scoped>
.arbitration-list,
.task-grid,
.decision-form {
  display: grid;
  gap: 14px;
}

.task-head,
.action-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 14px;
}

.task-grid {
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

.task-grid section {
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 12px;
  background: #fff;
}

.task-grid p {
  margin: 8px 0 0;
  color: var(--color-text-sub);
  line-height: 1.6;
}

.decision-form {
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  margin-top: 14px;
}

.decision-form textarea {
  min-height: 88px;
}

.danger {
  background: #dc2626;
  color: #fff;
}
</style>
