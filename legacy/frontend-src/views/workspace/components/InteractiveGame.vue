<script setup lang="ts">
import { ref, computed } from 'vue';

const props = defineProps<{
  mode?: 'ai-games' | 'sandbox';
}>();

const activeGameIndex = ref(0);

const aiGames = [
  { id: 0, title: '视觉任务挑战赛', file: '/视觉任务挑战赛-课前.html', tag: '课前预热' },
  { id: 1, title: '模型训练模拟器', file: '/模型训练模拟器-课中.html', tag: '课中核心' },
  { id: 2, title: '食品识别体验', file: '/food-recognition-simple.html', tag: '课后拓展' },
];

const currentGame = computed(() => aiGames[activeGameIndex.value]);

const openActiveGameInNewWindow = () => {
  const game = aiGames[activeGameIndex.value];
  if (!game) return;
  window.open(game.file, '_blank', 'noopener,noreferrer');
};
</script>

<template>
  <div class="w-full h-full flex flex-col">

    <!-- AI Games Mode: 3 tabbed game iframes -->
    <div v-if="mode === 'ai-games'" class="flex-1 flex flex-col bg-gray-50 rounded-2xl shadow-sm border border-gray-100 overflow-hidden min-h-[700px]">
      <div class="flex border-b border-gray-200 bg-white px-2">
        <button
          v-for="(game, index) in aiGames"
          :key="game.id"
          @click="activeGameIndex = index"
          :class="activeGameIndex === index ? 'border-indigo-600 text-indigo-600 bg-indigo-50/30' : 'border-transparent text-gray-500 hover:text-gray-800 hover:bg-gray-50'"
          class="px-6 py-4 border-b-2 font-medium text-sm transition-all flex items-center gap-2 relative"
        >
          {{ game.title }}
          <span
            :class="activeGameIndex === index ? 'bg-indigo-100 text-indigo-700' : 'bg-gray-100 text-gray-500'"
            class="text-[10px] px-2 py-0.5 rounded-full transition-colors"
          >
            {{ game.tag }}
          </span>
        </button>

        <div class="ml-auto flex items-center pr-4">
          <button @click="openActiveGameInNewWindow" class="text-sm text-indigo-600 hover:text-indigo-800 flex items-center gap-1 font-medium">
            <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path></svg>
            独立窗口打开
          </button>
        </div>
      </div>

      <div class="flex-1 relative bg-white">
        <transition name="fade" mode="out-in">
          <iframe
            :key="activeGameIndex"
            :src="currentGame.file"
            class="absolute inset-0 w-full h-full border-0"
          ></iframe>
        </transition>
      </div>
    </div>

    <!-- 3D Physics Sandbox Mode -->
    <div v-else-if="mode === 'sandbox'" class="w-full h-full flex flex-col p-4 bg-gray-50/50">
      <div class="bg-white px-5 py-3 border border-gray-200 rounded-t-xl flex justify-between items-center shadow-sm z-10 relative">
        <div class="flex items-center gap-3">
          <div class="w-8 h-8 rounded bg-indigo-50 flex items-center justify-center text-indigo-600">
            <svg class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 10l-2 1m0 0l-2-1m2 1v2.5M20 7l-2 1m2-1l-2-1m2 1v2.5M14 4l-2-1-2 1M4 7l2-1M4 7l2 1M4 7v2.5M12 21l-2-1m2 1l2-1m-2 1v-2.5M6 18l-2-1v-2.5M18 18l2-1v-2.5"></path></svg>
          </div>
          <span class="text-[15px] font-bold text-gray-800 tracking-wide">3D 交互式物理引擎 (Three.js)</span>
        </div>
        <span class="bg-indigo-100 text-indigo-700 px-3 py-1 rounded-full text-xs font-bold uppercase flex items-center gap-1.5">
          <span class="w-2 h-2 rounded-full bg-indigo-500 animate-pulse"></span>
          Live Sandbox
        </span>
      </div>
      <div class="w-full flex-1 min-h-[650px] bg-[#111827] rounded-b-xl overflow-hidden border-x border-b border-gray-200 shadow-lg relative">
        <iframe src="/lorentz-3d.html" class="w-full h-full border-0" allow="fullscreen" title="3D 洛伦兹力交互仿真引擎"></iframe>
      </div>
    </div>

  </div>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
