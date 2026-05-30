<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import EmptyState from '../components/EmptyState.vue';

const route = useRoute();
const loading = ref(true);
const error = ref('');

const title = computed(() => String(route.meta.title || '规划中模块'));
const description = computed(() => String(route.meta.description || '该模块已进入三端角色化菜单，后续接入具体业务能力。'));
const nextSteps = computed(() => {
  const items = route.meta.nextSteps;
  return Array.isArray(items) ? items.map(String) : ['接入真实业务接口', '补充列表、详情和操作流', '保留 demo/fallback 能力边界说明'];
});

onMounted(() => {
  try {
    loading.value = false;
  } catch (err) {
    error.value = err instanceof Error ? err.message : '占位模块加载失败。';
  }
});
</script>

<template>
  <section class="page">
    <p v-if="loading" class="panel muted">正在加载模块说明...</p>
    <p v-if="error" class="panel error-text">{{ error }}</p>
    <template v-if="!loading && !error">
      <article class="placeholder-hero">
        <span class="status-badge neutral">第一阶段占位</span>
        <h2>{{ title }}</h2>
        <p>{{ description }}</p>
      </article>

      <div class="role-layout">
        <article class="panel">
          <h2>模块用途</h2>
          <p>{{ description }}</p>
          <p class="demo-banner">当前为三端架构第一阶段占位页，不伪装成已完成真实业务能力。</p>
        </article>

        <article class="panel">
          <h2>后续接入能力</h2>
          <div v-if="nextSteps.length" class="list">
            <div v-for="item in nextSteps" :key="item" class="item compact">{{ item }}</div>
          </div>
          <EmptyState v-else title="暂无规划项" description="后续根据比赛演示路线补齐。" />
        </article>
      </div>
    </template>
  </section>
</template>
