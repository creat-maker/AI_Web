<script setup lang="ts">
import { computed } from 'vue';

interface MindmapNode {
  label: string;
  children?: MindmapNode[];
}

const props = defineProps<{
  data: MindmapNode;
}>();

type SectionType = 'concepts' | 'associations' | 'path' | 'default';

function detectSection(label: string): SectionType {
  if (/核心概念|概念|标签/.test(label)) return 'concepts';
  if (/知识关联|关联|映射|关系/.test(label)) return 'associations';
  if (/学习路径|路径|步骤|流程/.test(label)) return 'path';
  return 'default';
}

const sections = computed(() => {
  return (props.data.children ?? []).map((child) => ({
    ...child,
    sectionType: detectSection(child.label),
  }));
});

function parseKV(label: string): { key: string; value: string } | null {
  const match = label.match(/^(.+?)[：:]\s*(.+)$/);
  if (match) return { key: match[1].trim(), value: match[2].trim() };
  return null;
}

function extractStepNumber(label: string): { num: number; text: string } | null {
  const match = label.match(/^(\d+)[.、．]\s*(.+)$/);
  if (match) return { num: parseInt(match[1], 10), text: match[2].trim() };
  return null;
}
</script>

<template>
  <div class="kg-viewer">
    <!-- Root title -->
    <h3 class="kg-root-title">{{ data.label }}</h3>

    <div class="kg-sections">
      <div v-for="(section, i) in sections" :key="i" :class="['kg-section', `kg-section--${section.sectionType}`]">

        <!-- ═══ 核心概念 → Tag 胶囊 ═══ -->
        <template v-if="section.sectionType === 'concepts'">
          <div class="kg-section-header">
            <span class="kg-section-icon concepts-icon">&#9670;</span>
            <h3 class="kg-section-title">{{ section.label }}</h3>
          </div>
          <div class="kg-tag-row">
            <span v-for="(child, j) in section.children" :key="j" class="kg-tag">
              {{ child.label }}
            </span>
          </div>
        </template>

        <!-- ═══ 知识关联 → 键值对表格 ═══ -->
        <template v-else-if="section.sectionType === 'associations'">
          <div class="kg-section-header">
            <span class="kg-section-icon assoc-icon">&#9656;</span>
            <h3 class="kg-section-title">{{ section.label }}</h3>
          </div>
          <div class="kg-kv-table">
            <div v-for="(child, j) in section.children" :key="j" class="kg-kv-row">
              <template v-if="parseKV(child.label)">
                <span class="kg-kv-key">{{ parseKV(child.label)!.key }}</span>
                <span class="kg-kv-value">{{ parseKV(child.label)!.value }}</span>
              </template>
              <template v-else>
                <span class="kg-kv-key">层级 {{ j + 1 }}</span>
                <span class="kg-kv-value">{{ child.label }}</span>
              </template>
            </div>
          </div>
        </template>

        <!-- ═══ 学习路径 → 垂直 Stepper ═══ -->
        <template v-else-if="section.sectionType === 'path'">
          <div class="kg-section-header">
            <span class="kg-section-icon path-icon">&#9654;</span>
            <h3 class="kg-section-title">{{ section.label }}</h3>
          </div>
          <div class="kg-stepper">
            <div v-for="(child, j) in section.children" :key="j" class="kg-step">
              <div class="kg-step-rail">
                <span class="kg-step-dot">{{ extractStepNumber(child.label)?.num ?? (j + 1) }}</span>
                <span v-if="j < section.children!.length - 1" class="kg-step-line"></span>
              </div>
              <div class="kg-step-content">
                <span class="kg-step-text">{{ extractStepNumber(child.label)?.text ?? child.label }}</span>
              </div>
            </div>
          </div>
        </template>

        <!-- ═══ 默认：简洁列表 ═══ -->
        <template v-else>
          <div class="kg-section-header">
            <span class="kg-section-icon default-icon">&#9679;</span>
            <h3 class="kg-section-title">{{ section.label }}</h3>
          </div>
          <div class="kg-default-list">
            <span v-for="(child, j) in section.children" :key="j" class="kg-default-item">
              {{ child.label }}
            </span>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ── 全局容器 ── */
.kg-viewer {
  padding: 8px 0;
  line-height: 1.6;
}

.kg-root-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-main, #0f172a);
  margin: 0 0 24px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f1f5f9;
  text-align: center;
}

/* ── 模块分区 ── */
.kg-sections {
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.kg-section {
  /* 无边框，纯留白分隔 */
}

.kg-section-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 14px;
}

.kg-section-icon {
  font-size: 0.75rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 6px;
  flex-shrink: 0;
}

.concepts-icon {
  background: #eff6ff;
  color: #2563eb;
}

.assoc-icon {
  background: #f0fdf4;
  color: #16a34a;
}

.path-icon {
  background: #fef3c7;
  color: #d97706;
}

.default-icon {
  background: #f5f3ff;
  color: #7c3aed;
}

.kg-section-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-main, #0f172a);
  margin: 0;
}

/* ═══ Tag 胶囊样式 ═══ */
.kg-tag-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.kg-tag {
  display: inline-flex;
  align-items: center;
  padding: 6px 16px;
  border-radius: 20px;
  background: #eff6ff;
  color: #1d4ed8;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.15s ease;
  cursor: default;
  border: none;
}

.kg-tag:hover {
  background: #dbeafe;
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.12);
}

/* ═══ 键值对表格 ═══ */
.kg-kv-table {
  display: flex;
  flex-direction: column;
  gap: 0;
  border-radius: 10px;
  overflow: hidden;
  background: #fafbfc;
}

.kg-kv-row {
  display: grid;
  grid-template-columns: 120px 1fr;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid #f1f5f9;
  transition: background 0.12s;
}

.kg-kv-row:last-child {
  border-bottom: none;
}

.kg-kv-row:hover {
  background: #f8fafc;
}

.kg-kv-key {
  font-size: 0.875rem;
  font-weight: 600;
  color: #475569;
  white-space: nowrap;
  padding-right: 16px;
}

.kg-kv-value {
  font-size: 0.875rem;
  color: #0f172a;
  line-height: 1.6;
}

.kg-kv-value :deep(mark) {
  background: #fef08a;
  padding: 1px 4px;
  border-radius: 3px;
}

/* ═══ 垂直 Stepper ═══ */
.kg-stepper {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.kg-step {
  display: grid;
  grid-template-columns: 40px 1fr;
  gap: 0;
  min-height: 48px;
}

.kg-step-rail {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.kg-step-dot {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: linear-gradient(135deg, #2563eb, #3b82f6);
  color: #fff;
  font-size: 0.8rem;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  z-index: 1;
  box-shadow: 0 2px 6px rgba(37, 99, 235, 0.25);
}

.kg-step-line {
  width: 2px;
  flex: 1;
  min-height: 20px;
  background: repeating-linear-gradient(
    to bottom,
    #cbd5e1 0px,
    #cbd5e1 4px,
    transparent 4px,
    transparent 8px
  );
}

.kg-step-content {
  display: flex;
  align-items: center;
  padding: 4px 0 16px 12px;
}

.kg-step-text {
  font-size: 0.9rem;
  color: #0f172a;
  line-height: 1.6;
  background: linear-gradient(transparent 60%, #fef08a 60%);
  padding: 0 2px;
}

.kg-step:last-child .kg-step-content {
  padding-bottom: 0;
}

/* ═══ 默认列表 ═══ */
.kg-default-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding-left: 8px;
}

.kg-default-item {
  font-size: 0.875rem;
  color: #475569;
  line-height: 1.6;
  padding: 4px 0;
}

.kg-default-item::before {
  content: '·';
  margin-right: 8px;
  color: #94a3b8;
}
</style>
