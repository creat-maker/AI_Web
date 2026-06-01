<script setup lang="ts">
defineProps<{
  title?: string;
  subtitle?: string;
}>();
</script>

<template>
  <article class="data-card">
    <div v-if="title || subtitle || $slots.action" class="card-title">
      <div>
        <h2 v-if="title">{{ title }}</h2>
        <p v-if="subtitle" class="muted">{{ subtitle }}</p>
      </div>
      <slot name="action" />
    </div>
    <slot />
  </article>
</template>
