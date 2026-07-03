<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import { api } from '../api/client';
import DataCard from '../components/DataCard.vue';
import PageHeader from '../components/PageHeader.vue';
import StatusBadge from '../components/StatusBadge.vue';

interface ArbitrationTask {
  id: string;
  agent_run_id?: number;
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

const fallbackTasks: ArbitrationTask[] = [
  {
    id: 'demo-arb-low',
    student_name: '李明',
    course: 'Python 程序设计',
    topic: 'while 循环条件更新',
    risk_level: 'low',
    trigger_reason: '引用证据充分，但建议教师确认示例输出。',
    original_content: 'while 循环补弱讲义与变量更新练习。',
    suggested_content: '发布到学生端，并保留引用来源。',
    review_result: 'pending',
    retry_count: 0,
    rag_citations: ['python_programming.json-001'],
    profile_risk_evidence: ['while_loop 掌握度 0.48'],
    recommended_action: 'approve',
    status: 'pending'
  },
  {
    id: 'demo-arb-medium',
    student_name: '李明',
    course: 'Python 程序设计',
    topic: 'break / continue 对比',
    risk_level: 'medium',
    trigger_reason: '审核发现示例解释略少，需要教师补充说明。',
    original_content: 'break 和 continue 的输出判断题。',
    suggested_content: '补充 continue 跳过本轮但不跳出循环的解释。',
    review_result: 'needs_review',
    retry_count: 1,
    rag_citations: ['python_programming.json-002', 'python_programming.json-003'],
    profile_risk_evidence: ['break_continue 错误 streak=2'],
    recommended_action: 'revise',
    status: 'pending'
  },
  {
    id: 'demo-arb-high',
    student_name: '李明',
    course: 'Python 程序设计',
    topic: '循环结构扩展资源',
    risk_level: 'high',
    trigger_reason: '内容出现课程范围外示例，需拦截或重写。',
    original_content: '将循环结构扩展到股票预测与机器学习训练。',
    suggested_content: '拒绝该版本，重新回到 Python 循环基础。',
    review_result: 'blocked',
    retry_count: 3,
    rag_citations: [],
    profile_risk_evidence: ['课程对齐度低', '超纲风险高'],
    recommended_action: 'reject',
    status: 'pending'
  }
];

const tasks = ref<ArbitrationTask[]>(fallbackTasks);
const loading = ref(false);
const message = ref('');
const comments = reactive<Record<string, string>>({});
const revisedContent = reactive<Record<string, string>>({});
const suggestedActions = reactive<Record<string, string>>({});

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
  try {
    const result = await api.get<ArbitrationTask[]>('/api/v1/teacher-arbitrations');
    tasks.value = result.length ? result : fallbackTasks;
    message.value = '教师仲裁队列已刷新。';
  } catch {
    tasks.value = fallbackTasks;
    message.value = '当前网络不稳定，已展示本地仲裁演示队列。';
  } finally {
    loading.value = false;
  }
}

async function decide(task: ArbitrationTask, decision: 'approve' | 'revise' | 'reject') {
  const teacherComment = comments[task.id] || (
    decision === 'approve' ? '内容可发布，保留引用证据。' :
    decision === 'revise' ? '请按教师意见修改后重新生成。' :
    '超出课程范围，拒绝发布。'
  );
  try {
    const result = await api.post<{ status: string; message?: string }>(`/api/v1/teacher-arbitration/${task.agent_run_id || task.id}/decision`, {
      decision,
      teacher_comment: teacherComment,
      comment: teacherComment,
      revised_content: decision === 'revise' ? (revisedContent[task.id] || task.suggested_content) : undefined,
      suggested_action: suggestedActions[task.id] || task.recommended_action
    });
    task.status = result.status;
    task.teacher_comment = teacherComment;
    message.value = result.message || '教师仲裁结果已提交。';
  } catch (err) {
    message.value = err instanceof Error ? err.message : '教师仲裁提交失败。';
  }
}

onMounted(load);
</script>

<template>
  <section class="page decision-center-page">
    <PageHeader title="教师仲裁中心" description="复核高风险或多次审核未通过的路径、资源与报告，形成 approve / revise / reject 闭环。">
      <template #actions>
        <button class="secondary" :disabled="loading" @click="load">{{ loading ? '刷新中...' : '刷新' }}</button>
      </template>
    </PageHeader>

    <p v-if="message" class="panel muted">{{ message }}</p>

    <div class="arbitration-list">
      <DataCard v-for="task in tasks" :key="task.id" :title="`${task.student_name} · ${task.topic}`" :subtitle="`${task.course} · retry ${task.retry_count}`">
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
          <button type="button" @click="decide(task, 'approve')">通过</button>
          <button type="button" class="secondary" @click="decide(task, 'revise')">修改</button>
          <button type="button" class="danger" @click="decide(task, 'reject')">拒绝</button>
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
