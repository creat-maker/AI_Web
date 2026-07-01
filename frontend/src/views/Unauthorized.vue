<script setup lang="ts">
import { computed } from 'vue';
import { RouterLink } from 'vue-router';
import PageHeader from '../components/PageHeader.vue';
import { useRole } from '../composables/useRole';

const { currentHomePath, currentRoleLabel } = useRole();
const message = computed(() => `当前角色无权限访问该页面。当前会话为${currentRoleLabel.value}，请返回对应工作台继续操作。`);
</script>

<template>
  <section class="page">
    <PageHeader title="无访问权限" :description="message">
      <template #actions>
        <RouterLink class="btn" :to="currentHomePath">返回工作台</RouterLink>
        <RouterLink class="btn secondary" to="/login">切换账号</RouterLink>
      </template>
    </PageHeader>
    <article class="data-card">
      <h2>权限说明</h2>
      <p class="muted">系统按学生端、教师端、管理员端划分业务入口。请使用对应角色访问课程、资源、报告和治理页面。</p>
    </article>
  </section>
</template>
