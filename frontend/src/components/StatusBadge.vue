<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps<{
  label: string;
  tone?: 'info' | 'success' | 'warning' | 'danger' | 'neutral' | 'purple';
}>();

const normalizedTone = computed(() => {
  if (props.tone) return props.tone;
  const text = props.label.toLowerCase();
  if (/失败|错误|异常|逾期|fail|error|danger/.test(text)) return 'danger';
  if (/待|审核|警告|提醒|warning|pending/.test(text)) return 'warning';
  if (/优秀|高分|管理员|purple/.test(text)) return 'purple';
  if (/未开始|草稿|停用|归档|neutral|draft/.test(text)) return 'neutral';
  if (/成功|完成|启用|正常|在线|pass|ready|success/.test(text)) return 'success';
  return 'info';
});
</script>

<template>
  <span :class="['status-badge', normalizedTone]">{{ label }}</span>
</template>
