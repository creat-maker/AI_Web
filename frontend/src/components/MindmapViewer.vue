<script setup lang="ts">
import { computed, ref } from 'vue';
import MindmapBranch from './MindmapBranch.vue';

interface MindmapNode {
  label: string;
  children?: MindmapNode[];
}

const props = defineProps<{
  data: MindmapNode;
}>();

const collapsed = ref<Set<string>>(new Set());

function toggle(key: string) {
  const next = new Set(collapsed.value);
  if (next.has(key)) {
    next.delete(key);
  } else {
    next.add(key);
  }
  collapsed.value = next;
}

const hasChildren = computed(() => (props.data.children?.length ?? 0) > 0);
</script>

<template>
  <div class="mindmap-viewer">
    <div class="mindmap-root">
      <div class="mindmap-node root-node">
        <span class="node-label root-label">{{ data.label }}</span>
      </div>
      <div v-if="hasChildren" class="mindmap-branches">
        <div v-for="(child, i) in data.children" :key="i" class="mindmap-branch">
          <MindmapBranch :node="child" :path="`root/${child.label}`" :collapsed="collapsed" @toggle="toggle" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.mindmap-viewer {
  padding: 20px;
  overflow-x: auto;
}

.mindmap-root {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 24px;
}

.root-node {
  background: var(--color-primary);
  color: var(--text-light);
  border-radius: 12px;
  padding: 12px 28px;
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
}

.root-label {
  font-size: 1.1rem;
  font-weight: 700;
}

.mindmap-branches {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
  justify-content: center;
}

.mindmap-branch {
  flex: 0 1 auto;
  min-width: 180px;
}
</style>
