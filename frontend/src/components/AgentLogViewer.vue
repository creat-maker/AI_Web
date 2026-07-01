<script setup lang="ts">
defineProps<{
  steps: Array<{
    key?: string;
    name: string;
    status: string;
    duration?: string;
    duration_ms?: number;
    input_summary?: string;
    output_summary?: string;
    audit_result?: unknown;
    retry_count?: number;
    teacher_arbitration_status?: string;
  }>;
}>();

function tone(status: string) {
  if (['success', '成功', 'passed'].includes(status)) return 'success';
  if (['failed', 'error', '失败'].includes(status)) return 'danger';
  if (['running', '运行中'].includes(status)) return 'purple';
  return 'warning';
}
</script>

<template>
  <div class="agent-log-viewer">
    <article v-for="(step, index) in steps" :key="step.key || step.name" class="agent-log-item">
      <div class="agent-log-index">{{ index + 1 }}</div>
      <div>
        <div class="agent-log-head">
          <strong>{{ step.name }}</strong>
          <span :class="['status-badge', tone(step.status)]">{{ step.status }}</span>
        </div>
        <p><b>输入</b>{{ step.input_summary || '等待上游节点输入' }}</p>
        <p><b>输出</b>{{ step.output_summary || '等待节点输出' }}</p>
        <p class="agent-log-meta">
          耗时 {{ step.duration || `${step.duration_ms || 0}ms` }} · 回流 {{ step.retry_count || 0 }} 次 · 仲裁 {{ step.teacher_arbitration_status || '无' }}
        </p>
      </div>
    </article>
  </div>
</template>

<style scoped>
.agent-log-viewer {
  display: grid;
  gap: 12px;
}
.agent-log-item {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 12px;
  border: 1px solid var(--border-light);
  border-radius: 12px;
  padding: 14px;
  background: #fff;
}
.agent-log-index {
  display: inline-grid;
  place-items: center;
  width: 34px;
  height: 34px;
  border-radius: 10px;
  color: #fff;
  background: var(--color-primary);
  font-weight: 800;
}
.agent-log-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}
p {
  margin: 8px 0 0;
  color: var(--text-secondary);
}
b {
  margin-right: 8px;
  color: var(--color-primary-dark);
}
.agent-log-meta {
  color: var(--text-muted);
  font-size: 13px;
}
</style>
