<script setup lang="ts">
const props = defineProps<{
  isAiDemo?: boolean;
}>();

const handleDownloadRealPPT = () => {
  const link = document.createElement('a');
  link.href = '/物理之美：洛伦兹力的奥秘与应用.pptx';
  link.download = '物理之美：洛伦兹力的奥秘与应用.pptx';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

const handleDownloadAiPptDemo = () => {
  const link = document.createElement('a');
  link.href = '/老年餐饮智能辅助平台项目实战.pdf';
  link.download = '老年餐饮智能辅助平台项目实战.pdf';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};
</script>

<template>
  <div class="w-full h-full flex flex-col">

    <!-- AI Demo Mode -->
    <div v-if="isAiDemo" class="w-full h-full flex flex-col bg-gray-50 rounded-2xl overflow-hidden border border-gray-200">
      <div class="h-10 bg-white border-b border-gray-200 flex items-center justify-between px-4">
        <span class="text-sm font-medium text-gray-700">《人工智能应用基础 - 老年餐饮智能辅助平台》</span>
        <button @click="handleDownloadAiPptDemo" class="text-indigo-600 hover:text-indigo-800 text-sm flex items-center gap-1">
          <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
          导出 PPTX
        </button>
      </div>
      <iframe src="/老年餐饮智能辅助平台项目实战.pdf#toolbar=0" class="flex-1 w-full border-0" title="AI 生成演示文稿预览"></iframe>
    </div>

    <!-- Normal PPT View -->
    <div v-else class="w-full h-full flex flex-col items-center justify-start bg-gradient-to-br from-slate-100 via-gray-50 to-indigo-50 min-h-[600px] py-8 px-6">
      <!-- 顶部工具栏 -->
      <div class="w-full max-w-5xl flex justify-between items-center mb-5">
        <div class="flex items-center gap-2.5">
          <div class="w-7 h-7 rounded-lg bg-indigo-600 flex items-center justify-center">
            <span class="text-white text-xs font-black">P</span>
          </div>
          <span class="text-sm font-semibold text-gray-700">物理之美：洛伦兹力的奥秘与应用.pptx</span>
        </div>
        <button @click="handleDownloadRealPPT" class="text-sm bg-white text-indigo-600 hover:bg-indigo-50 border border-indigo-100 px-4 py-1.5 rounded-xl shadow-sm transition font-medium">
          ↓ 下载源文件
        </button>
      </div>
      <!-- 悬浮卡片容器 -->
      <div class="w-full max-w-5xl flex-1 rounded-3xl overflow-hidden shadow-[0_20px_60px_-10px_rgba(99,102,241,0.18),0_4px_16px_rgba(0,0,0,0.06)] bg-white" style="min-height:520px">
        <iframe
          src="/perfect-slides.pdf#toolbar=0&view=FitH"
          class="w-full h-full min-h-[520px] border-0"
        ></iframe>
      </div>
    </div>

  </div>
</template>
