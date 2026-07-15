<script setup lang="ts">
defineProps<{ title?: string; subtitle?: string }>();
</script>

<template>
  <section class="panel">
    <div v-if="title || subtitle || $slots.action" class="panel-title">
      <div>
        <h2 v-if="title">{{ title }}</h2>
        <p v-if="subtitle" class="muted">{{ subtitle }}</p>
      </div>
      <slot name="action" />
    </div>
    <slot />
  </section>
</template>
