<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted, nextTick, watch } from 'vue';

interface MindmapNode {
  label: string;
  children?: MindmapNode[];
}

const props = defineProps<{
  data: MindmapNode;
}>();

type SectionType = 'concepts' | 'associations' | 'path' | 'default';

const sectionMeta: Record<SectionType, { accent: string; icon: string; border: string }> = {
  concepts: { accent: '#2563eb', icon: '&#9670;', border: '#2563eb' },
  associations: { accent: '#7c3aed', icon: '&#9656;', border: '#7c3aed' },
  path: { accent: '#d97706', icon: '&#9654;', border: '#d97706' },
  default: { accent: '#64748b', icon: '&#9679;', border: '#64748b' },
};

function detectSection(label: string): SectionType {
  if (/核心概念|概念|标签/.test(label)) return 'concepts';
  if (/知识关联|关联|映射|关系/.test(label)) return 'associations';
  if (/学习路径|路径|步骤|流程/.test(label)) return 'path';
  return 'default';
}

const sections = computed(() => {
  return (props.data.children ?? []).map((child) => {
    const sectionType = detectSection(child.label);
    return { ...child, sectionType, meta: sectionMeta[sectionType] };
  });
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

/* ── 树状连线：动态 SVG 定位 ── */
const gridRef = ref<HTMLElement | null>(null);
const treeSvgPaths = ref<string>('');
const isNarrow = ref(false);

function updateTreeLines() {
  const grid = gridRef.value;
  if (!grid) return;

  const cards = grid.querySelectorAll('.kg-branch-card');
  if (cards.length === 0) return;

  const gridRect = grid.getBoundingClientRect();
  const points: { x: number; y: number }[] = [];

  cards.forEach((card) => {
    const rect = card.getBoundingClientRect();
    points.push({
      x: rect.left + rect.width / 2 - gridRect.left,
      y: 0,
    });
  });

  // 检查是否窄屏（卡片纵向堆叠）
  const firstRect = cards[0].getBoundingClientRect();
  const secondRect = cards.length > 1 ? cards[1].getBoundingClientRect() : null;
  isNarrow.value = secondRect !== null && Math.abs(firstRect.top - secondRect.top) > 10;

  if (isNarrow.value || points.length <= 1) {
    treeSvgPaths.value = '';
    return;
  }

  const svgW = gridRect.width;
  const stemH = 14;
  const dropH = 12;
  const totalH = stemH + dropH;
  const barY = stemH;

  let d = '';
  // 主干
  d += `M ${svgW / 2} 0 L ${svgW / 2} ${barY} `;
  // 横干：从最左分支中心到最右分支中心
  const leftX = points[0].x;
  const rightX = points[points.length - 1].x;
  d += `M ${leftX} ${barY} L ${rightX} ${barY} `;
  // 分支竖线
  points.forEach((p) => {
    d += `M ${p.x} ${barY} L ${p.x} ${totalH} `;
  });

  treeSvgPaths.value = d;
}

let resizeObserver: ResizeObserver | null = null;

onMounted(() => {
  nextTick(updateTreeLines);
  if (gridRef.value) {
    resizeObserver = new ResizeObserver(updateTreeLines);
    resizeObserver.observe(gridRef.value);
  }
});

onUnmounted(() => {
  resizeObserver?.disconnect();
});

watch(() => props.data, () => nextTick(updateTreeLines));
</script>

<template>
  <div class="kg-radiate">
    <!-- 主节点胶囊 -->
    <div class="kg-center-node">
      <span class="kg-center-label">{{ data.label }}</span>
    </div>

    <!-- 树状连接线 SVG -->
    <svg
      v-if="treeSvgPaths && !isNarrow"
      class="kg-tree-svg"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
    >
      <path :d="treeSvgPaths" stroke="#e2e8f0" stroke-width="1.5" stroke-linecap="round" />
    </svg>

    <!-- 窄屏：简单主干线 -->
    <div v-if="isNarrow" class="kg-tree-stem-narrow"></div>

    <!-- 分支卡片网格 -->
    <div ref="gridRef" class="kg-branch-grid">
      <div
        v-for="(section, i) in sections"
        :key="i"
        :class="['kg-branch-card', `kg-branch--${section.sectionType}`]"
        :style="{ '--accent': section.meta.accent, '--border-top': section.meta.border }"
      >
        <!-- 卡片头部 -->
        <div class="kg-branch-header">
          <span class="kg-branch-icon" v-html="section.meta.icon"></span>
          <h3 class="kg-branch-title">{{ section.label }}</h3>
        </div>

        <!-- ═══ 核心概念 → Tag 标签云 ═══ -->
        <template v-if="section.sectionType === 'concepts'">
          <div class="kg-tag-cloud">
            <span v-for="(child, j) in section.children" :key="j" class="kg-tag">
              {{ child.label }}
            </span>
          </div>
        </template>

        <!-- ═══ 知识关联 → 轻量键值对 ═══ -->
        <template v-else-if="section.sectionType === 'associations'">
          <div class="kg-kv-list">
            <div v-for="(child, j) in section.children" :key="j" class="kg-kv-item">
              <template v-if="parseKV(child.label)">
                <span class="kg-kv-key">{{ parseKV(child.label)!.key }}</span>
                <span class="kg-kv-sep">→</span>
                <span class="kg-kv-value">{{ parseKV(child.label)!.value }}</span>
              </template>
              <template v-else>
                <span class="kg-kv-key">层级 {{ j + 1 }}</span>
                <span class="kg-kv-sep">→</span>
                <span class="kg-kv-value">{{ child.label }}</span>
              </template>
            </div>
          </div>
        </template>

        <!-- ═══ 学习路径 → 精致 Stepper ═══ -->
        <template v-else-if="section.sectionType === 'path'">
          <div class="kg-stepper">
            <div v-for="(child, j) in section.children" :key="j" class="kg-step">
              <div class="kg-step-rail">
                <span class="kg-step-dot">{{ extractStepNumber(child.label)?.num ?? (j + 1) }}</span>
                <span v-if="j < section.children!.length - 1" class="kg-step-line"></span>
              </div>
              <div class="kg-step-body">
                <span class="kg-step-text">{{ extractStepNumber(child.label)?.text ?? child.label }}</span>
              </div>
            </div>
          </div>
        </template>

        <!-- ═══ 默认 ═══ -->
        <template v-else>
          <div class="kg-plain-list">
            <span v-for="(child, j) in section.children" :key="j" class="kg-plain-item">
              {{ child.label }}
            </span>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ═══════════════════════════════════════════
   中心辐射式知识图谱 — SVG 树状连线
   ═══════════════════════════════════════════ */

.kg-radiate {
  padding: 12px 0;
  line-height: 1.6;
}

/* ── 主节点胶囊 ── */
.kg-center-node {
  display: flex;
  justify-content: center;
}

.kg-center-label {
  display: inline-flex;
  align-items: center;
  padding: 10px 32px;
  border-radius: 28px;
  background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  color: #f8fafc;
  font-size: 1.15rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  box-shadow: 0 4px 20px rgba(30, 41, 59, 0.25);
}

/* ═══════════════════════════════════════════
   SVG 树状连线
   通过 ResizeObserver 动态计算卡片位置，
   绘制：主干 → 横干 → 分支竖线
   ═══════════════════════════════════════════ */

.kg-tree-svg {
  display: block;
  width: 100%;
  height: 26px; /* stemH(14) + dropH(12) */
  overflow: visible;
  z-index: 0;
  position: relative;
}

/* 窄屏简单主干线 */
.kg-tree-stem-narrow {
  width: 1.5px;
  height: 14px;
  background: #e2e8f0;
  margin: 0 auto;
}

/* ═══════════════════════════════════════════
   分支卡片网格
   ═══════════════════════════════════════════ */

.kg-branch-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  position: relative;
  z-index: 1;
}

/* ── 单个分支卡片 ── */
.kg-branch-card {
  background: #ffffff;
  border-radius: 14px;
  padding: 20px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.06), 0 4px 16px rgba(0, 0, 0, 0.04);
  border-top: 3px solid var(--border-top);
  transition: box-shadow 0.2s ease, transform 0.2s ease;
}

.kg-branch-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08), 0 8px 28px rgba(0, 0, 0, 0.06);
  transform: translateY(-2px);
}

/* ── 卡片头部 ── */
.kg-branch-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.kg-branch-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  border-radius: 8px;
  background: color-mix(in srgb, var(--accent) 12%, transparent);
  color: var(--accent);
  font-size: 0.7rem;
  flex-shrink: 0;
}

.kg-branch-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

/* ═══ Tag 标签云 ═══ */
.kg-tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.kg-tag {
  display: inline-flex;
  align-items: center;
  padding: 5px 14px;
  border-radius: 18px;
  background: color-mix(in srgb, var(--accent) 10%, transparent);
  color: var(--accent);
  font-size: 0.82rem;
  font-weight: 500;
  cursor: default;
  border: 1px solid color-mix(in srgb, var(--accent) 18%, transparent);
  transition: all 0.2s ease;
  user-select: none;
}

.kg-tag:hover {
  background: color-mix(in srgb, var(--accent) 20%, transparent);
  border-color: color-mix(in srgb, var(--accent) 35%, transparent);
  box-shadow: 0 2px 10px color-mix(in srgb, var(--accent) 20%, transparent);
  transform: translateY(-1px);
}

/* ═══ 轻量键值对 ═══ */
.kg-kv-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.kg-kv-item {
  display: flex;
  align-items: baseline;
  gap: 8px;
  padding: 6px 0;
}

.kg-kv-key {
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--accent);
  white-space: nowrap;
  flex-shrink: 0;
  background: color-mix(in srgb, var(--accent) 10%, transparent);
  padding: 2px 8px;
  border-radius: 4px;
}

.kg-kv-sep {
  color: #cbd5e1;
  font-size: 0.75rem;
  flex-shrink: 0;
}

.kg-kv-value {
  font-size: 0.85rem;
  color: #334155;
  line-height: 1.6;
}

/* ═══ 精致 Stepper ═══ */
.kg-stepper {
  display: flex;
  flex-direction: column;
}

.kg-step {
  display: grid;
  grid-template-columns: 36px 1fr;
  min-height: 44px;
}

.kg-step-rail {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.kg-step-dot {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: var(--accent);
  color: #fff;
  font-size: 0.75rem;
  font-weight: 700;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  z-index: 1;
  box-shadow: 0 2px 8px color-mix(in srgb, var(--accent) 35%, transparent);
}

.kg-step-line {
  width: 2px;
  flex: 1;
  min-height: 16px;
  background: linear-gradient(to bottom, color-mix(in srgb, var(--accent) 30%, transparent), transparent);
  border-radius: 1px;
}

.kg-step-body {
  display: flex;
  align-items: center;
  padding: 2px 0 14px 10px;
}

.kg-step-text {
  font-size: 0.85rem;
  color: #1e293b;
  line-height: 1.6;
  background: linear-gradient(transparent 62%, color-mix(in srgb, var(--accent) 18%, transparent) 62%);
  padding: 0 2px;
  font-weight: 500;
}

.kg-step:last-child .kg-step-body {
  padding-bottom: 0;
}

.kg-step:last-child .kg-step-line {
  display: none;
}

/* ═══ 默认列表 ═══ */
.kg-plain-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.kg-plain-item {
  font-size: 0.85rem;
  color: #475569;
  line-height: 1.6;
  padding-left: 12px;
  position: relative;
}

.kg-plain-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 10px;
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--accent);
  opacity: 0.5;
}

/* ═══════════════════════════════════════════
   响应式：窄屏隐藏树状连线，改用左侧时间轴
   ═══════════════════════════════════════════ */

@media (max-width: 640px) {
  .kg-branch-grid {
    grid-template-columns: 1fr;
  }

  .kg-tree-svg {
    display: none;
  }

  .kg-center-label {
    font-size: 1rem;
    padding: 8px 24px;
  }

  /* 窄屏：卡片左侧加竖线时间轴 */
  .kg-branch-card {
    position: relative;
    margin-left: 20px;
  }

  .kg-branch-card::before {
    content: '';
    position: absolute;
    left: -20px;
    top: 0;
    bottom: 0;
    width: 1.5px;
    background: #e2e8f0;
  }

  .kg-branch-card::after {
    content: '';
    position: absolute;
    left: -24px;
    top: 20px;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--border-top);
  }
}
</style>
