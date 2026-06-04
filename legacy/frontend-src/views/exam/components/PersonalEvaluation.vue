<script setup lang="ts">
defineProps<{
  onBack: () => void;
  onExport: (action: string) => void;
}>();
</script>

<template>
  <div class="flex-1 bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden min-h-[800px] flex flex-col animate-in slide-in-from-right-4 duration-500">
    <div class="px-6 py-4 border-b border-gray-100 flex justify-between items-center bg-gray-50/50">
      <div class="flex items-center gap-3">
        <button @click="onBack" class="text-gray-500 hover:text-indigo-600 flex items-center gap-1 text-sm font-medium transition-colors">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
          返回大屏
        </button>
        <div class="h-4 w-px bg-gray-300"></div>
        <h2 class="text-base font-bold text-gray-800">AI 专属学情评价报告</h2>
      </div>
      <button @click="onExport('导出 PDF')" class="bg-indigo-50 text-indigo-600 px-4 py-1.5 rounded-lg text-sm font-medium hover:bg-indigo-100">导出 PDF</button>
    </div>
    <iframe src="/评价.html" class="w-full flex-1 border-0 bg-gray-50"></iframe>
  </div>
</template>
