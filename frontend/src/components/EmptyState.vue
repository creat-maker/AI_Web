<script setup lang="ts">
defineProps<{
  title: string;
  description?: string;
}>();
</script>

<template>
  <div class="empty-card">
    <strong>{{ title }}</strong>
    <p v-if="description">{{ description }}</p>
  </div>
</template>
