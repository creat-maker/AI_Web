<script setup lang="ts">
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import PageHeader from '../components/PageHeader.vue';

const route = useRoute();
const title = computed(() => String(route.meta.title || '能力说明'));
const description = computed(() => String(route.meta.description || '该入口用于说明平台可扩展能力和当前业务边界。'));
const nextSteps = computed(() => (Array.isArray(route.meta.nextSteps) ? route.meta.nextSteps as string[] : []));
</script>

<template>
  <section class="page">
    <PageHeader :title="title" :description="description" />
    <article class="data-card">
      <h2>平台能力说明</h2>
      <p class="muted">当前系统已覆盖课程、资源、画像、答疑、测评、报告、治理和运行状态等主链路。该入口保留为可扩展能力说明，避免访问时出现空白页面。</p>
      <ul v-if="nextSteps.length">
        <li v-for="item in nextSteps" :key="item">{{ item }}</li>
      </ul>
    </article>
  </section>
</template>
