<script setup lang="ts">
defineProps<{
  citation: {
    citation_id?: string;
    source_file?: string;
    sourceFile?: string;
    section_title?: string;
    section?: string;
    page_number?: number | null;
    confidence?: number;
    snippet?: string;
  };
}>();
</script>

<template>
  <article class="citation-card">
    <div class="citation-head">
      <strong>{{ citation.source_file || citation.sourceFile || '课程知识库' }}</strong>
      <span>{{ Math.round((citation.confidence || 0) * 100) }}%</span>
    </div>
    <p>{{ citation.section_title || citation.section || '循环结构章节' }}<template v-if="citation.page_number"> · p.{{ citation.page_number }}</template></p>
    <blockquote>{{ citation.snippet || '暂无证据片段。' }}</blockquote>
    <small>{{ citation.citation_id || 'local-fallback-citation' }}</small>
  </article>
</template>

<style scoped>
.citation-card {
  border: 1px solid var(--border-light);
  border-radius: 10px;
  padding: 12px;
  background: #fff;
}
.citation-head {
  display: flex;
  justify-content: space-between;
  gap: 10px;
}
.citation-head span {
  color: var(--status-success-text);
  font-weight: 800;
}
p,
blockquote {
  margin: 8px 0 0;
  color: var(--text-secondary);
}
blockquote {
  border-left: 3px solid var(--color-primary);
  padding-left: 10px;
}
small {
  display: block;
  margin-top: 8px;
  color: var(--text-muted);
}
</style>
