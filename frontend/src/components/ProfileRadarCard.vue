<script setup lang="ts">
defineProps<{ dimensions: Array<{ dimension?: string; name?: string; score?: number; value?: number; label?: string }> }>();
</script>

<template>
  <div class="profile-radar-card">
    <article v-for="item in dimensions" :key="item.dimension || item.name">
      <div>
        <strong>{{ item.dimension || item.name }}</strong>
        <span>{{ item.label || '画像维度' }}</span>
      </div>
      <div class="progress-track">
        <span :style="{ width: `${item.score ?? item.value ?? 0}%` }"></span>
      </div>
      <b>{{ item.score ?? item.value ?? 0 }}</b>
    </article>
  </div>
</template>

<style scoped>
.profile-radar-card {
  display: grid;
  gap: 10px;
}
article {
  display: grid;
  grid-template-columns: 150px minmax(0, 1fr) 42px;
  gap: 10px;
  align-items: center;
}
strong,
span {
  display: block;
}
span {
  margin-top: 3px;
  color: var(--text-muted);
  font-size: 12px;
}
b {
  text-align: right;
}
</style>
