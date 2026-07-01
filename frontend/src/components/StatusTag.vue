<script setup lang="ts">
defineProps<{ label: string; tone?: 'success' | 'warning' | 'danger' | 'info' | 'neutral' | 'purple' }>();
</script>

<template>
  <span :class="['status-badge', tone || 'info']">{{ label }}</span>
</template>
