<script setup lang="ts">
defineProps<{ logs: Array<{ time?: string; timestamp?: string; trigger?: string; old_level?: string; new_level?: string; reason?: string; inserted_tasks?: string[]; related_concepts?: string[] }> }>();
</script>

<template>
  <div class="path-timeline">
    <article v-for="(item, index) in logs" :key="`${item.time || item.timestamp}-${index}`">
      <span class="dot"></span>
      <div>
        <strong>{{ item.trigger || '路径调整' }} · {{ item.new_level || '巩固练习' }}</strong>
        <p>{{ item.reason || '根据测验结果和 DKVMN 掌握度调整路径。' }}</p>
        <small>{{ item.time || item.timestamp || '最近更新' }} · {{ (item.inserted_tasks || []).join('、') || '补弱任务' }}</small>
      </div>
    </article>
  </div>
</template>

<style scoped>
.path-timeline {
  display: grid;
  gap: 12px;
}
article {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 10px;
}
.dot {
  width: 12px;
  height: 12px;
  margin-top: 6px;
  border-radius: 999px;
  background: var(--color-primary);
}
p {
  margin: 6px 0 0;
  color: var(--text-secondary);
}
small {
  display: block;
  margin-top: 6px;
  color: var(--text-muted);
}
</style>
