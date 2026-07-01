<script setup lang="ts">
import { onMounted, ref } from 'vue';

const loading = ref(true);
const error = ref('');

onMounted(() => {
  try {
    loading.value = false;
  } catch (err) {
    error.value = err instanceof Error ? err.message : '能力边界说明加载失败。';
  }
});
</script>

<template>
  <section class="page">
    <p v-if="loading" class="panel muted">正在加载系统能力边界说明...</p>
    <p v-if="error" class="panel error-text">{{ error }}</p>

    <template v-if="!loading && !error">
      <article class="placeholder-hero">
        <span class="status-badge warning">演示模式说明</span>
        <h2>系统能力边界说明</h2>
        <p>用于说明真实实现、当前能力边界和后续可扩展位置，避免把轻量能力描述为完整生产能力。</p>
      </article>

      <div class="role-layout">
        <article class="panel">
          <h2>当前真实能力</h2>
          <div class="list">
            <div class="item compact">FastAPI 接口、Vue 路由和三端 Layout 为项目内真实实现。</div>
            <div class="item compact">SQLite fallback 会持久化课程、文档、问答、报告、日志和测评记录。</div>
            <div class="item compact">知识库上传、文本切片、检索、报告下载和日志聚合沿用现有项目能力。</div>
          </div>
        </article>

        <article class="panel">
          <h2>本地运行与降级能力</h2>
          <div class="list">
            <div class="item compact">未配置真实模型 Key 时使用本地智能评测引擎。</div>
            <div class="item compact">科大讯飞 TTS / Spark / Safety 为可配置服务；无 Key 时系统使用本地智能评测引擎稳定运行。</div>
            <div class="item compact">防幻觉机制包含课程知识库引用、内容审核、人工复核和可接入讯飞安全服务。</div>
            <div class="item compact">RAG 质量诊断、query rewrite、错因识别和掌握度变化为规则估计。</div>
            <div class="item compact">Agent 工作流为 EduMind 内置轻量编排，后续可接入真实 LangGraph。</div>
          </div>
        </article>
      </div>

      <div class="role-layout">
        <article class="panel">
          <h2>后续真实能力接入位置</h2>
          <div class="list">
            <div class="item compact">真实 RAG：替换 `backend/app/rag/vector_store.py` 和 TutorChat 检索链。</div>
            <div class="item compact">真实 LangGraph：替换 AgentWorkflow 的本地节点执行和 run_id 写入。</div>
            <div class="item compact">真实知识追踪：将 TeacherAnalysis 的规则掌握度替换为 BKT/DKT 服务。</div>
          </div>
        </article>

        <article class="panel">
          <h2>开源组件与合规说明</h2>
          <p>本项目仅参考 RAG、Agent、引用溯源、教学闭环等功能思想，没有下载、复制或缝合 Dify、RAGFlow、FastGPT、OpenTutor 等项目源码。</p>
          <p class="muted">新增三端角色化能力为 EduMind 内部前端状态和布局实现，不涉及外部品牌素材、Logo 或商业文案。</p>
        </article>
      </div>
    </template>
  </section>
</template>
