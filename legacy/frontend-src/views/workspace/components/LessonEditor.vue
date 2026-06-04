<script setup lang="ts">
import { marked } from 'marked';
import markedKatex from 'marked-katex-extension';
import { computed, ref } from 'vue';
import { FileQuestion, Loader2, Trash2 } from 'lucide-vue-next';
import { apiClient } from '@/api/client';
import {
  isRegenerating,
  isLessonPlanRewriteActive,
  workspaceData,
  type WorkspaceLessonPlanData,
} from '@/composables/useWorkspaceState';

const props = defineProps<{
  isGenerating?: boolean;
  isGenerated?: boolean;
  isAiDemo?: boolean;
  projectName?: string;
}>();

const emit = defineEmits<{
  (e: 'generate-quiz'): void;
}>();

marked.use(markedKatex({ throwOnError: false }));
marked.use({ gfm: true, breaks: true });

const isGeneratingQuiz = ref(false);
const quizzes = ref<{ id: number; question: string; options: string[]; answer: number }[]>([]);

const shouldShowSharedLessonPlan = computed(() =>
  (props.isGenerated || isLessonPlanRewriteActive.value || isRegenerating.value)
);

const renderedContent = computed(() => {
  const content = workspaceData.value.content || '';
  if (!content.trim()) return '';
  return workspaceData.value.contentFormat === 'html'
    ? content
    : (marked.parse(content) as string);
});

const AI_DEMO_LESSON_HTML = `
<div class="max-w-4xl mx-auto bg-white p-10 rounded-2xl shadow-sm border border-gray-100">
  <h1 class="text-3xl font-extrabold text-gray-900 mb-6 pb-4 border-b">《人工智能应用基础》标准示范教案</h1>
  <div class="prose max-w-none text-gray-800">
    <div class="bg-indigo-50 text-indigo-700 p-4 rounded-lg mb-6 text-sm">
      <strong>适用年级：</strong> 高二/职高二年级 | <strong>预计课时：</strong> 45分钟 | <strong>核心素养：</strong> 计算思维、信息意识
    </div>
    <h3 class="text-xl font-bold mb-3 mt-6 text-indigo-900">一、 核心教学目标</h3>
    <ul class="list-disc pl-5 mb-4 space-y-2">
      <li><strong>知识与技能：</strong>理解人工智能的基本概念，掌握图像识别的基础逻辑。</li>
      <li><strong>过程与方法：</strong>通过"模型训练模拟器"实操，体验数据标注与模型生成的全过程。</li>
    </ul>
    <h3 class="text-xl font-bold mb-3 mt-6 text-indigo-900">二、 教学过程设计 (45分钟)</h3>
    <p class="mb-2"><strong>1. 情境导入 (5分钟)：</strong> 播放无人驾驶汽车避让行人的视频，提问"汽车是怎么'看'到人的？"</p>
    <p class="mb-2"><strong>2. 核心概念 (15分钟)：</strong> 讲解计算机视觉（CV）与监督学习的基本原理。</p>
    <p class="mb-2"><strong>3. 互动实操 (20分钟)：</strong> 学生使用系统内置的【食品识别体验】互动件，收集数据并训练分类器。</p>
  </div>
</div>`;

const generateQuiz = async () => {
  isGeneratingQuiz.value = true;
  try {
    const resp = await apiClient.post<{ question: string; options: string[]; answer: number }[]>('/api/avatar/generate-quiz', {
      session_id: `workspace-quiz-lesson-editor`,
      topic: workspaceData.value.content.slice(0, 300),
      count: 5,
    });
    quizzes.value = resp.data.map((q, i) => ({ id: i + 1, ...q }));
  } catch {
    emit('generate-quiz');
  } finally {
    isGeneratingQuiz.value = false;
  }
};

const deleteQuiz = (id: number) => {
  quizzes.value = quizzes.value.filter((q) => q.id !== id);
};
</script>

<template>
  <div class="w-full">
    <!-- State 1: AI Demo -->
    <div v-if="isAiDemo" class="flex-1 p-8 overflow-y-auto bg-gray-50" v-html="AI_DEMO_LESSON_HTML"></div>

    <!-- State 2: AI Generating -->
    <div v-else-if="isGenerating" class="flex flex-col items-center justify-center min-h-[500px] gap-5">
      <svg class="w-12 h-12 text-indigo-500 animate-spin" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <h3 class="text-lg font-medium text-gray-800">AI 正在为您深度解析资料...</h3>
      <p class="text-gray-400">即将生成专属教案框架</p>
      <div class="w-56 h-1.5 bg-indigo-100 rounded-full overflow-hidden">
        <div class="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full animate-[progress_1.5s_ease-out_forwards]"></div>
      </div>
    </div>

    <!-- State 3: Generated (momentum mock / rewritten) -->
    <div v-else-if="shouldShowSharedLessonPlan" class="p-10 relative">
      <div :class="{ 'blur-sm opacity-50': isRegenerating }" class="transition-all duration-500">
        <h1 class="text-3xl font-extrabold text-gray-900 mb-8 pb-4 border-b border-gray-100">
          {{ workspaceData.title }}
        </h1>
        <div class="prose prose-sm prose-indigo max-w-none math-render-area rendered-markdown rendered-document-markdown break-words" v-html="renderedContent"></div>
      </div>
      <!-- Regenerating overlay -->
      <div v-if="isRegenerating" class="absolute inset-0 z-10 flex flex-col items-center justify-center bg-white/70 backdrop-blur-sm rounded-2xl">
        <svg class="w-12 h-12 text-indigo-600 animate-spin mb-3" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span class="text-indigo-700 font-bold tracking-widest">AI 正在根据您的要求重写教案...</span>
      </div>
    </div>

    <!-- State 4: Normal lesson plan -->
    <div v-else class="relative max-w-4xl mx-auto">
      <!-- Floating Action Bar -->
      <div class="absolute -right-20 top-0 flex flex-col gap-4">
        <button
          @click="generateQuiz"
          class="w-14 h-14 bg-white rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.08)] flex items-center justify-center text-indigo-600 hover:bg-indigo-50 hover:scale-105 transition-all group relative"
        >
          <FileQuestion class="w-6 h-6" />
          <div class="absolute right-full mr-4 top-1/2 -translate-y-1/2 px-3 py-1.5 bg-gray-900 text-white text-xs font-bold rounded-lg opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
            根据当前内容自动出题
          </div>
        </button>
      </div>

      <div class="bg-white shadow-[0_2px_12px_rgba(0,0,0,0.04)] min-h-[800px] p-12 rounded-sm mb-8 min-w-0 overflow-hidden">
        <article class="prose prose-sm prose-indigo max-w-none min-w-0 break-words math-render-area prose-table:border-collapse prose-th:border prose-th:bg-gray-100 prose-th:px-3 prose-th:py-2 prose-td:border prose-td:p-2 prose-headings:font-bold prose-ul:list-disc prose-li:my-1 text-gray-700 rendered-markdown rendered-document-markdown" v-html="renderedContent"></article>
      </div>

      <!-- Quizzes -->
      <div v-if="isGeneratingQuiz" class="bg-white p-12 rounded-[32px] shadow-sm flex flex-col items-center justify-center gap-6 mb-8">
        <Loader2 class="w-10 h-10 text-indigo-600 animate-spin" />
        <div class="text-center space-y-2">
          <h3 class="text-xl font-black text-gray-900">AI 正在提取知识点...</h3>
          <p class="text-sm text-gray-400 font-medium">正在生成配套选择题</p>
        </div>
      </div>

      <div v-else-if="quizzes.length > 0" class="space-y-6 mb-8">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-indigo-50 rounded-xl flex items-center justify-center text-indigo-600">
            <FileQuestion class="w-5 h-5" />
          </div>
          <h3 class="text-2xl font-black text-gray-900">AI 生成随堂测验</h3>
        </div>
        <div class="grid grid-cols-1 gap-4">
          <div v-for="(quiz, index) in quizzes" :key="quiz.id" class="bg-white p-6 rounded-[24px] shadow-sm border border-gray-50 group relative">
            <div class="absolute top-6 right-6 opacity-0 group-hover:opacity-100 transition-opacity">
              <button @click="deleteQuiz(quiz.id)" class="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors">
                <Trash2 class="w-4 h-4" />
              </button>
            </div>
            <div class="space-y-4 pr-12">
              <h4 class="text-sm font-bold text-gray-900 leading-relaxed">
                <span class="text-indigo-600 mr-2">{{ index + 1 }}.</span>
                {{ quiz.question }}
              </h4>
              <div class="grid grid-cols-2 gap-3">
                <div
                  v-for="(opt, oIndex) in quiz.options"
                  :key="oIndex"
                  class="p-3 rounded-xl text-sm font-medium border transition-colors cursor-pointer"
                  :class="oIndex === quiz.answer ? 'bg-indigo-50 border-indigo-200 text-indigo-700' : 'bg-gray-50 border-transparent text-gray-600 hover:bg-gray-100'"
                >
                  <span class="mr-2">{{ String.fromCharCode(65 + oIndex) }}.</span>
                  {{ opt }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
