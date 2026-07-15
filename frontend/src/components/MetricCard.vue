<script setup lang="ts">
defineProps<{ label: string; value: string | number; unit?: string; hint?: string; tone?: string }>();
</script>

<template>
  <article :class="['stat-card', tone]">
    <div class="stat-content">
      <span>{{ label }}</span>
      <strong>{{ value }}<small v-if="unit">{{ unit }}</small></strong>
      <p v-if="hint">{{ hint }}</p>
    </div>
  </article>
</template>
