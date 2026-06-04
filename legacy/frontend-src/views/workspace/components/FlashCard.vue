<script setup lang="ts">
import { computed, ref } from 'vue';
import { marked } from 'marked';
import markedKatex from 'marked-katex-extension';

marked.use(markedKatex({ throwOnError: false }));
marked.use({ gfm: true, breaks: true });

const props = defineProps<{
  isAiDemo?: boolean;
}>();

const LORENTZ_FLASHCARDS: { q: string; a: string }[] = [
  { q: '洛伦兹力的定义是什么？', a: '运动电荷在磁场中所受到的力。它是安培力的微观本质。' },
  { q: '洛伦兹力的大小公式？', a: '$$F = qvB$$ (前提是 $v \\perp B$)' },
  { q: '如何判断洛伦兹力的方向？', a: '**左手定则**：磁感线穿心，四指指正电荷运动方向，大拇指指受力方向。' },
  { q: '洛伦兹力是否对电荷做功？', a: '**不做功**。因为力始终垂直于速度方向，只改变速度方向，不改变大小。' },
  { q: '带电粒子在磁场中做圆周运动的半径公式？', a: '$$r = \\frac{mv}{qB}$$' },
  { q: '带电粒子在磁场中圆周运动的周期公式？', a: '$$T = \\frac{2\\pi m}{qB}$$ (注意：周期与速度、半径均无关)' },
  { q: '回旋加速器利用了洛伦兹力的什么特性？', a: '利用磁场使粒子发生偏转，从而实现多次经过电场加速。' },
  { q: '极光的成因与洛伦兹力有关吗？', a: '有关。地球磁场通过洛伦兹力俘获太阳风中的高能粒子，使其向两极沉降。' },
];

const AI_DEMO_FLASHCARDS = [
  { q: '什么是计算机视觉 (CV)？', a: '让计算机像人类一样"看"懂图像和视频的技术，常用于人脸识别和自动驾驶。' },
  { q: '监督学习与无监督学习的核心区别？', a: '监督学习的训练数据带有"标签"（标准答案），而无监督学习的数据没有标签，靠算法自行发现规律。' },
  { q: '什么是"过拟合 (Overfitting)"？', a: '模型在训练数据上表现极好，但在没见过的新数据上表现很差，就像"死记硬背"的学生不会举一反三。' },
];

const flashcardData = computed(() => props.isAiDemo ? AI_DEMO_FLASHCARDS : LORENTZ_FLASHCARDS);
const currentCardIndex = ref(0);
const flashcardMasteredCount = ref(0);
const isFlashcardFlipped = ref(false);
const flashcardIsAnimating = ref(false);

const isAiDemoCardFlipped = ref(false);
const aiDemoCurrentCardIndex = ref(0);
const aiDemoCurrentFlashcard = computed(() =>
  AI_DEMO_FLASHCARDS[aiDemoCurrentCardIndex.value] || AI_DEMO_FLASHCARDS[0]
);

const renderFlashcardContent = (text: string) => marked.parse(text) as string;

const handleNextCard = (action: 'mastered' | 'review') => {
  if (flashcardIsAnimating.value) return;
  isFlashcardFlipped.value = false;
  flashcardIsAnimating.value = true;
  if (action === 'mastered') {
    flashcardMasteredCount.value += 1;
  }
  window.setTimeout(() => {
    currentCardIndex.value = (currentCardIndex.value + 1) % flashcardData.value.length;
    flashcardIsAnimating.value = false;
  }, 300);
};

const flipAiDemoCard = () => {
  isAiDemoCardFlipped.value = !isAiDemoCardFlipped.value;
};

const nextAiDemoCard = () => {
  if (aiDemoCurrentCardIndex.value < AI_DEMO_FLASHCARDS.length - 1) {
    aiDemoCurrentCardIndex.value += 1;
    isAiDemoCardFlipped.value = false;
  }
};
</script>

<template>
  <div class="w-full h-full flex flex-col items-center justify-center bg-[#F4F5F7] p-8 overflow-hidden relative">

    <!-- AI Demo Mode -->
    <template v-if="isAiDemo">
      <h2 class="text-2xl font-bold text-gray-800 mb-2">人工智能基础复习</h2>
      <div class="text-sm font-medium text-indigo-600 bg-indigo-100 px-3 py-1 rounded-full mb-8">
        PROGRESS : {{ aiDemoCurrentCardIndex + 1 }} / {{ AI_DEMO_FLASHCARDS.length }}
      </div>

      <div @click="flipAiDemoCard" class="w-full max-w-2xl h-80 perspective-1000 cursor-pointer relative group">
        <div :class="isAiDemoCardFlipped ? 'rotate-y-180' : ''" class="w-full h-full duration-500 preserve-3d relative transition-transform">
          <div class="absolute w-full h-full backface-hidden bg-white rounded-3xl shadow-md border border-gray-100 flex flex-col items-center justify-center p-10">
            <span class="absolute top-6 left-6 text-6xl text-gray-100 font-black">?</span>
            <h3 class="text-3xl font-bold text-gray-800 text-center">{{ aiDemoCurrentFlashcard?.q }}</h3>
            <p class="text-indigo-400 text-sm font-bold tracking-widest mt-10 uppercase group-hover:text-indigo-600 transition-colors">Click to reveal</p>
            <span class="text-indigo-400 mt-2">↓</span>
          </div>
          <div class="absolute w-full h-full backface-hidden bg-indigo-600 rounded-3xl shadow-md rotate-y-180 flex flex-col items-center justify-center p-10">
            <span class="absolute top-6 left-6 text-6xl text-white/10 font-black">!</span>
            <p class="text-2xl text-white font-medium text-center leading-relaxed">{{ aiDemoCurrentFlashcard?.a }}</p>
          </div>
        </div>
      </div>

      <div class="mt-10 flex gap-6" :class="isAiDemoCardFlipped ? 'opacity-100' : 'opacity-0 pointer-events-none'" style="transition: opacity 0.3s">
        <button @click="nextAiDemoCard" class="flex flex-col items-center gap-2 group">
          <div class="w-16 h-16 rounded-full bg-white shadow flex items-center justify-center text-red-500 group-hover:bg-red-50 transition-colors">
            <svg class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          </div>
          <span class="text-sm font-medium text-gray-500">待加强</span>
        </button>
        <button @click="nextAiDemoCard" class="flex flex-col items-center gap-2 group">
          <div class="w-16 h-16 rounded-full bg-white shadow flex items-center justify-center text-green-500 group-hover:bg-green-50 transition-colors">
            <svg class="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
          </div>
          <span class="text-sm font-medium text-gray-500">已掌握</span>
        </button>
      </div>
    </template>

    <!-- Normal Flashcard Mode -->
    <template v-else>
      <!-- 顶部光晕背景 -->
      <div class="absolute top-0 left-0 w-full h-64 bg-gradient-to-b from-indigo-100/50 to-transparent pointer-events-none"></div>

      <!-- 标题与进度胶囊 -->
      <div class="relative z-10 mb-8 text-center flex flex-col items-center">
        <h2 class="text-[28px] font-extrabold text-gray-800 tracking-tight mb-4">洛伦兹力专项复习</h2>
        <div class="bg-white/80 backdrop-blur-md px-5 py-2 rounded-full shadow-[0_2px_10px_rgb(0,0,0,0.06)] border border-gray-200/60 flex items-center gap-2">
          <span class="w-2.5 h-2.5 rounded-full bg-indigo-500 animate-pulse"></span>
          <span class="text-[13px] font-bold text-indigo-900 tracking-wider">PROGRESS : {{ currentCardIndex + 1 }} / {{ LORENTZ_FLASHCARDS.length }}</span>
        </div>
      </div>

      <!-- 3D 卡片舞台 -->
      <div
        class="relative z-10 w-full max-w-2xl h-[420px] [perspective:2000px] cursor-pointer group"
        @click="!flashcardIsAnimating && (isFlashcardFlipped = !isFlashcardFlipped)"
      >
        <div
          class="w-full h-full relative transition-[transform] duration-700 [transition-timing-function:cubic-bezier(0.23,1,0.32,1)] [transform-style:preserve-3d] rounded-3xl shadow-[0_20px_60px_rgba(0,0,0,0.05)] group-hover:shadow-[0_30px_70px_rgba(79,70,229,0.15)]"
          :class="{ '[transform:rotateY(180deg)]': isFlashcardFlipped }"
        >
          <!-- 正面：问题 -->
          <div class="absolute inset-0 w-full h-full [backface-visibility:hidden] bg-white rounded-3xl border border-gray-100 flex flex-col items-center justify-center p-12 text-center">
            <div class="absolute top-8 left-8 text-gray-100">
              <svg class="w-16 h-16" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17h-2v-2h2v2zm2.07-7.75l-.9.92C13.45 12.9 13 13.5 13 15h-2v-2.5c0-.55.22-1.05.59-1.42l1.2-1.2C13.1 9.5 13.3 9.1 13.3 8.5c0-1.38-1.12-2.5-2.5-2.5-1.38 0-2.5 1.12-2.5 2.5H6.5c0-2.48 2.02-4.5 4.5-4.5s4.5 2.02 4.5 4.5c0 1.1-.45 2.1-1.18 2.83z"/></svg>
            </div>
            <div
              class="text-[28px] font-bold text-gray-800 leading-snug z-10 rendered-markdown"
              v-html="renderFlashcardContent(LORENTZ_FLASHCARDS[currentCardIndex]?.q ?? '')"
            ></div>
            <div class="absolute bottom-8 flex flex-col items-center text-gray-300 group-hover:text-indigo-400 transition-colors duration-300">
              <span class="text-xs font-bold uppercase tracking-[0.2em] mb-2">Click to Reveal</span>
              <svg class="w-5 h-5 animate-bounce" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 15l-3 3m0 0l-3-3m3 3V9"></path></svg>
            </div>
          </div>

          <!-- 反面：解析 -->
          <div class="absolute inset-0 w-full h-full [backface-visibility:hidden] [transform:rotateY(180deg)] bg-gradient-to-br from-indigo-600 via-indigo-700 to-purple-800 rounded-3xl flex flex-col items-center justify-center p-12 text-center text-white">
            <div class="absolute top-8 right-8 text-white/10">
              <svg class="w-16 h-16" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg>
            </div>
            <div
              class="text-[22px] font-medium leading-relaxed rendered-markdown [&_strong]:font-black [&_.katex]:text-white [&_.katex-html]:text-white z-10"
              v-html="renderFlashcardContent(LORENTZ_FLASHCARDS[currentCardIndex]?.a ?? '')"
            ></div>
          </div>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="relative z-10 flex gap-12 mt-12">
        <div class="flex flex-col items-center gap-2">
          <button
            @click.stop="handleNextCard('review')"
            :disabled="flashcardIsAnimating"
            class="group relative w-16 h-16 rounded-full bg-white shadow-[0_8px_20px_rgb(0,0,0,0.06)] border border-gray-100 flex items-center justify-center hover:scale-110 hover:shadow-[0_12px_25px_rgba(244,63,94,0.2)] transition-all duration-300 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <div class="absolute inset-0 rounded-full bg-rose-50 opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <svg class="w-8 h-8 text-rose-500 relative z-10" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12"></path></svg>
          </button>
          <span class="text-[13px] font-bold text-gray-400">待加强</span>
        </div>

        <div class="flex flex-col items-center gap-2">
          <button
            @click.stop="handleNextCard('mastered')"
            :disabled="flashcardIsAnimating"
            class="group relative w-16 h-16 rounded-full bg-white shadow-[0_8px_20px_rgb(0,0,0,0.06)] border border-gray-100 flex items-center justify-center hover:scale-110 hover:shadow-[0_12px_25px_rgba(16,185,129,0.2)] transition-all duration-300 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <div class="absolute inset-0 rounded-full bg-emerald-50 opacity-0 group-hover:opacity-100 transition-opacity"></div>
            <svg class="w-8 h-8 text-emerald-500 relative z-10" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M5 13l4 4L19 7"></path></svg>
          </button>
          <span class="text-[13px] font-bold text-gray-400">已掌握</span>
        </div>
      </div>

      <!-- 掌握计数与重置 -->
      <div class="relative z-10 mt-8 flex items-center gap-4 text-xs text-gray-400">
        <span>已掌握 <strong class="text-emerald-600">{{ flashcardMasteredCount }}</strong> 张</span>
        <span class="text-gray-200">·</span>
        <button
          @click="currentCardIndex = 0; flashcardMasteredCount = 0; isFlashcardFlipped = false"
          class="hover:text-indigo-500 transition-colors font-medium"
        >↺ 重新开始</button>
      </div>
    </template>
  </div>
</template>

<style scoped>
.perspective-1000 {
  perspective: 1000px;
}

.preserve-3d {
  transform-style: preserve-3d;
}

.backface-hidden {
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
}

.rotate-y-180 {
  transform: rotateY(180deg);
}
</style>
