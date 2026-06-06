<script setup lang="ts">
defineProps<{
  label: string;
  value: string | number;
  unit?: string;
  hint?: string;
  icon?: string;
  trend?: string;
  tone?: 'blue' | 'green' | 'orange' | 'purple' | 'red' | 'cyan';
}>();
</script>

<template>
  <article :class="['stat-card', tone || 'blue']">
    <div class="stat-content">
      <span class="stat-label">{{ label }}</span>
      <strong class="stat-value">{{ value }}<small v-if="unit">{{ unit }}</small></strong>
      <p v-if="hint || trend" class="stat-hint">
        <template v-if="hint">{{ hint }}</template>
        <template v-if="trend"> {{ trend }}</template>
      </p>
    </div>
    <span class="stat-icon">{{ icon || label.slice(0, 1) }}</span>
  </article>
</template>
