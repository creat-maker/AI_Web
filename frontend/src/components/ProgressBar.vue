<script setup lang="ts">
withDefaults(
  defineProps<{
    value: number;
    tone?: 'primary' | 'success' | 'warning' | 'danger';
    label?: string;
    showValue?: boolean;
  }>(),
  {
    tone: 'primary',
    showValue: false
  }
);
</script>

<template>
  <div class="progress-wrap">
    <div v-if="label || showValue" class="progress-label">
      <span>{{ label || '进度' }}</span>
      <strong>{{ Math.round(Math.max(0, Math.min(100, value))) }}%</strong>
    </div>
    <div :class="['progress-track', tone === 'primary' ? '' : tone]" aria-hidden="true">
      <span :style="{ width: `${Math.max(0, Math.min(100, value))}%` }"></span>
    </div>
  </div>
</template>
