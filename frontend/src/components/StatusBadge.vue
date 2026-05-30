<script setup lang="ts">
defineProps<{
  label: string;
  tone?: 'info' | 'success' | 'warning' | 'danger' | 'neutral';
}>();
</script>

<template>
  <span :class="['status-badge', tone || 'info']">{{ label }}</span>
</template>
