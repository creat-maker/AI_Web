<script setup lang="ts">
defineProps<{
  label: string;
  value: string | number;
  unit?: string;
  hint?: string;
  tone?: 'blue' | 'green' | 'orange' | 'purple';
}>();
</script>

<template>
  <article :class="['stat-card', tone || 'blue']">
    <span>{{ label }}</span>
    <strong>{{ value }}<small v-if="unit">{{ unit }}</small></strong>
    <p v-if="hint">{{ hint }}</p>
  </article>
</template>
