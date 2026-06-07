<script setup lang="ts">
import { computed } from 'vue';

interface MindmapNode {
  label: string;
  children?: MindmapNode[];
}

const props = defineProps<{
  node: MindmapNode;
  path: string;
  collapsed: Set<string>;
}>();

const emit = defineEmits<{
  toggle: [key: string];
}>();

const hasChildren = computed(() => (props.node.children?.length ?? 0) > 0);
const isCollapsed = computed(() => props.collapsed.has(props.path));
const depth = computed(() => props.path.split('/').length - 1);

function handleToggle() {
  emit('toggle', props.path);
}
</script>

<template>
  <div :class="['branch', `depth-${Math.min(depth, 3)}`]">
    <div :class="['branch-header', { leaf: !hasChildren }]" @click="hasChildren && handleToggle()">
      <span v-if="hasChildren" class="toggle-icon">{{ isCollapsed ? '+' : '−' }}</span>
      <span v-else class="dot"></span>
      <span class="branch-label">{{ node.label }}</span>
    </div>
    <div v-if="hasChildren && !isCollapsed" class="branch-children">
      <div v-for="(child, i) in node.children" :key="i" class="branch-child">
        <MindmapBranch
          :node="child"
          :path="`${path}/${child.label}`"
          :collapsed="collapsed"
          @toggle="(k: string) => emit('toggle', k)"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.branch {
  border-left: 2px solid var(--color-primary-border, #bfdbfe);
  margin-left: 12px;
  padding-left: 16px;
}

.branch.depth-1 {
  border-left-color: var(--color-primary, #2563eb);
  margin-left: 0;
  padding-left: 0;
}

.branch-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.15s;
  margin: 4px 0;
}

.branch-header:not(.leaf):hover {
  background: var(--color-primary-light, #eff6ff);
}

.branch-header.leaf {
  cursor: default;
  padding: 6px 12px;
}

.toggle-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  border-radius: 4px;
  background: var(--color-primary-light, #eff6ff);
  color: var(--color-primary, #2563eb);
  font-size: 14px;
  font-weight: 700;
  flex-shrink: 0;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-primary-border, #bfdbfe);
  flex-shrink: 0;
}

.branch-label {
  font-size: 0.9rem;
  color: var(--text-main, #0f172a);
  font-weight: 500;
}

.depth-1 > .branch-header .branch-label {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--color-primary-dark, #1d4ed8);
}

.branch-children {
  margin-top: 2px;
}
</style>
