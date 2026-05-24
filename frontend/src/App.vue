<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { RouterLink, RouterView } from 'vue-router';
import { api } from './api/client';
import type { RuntimeInfo } from './types';

const runtime = ref<RuntimeInfo | null>(null);

const navItems = [
  ['Dashboard', '/dashboard'],
  ['课程管理', '/courses'],
  ['知识库', '/knowledge-base'],
  ['学生画像', '/profiles'],
  ['学习路径', '/learning-paths'],
  ['资源生成', '/resources'],
  ['Agent 工作流', '/agent-workflow'],
  ['智能答疑', '/tutor-chat'],
  ['测验评价', '/quiz-evaluate'],
  ['教师分析', '/teacher-analysis'],
  ['报告中心', '/reports']
];

onMounted(async () => {
  runtime.value = await api.get<RuntimeInfo>('/api/v1/runtime').catch(() => ({ llm_mode: 'offline', mock_mode: true }));
});
</script>

<template>
  <div class="shell">
    <aside class="sidebar">
      <div class="brand">
        <strong>EduAgent Studio</strong>
        <span>中国软件杯 A3</span>
      </div>
      <nav>
        <RouterLink v-for="[label, path] in navItems" :key="path" :to="path">{{ label }}</RouterLink>
      </nav>
    </aside>
    <main class="main">
      <header class="topbar">
        <div>
          <h1>个性化学习资源生成与多智能体系统</h1>
          <p>课程知识库、学生画像、学习路径、资源生成、答疑、测评与报告闭环</p>
        </div>
        <span class="mode" :class="{ mock: runtime?.mock_mode }">
          {{ runtime?.mock_mode ? '演示 mock 模式' : `真实 AI 模式：${runtime?.llm_mode}` }}
        </span>
      </header>
      <RouterView />
    </main>
  </div>
</template>
