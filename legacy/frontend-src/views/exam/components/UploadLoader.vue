<script setup lang="ts">
defineProps<{
  message?: string;
  subMessage?: string;
}>();
</script>

<template>
  <div class="flex-1 flex flex-col items-center justify-center bg-white rounded-2xl shadow-sm border border-gray-100 min-h-[600px]">
    <div class="relative w-20 h-20 mb-6 flex items-center justify-center">
      <svg class="w-16 h-16 text-indigo-100 absolute animate-spin" style="animation-duration: 3s;" fill="none" viewBox="0 0 24 24"><circle class="opacity-100" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"></circle></svg>
      <svg class="w-16 h-16 text-indigo-600 absolute animate-spin" style="animation-duration: 1s;" fill="none" viewBox="0 0 24 24"><path fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
    </div>
    <h3 class="text-xl font-bold text-gray-800">{{ message || '织课 AI 正在批阅学生答题卡...' }}</h3>
    <p class="text-gray-400 mt-2">{{ subMessage || '正在进行 OCR 识别与多维度学情诊断' }}</p>
  </div>
</template>
