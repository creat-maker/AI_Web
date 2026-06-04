<script setup lang="ts">
import { computed, ref } from 'vue';
import { 
  Sparkles, 
  User, 
  Paperclip, 
  Mic, 
  Send, 
  FileText, 
  Plus,
  Zap,
  CheckCircle2
} from 'lucide-vue-next';
import type { ChatMessage, CourseAnalysisData } from '../../types';
import { marked } from 'marked';

const props = defineProps<{
  title: string;
  chatMessages: ChatMessage[];
  activeTab: string;
  mode?: 'generator' | 'workspace';
  analysisData?: CourseAnalysisData;
  isLoadingAnalysis?: boolean;
  isSending?: boolean;
}>();

const emit = defineEmits<{
  (e: 'update:activeTab', tab: string): void;
  (e: 'send-message', content: string): void;
  (e: 'open-upload'): void;
  (e: 'action', action: string): void;
}>();

marked.use({
  gfm: true,
  breaks: true,
});

const fallbackAnalysisData: CourseAnalysisData = {
  difficulty: 72,
  knowledgePoints: [
    { name: '网络安全基础概念', coverage: 86 },
    { name: 'SQL 注入原理', coverage: 61 },
    { name: '输入校验与防护', coverage: 55 },
  ],
  suggestions: [
    '### 课堂推进建议\n- 先用生活化案例解释“输入框为什么会变成攻击入口”\n- 再用两段对比代码展示“拼接 SQL”和“预编译语句”的差异\n- 最后安排一次 5 分钟错因复盘，聚焦学生最容易混淆的执行链路',
    '### 教学板书建议\n| 模块 | 课堂目标 | 板书关键词 |\n| --- | --- | --- |\n| 输入校验 | 识别危险输入 | 长度、类型、白名单 |\n| SQL 注入 | 看懂越权执行路径 | 拼接、执行、回显 |\n| 防护策略 | 建立防御闭环 | 参数化、最小权限、日志 |',
    '### 练习分层建议\n- 基础层：判断哪些输入存在风险\n- 进阶层：分析一段存在漏洞的伪代码\n- 提升层：让学生口头复述完整攻击与防护路径',
  ],
  learning_condition: {
    summary: '高二3班学情预估：学生对网络安全基础概念易于接受，但对“SQL注入原理”等涉及代码逻辑的模块存在严重理解混淆。',
    painPoints: [
      {
        name: 'SQL注入代码执行逻辑',
        errorRate: 45,
        description: '学生往往只能记住“输入危险字符会出问题”，却无法清楚分辨用户输入、SQL 语句拼接和数据库执行这三个阶段的边界，因此一旦题目换成代码片段或流程图，就容易把“输入内容”和“执行指令”混为一谈。',
        strategy: '💡 破局策略：建议使用数据流向可视化工具，分步演示恶意代码是如何越权的。',
      },
    ],
  },
};

const resolvedAnalysisData = computed<CourseAnalysisData>(() => props.analysisData ?? fallbackAnalysisData);

const analysisSummaryText = computed(() => {
  const raw = resolvedAnalysisData.value.learning_condition?.summary?.trim() || '';
  if (!raw) {
    return '学生对网络安全基础概念易于接受，但对“SQL注入原理”等涉及代码逻辑的模块存在严重理解混淆。';
  }

  return raw
    .replace(/^基于虚构(?:的)?高二3班近10次测评数据(?:档案)?[：:，,\s]*/u, '')
    .replace(/^高二3班学情预估[：:，,\s]*/u, '')
    .trim();
});

const featuredPainPoint = computed(() => {
  const points = resolvedAnalysisData.value.learning_condition?.painPoints || [];
  return points[0] ?? fallbackAnalysisData.learning_condition!.painPoints[0];
});

const userInput = ref('');

const renderedMessages = computed(() => (
  props.chatMessages.map((msg) => ({
    ...msg,
    renderedContent: marked.parse(msg.content || '') as string,
  }))
));

const handleSend = () => {
  if (!userInput.value.trim()) return;
  emit('send-message', userInput.value);
  userInput.value = '';
};
</script>

<template>
  <aside class="w-96 min-w-0 flex-shrink-0 h-full bg-white shadow-[-4px_0_24px_rgba(0,0,0,0.02)] flex flex-col z-20">
    <!-- Sidebar Tabs -->
    <div class="p-6">
      <div class="flex bg-gray-50 p-1 rounded-2xl">
        <button 
          @click="emit('update:activeTab', 'chat')"
          class="flex-1 py-2.5 text-xs font-bold rounded-xl transition-all"
          :class="[activeTab === 'chat' ? 'bg-white shadow-sm text-gray-900' : 'text-gray-400 hover:text-gray-600']"
        >
          {{ mode === 'workspace' ? 'AI 伴写对话' : title + '伴写对话' }}
        </button>
        <button 
          @click="emit('update:activeTab', mode === 'workspace' ? 'analysis' : 'outline')"
          class="flex-1 py-2.5 text-xs font-bold rounded-xl transition-all"
          :class="[activeTab !== 'chat' ? 'bg-white shadow-sm text-gray-900' : 'text-gray-400 hover:text-gray-600']"
        >
          {{ mode === 'workspace' ? '教案深度分析' : '结构大纲' }}
        </button>
      </div>
    </div>

    <!-- Chat Area -->
    <div v-if="activeTab === 'chat'" class="flex-1 flex flex-col overflow-hidden">
      <div class="flex-1 overflow-y-auto p-6 space-y-8 custom-scrollbar">
        <div v-for="(msg, idx) in renderedMessages" :key="idx" :class="['flex gap-3', msg.role === 'user' ? 'flex-row-reverse' : '']">
          <div :class="['w-9 h-9 rounded-xl flex items-center justify-center flex-shrink-0 shadow-sm', msg.role === 'ai' ? 'bg-indigo-600 text-white' : 'bg-gray-100']">
            <Sparkles v-if="msg.role === 'ai'" class="w-5 h-5" />
            <User v-else class="w-5 h-5 text-gray-500" />
          </div>
          <div class="flex min-w-0 max-w-[85%] flex-col gap-2">
            <div :class="['min-w-0 overflow-hidden p-4 rounded-2xl text-sm leading-relaxed shadow-sm', msg.role === 'ai' ? 'bg-gray-50 text-gray-800 rounded-tl-none' : 'bg-indigo-600 text-white rounded-tr-none']">
              <div :class="['rendered-markdown rendered-chat-markdown break-words whitespace-pre-wrap', msg.role === 'user' ? 'rendered-markdown-inverse' : '']" v-html="msg.renderedContent"></div>
            </div>
            
            <!-- Preview Card (Workspace specific) -->
            <div v-if="msg.preview" class="p-4 bg-indigo-50/50 rounded-2xl border border-indigo-100 space-y-2">
              <div class="flex items-center gap-2">
                <Zap class="w-4 h-4 text-indigo-600" />
                <span class="text-xs font-bold text-indigo-900">{{ msg.preview.title }}</span>
              </div>
              <p class="text-[10px] text-indigo-700 leading-relaxed">{{ msg.preview.desc }}</p>
            </div>

            <!-- Attachment Card -->
            <div v-if="msg.attachment" class="p-3 bg-white rounded-2xl shadow-sm flex items-center gap-3 border border-gray-50">
              <div class="w-10 h-10 bg-indigo-50 rounded-xl flex items-center justify-center text-indigo-600">
                <FileText class="w-5 h-5" />
              </div>
              <div class="flex flex-col min-w-0">
                <span class="text-[10px] font-bold text-gray-900 truncate">{{ msg.attachment.name }}</span>
                <span class="text-[9px] text-gray-400">{{ msg.attachment.size }}</span>
              </div>
            </div>

            <span :class="['text-[10px] text-gray-400', msg.role === 'user' ? 'text-right' : '']">{{ msg.time }}</span>
          </div>
        </div>
      </div>

      <!-- Input Area -->
      <div class="p-6">
        <div class="flex items-center bg-gray-100/80 backdrop-blur-sm rounded-2xl px-4 py-2 shadow-sm">
          <button 
            @click="emit('open-upload')"
            class="p-1 text-gray-500 hover:text-indigo-600 transition-colors cursor-pointer"
          >
            <Paperclip class="w-5 h-5" />
          </button>
          <input 
            v-model="userInput"
            type="text"
            :placeholder="`输入关于${title}的修改指令...`" 
            @keyup.enter="handleSend"
            :disabled="props.isSending"
            class="flex-1 mx-3 bg-transparent border-none text-sm focus:ring-0 outline-none py-2"
          />
          <div class="flex items-center gap-3">
            <button @click="emit('action', '语音输入功能开发中')" class="p-1 text-gray-500 hover:text-indigo-600 transition-colors cursor-pointer">
              <Mic class="w-5 h-5" />
            </button>
            <button 
              @click="handleSend"
              :disabled="props.isSending"
              class="p-2 bg-indigo-600 text-white rounded-full hover:bg-indigo-700 transition-all shadow-md shadow-indigo-100 active:scale-95"
            >
              <Send class="w-4 h-4" :class="props.isSending ? 'opacity-60' : ''" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Outline Area (Generator Mode) -->
    <div v-else-if="mode !== 'workspace'" class="flex-1 overflow-y-auto p-8 space-y-8 custom-scrollbar">
      <div class="space-y-6">
        <div v-for="i in 4" :key="i" class="flex gap-4 group cursor-pointer">
          <div class="flex flex-col items-center">
            <div class="w-8 h-8 rounded-full bg-indigo-50 text-indigo-600 flex items-center justify-center text-xs font-black group-hover:bg-indigo-600 group-hover:text-white transition-colors">
              {{ i }}
            </div>
            <div v-if="i < 4" class="w-px h-full bg-gray-100 my-2"></div>
          </div>
          <div class="flex-1 pt-1 space-y-2">
            <h4 class="text-sm font-bold text-gray-900 group-hover:text-indigo-600 transition-colors">章节标题 {{ i }}</h4>
            <p class="text-[10px] text-gray-400 leading-relaxed">这里是该章节的核心内容概述，AI 将根据此大纲生成具体细节。</p>
          </div>
        </div>
      </div>
      <button @click="emit('action', '结构大纲编辑功能开发中')" class="w-full py-4 bg-gray-50 rounded-2xl text-xs font-bold text-gray-500 hover:bg-gray-100 transition-colors flex items-center justify-center gap-2">
        <Plus class="w-4 h-4" /> 添加新章节
      </button>
    </div>

    <!-- Analysis Area (Workspace Mode) -->
    <div v-else-if="isLoadingAnalysis" class="flex-1 overflow-y-auto p-8 space-y-10 custom-scrollbar">
      <!-- Skeleton: Difficulty -->
      <div class="space-y-4 animate-pulse">
        <div class="flex items-center justify-between">
          <div class="h-3.5 w-24 rounded-full bg-gray-200"></div>
          <div class="h-3.5 w-8 rounded-full bg-indigo-100"></div>
        </div>
        <div class="h-2 w-full rounded-full bg-gray-100">
          <div class="h-full w-3/4 rounded-full bg-gradient-to-r from-indigo-200 to-purple-200"></div>
        </div>
      </div>
      <!-- Skeleton: Knowledge Points -->
      <div class="space-y-6 animate-pulse">
        <div class="h-3.5 w-28 rounded-full bg-gray-200"></div>
        <div class="space-y-4">
          <div v-for="n in 3" :key="n" class="space-y-2">
            <div class="flex justify-between">
              <div class="h-2.5 rounded-full bg-gray-100" :style="{ width: ['60%', '50%', '45%'][n - 1] }"></div>
              <div class="h-2.5 w-6 rounded-full bg-gray-100"></div>
            </div>
            <div class="h-1 w-full rounded-full bg-gray-100"></div>
          </div>
        </div>
      </div>
      <!-- Skeleton: Learning Condition -->
      <div class="space-y-5 animate-pulse">
        <div class="h-3.5 w-36 rounded-full bg-orange-100"></div>
        <div class="rounded-2xl bg-orange-50/60 p-5 space-y-3">
          <div class="h-2.5 w-full rounded-full bg-orange-100"></div>
          <div class="h-2.5 w-4/5 rounded-full bg-orange-100"></div>
        </div>
        <div class="space-y-3">
          <div v-for="n in 2" :key="n" class="flex items-center gap-3">
            <div class="h-6 w-1/3 rounded-full bg-orange-100"></div>
            <div class="h-1.5 flex-1 rounded-full bg-orange-100">
              <div class="h-full rounded-full bg-orange-200" :style="{ width: ['45%', '38%'][n - 1] }"></div>
            </div>
          </div>
        </div>
      </div>
      <!-- Skeleton: Suggestions -->
      <div class="space-y-6 animate-pulse">
        <div class="h-3.5 w-24 rounded-full bg-gray-200"></div>
        <div class="space-y-3">
          <div v-for="n in 3" :key="n" class="flex gap-3 p-4 bg-gray-50 rounded-2xl">
            <div class="h-4 w-4 rounded-full bg-green-100 flex-shrink-0"></div>
            <div class="flex-1 space-y-2">
              <div class="h-2.5 w-full rounded bg-gray-100"></div>
              <div class="h-2.5 w-3/4 rounded bg-gray-100"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="flex-1 overflow-y-auto p-8 space-y-10 custom-scrollbar">
      <!-- Difficulty -->
      <div class="space-y-4">
        <div class="flex items-center justify-between">
          <h4 class="text-sm font-bold text-gray-900">课程难度评估</h4>
          <span class="text-xs font-black text-indigo-600">{{ resolvedAnalysisData.difficulty }}%</span>
        </div>
        <div class="h-2 w-full bg-gray-100 rounded-full overflow-hidden">
          <div class="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full" :style="{ width: resolvedAnalysisData.difficulty + '%' }"></div>
        </div>
        <p class="text-[10px] text-gray-400 leading-relaxed">基于知识点 density 与逻辑复杂度分析，当前教案难度适中，适合大部分学生。</p>
      </div>

      <!-- Knowledge Points -->
      <div class="space-y-6">
        <h4 class="text-sm font-bold text-gray-900">核心知识点覆盖率</h4>
        <div class="space-y-4">
          <div v-for="point in resolvedAnalysisData.knowledgePoints" :key="point.name" class="space-y-2">
            <div class="flex justify-between text-[10px] font-bold">
              <span class="text-gray-600">{{ point.name }}</span>
              <span class="text-gray-400">{{ point.coverage }}%</span>
            </div>
            <div class="h-1 w-full bg-gray-50 rounded-full overflow-hidden">
              <div class="h-full bg-indigo-600 rounded-full" :style="{ width: point.coverage + '%' }"></div>
            </div>
          </div>
        </div>
        <!-- Hardcoded Learning Condition Update requested by user -->
        <div class="mt-6">
          <h3 class="text-sm font-bold text-gray-800 mb-2">🎯 学情诊断与难点预警</h3>
          <div class="bg-orange-50 rounded-lg p-3 border border-orange-100">
            <p class="text-xs text-orange-800 mb-2">
              <span class="font-bold">班级学情预估：</span>{{ analysisSummaryText }}
            </p>
            <div class="space-y-2">
              <div class="flex items-start bg-white p-2 rounded shadow-sm">
                <div class="flex-1">
                  <div class="flex justify-between items-center">
                    <span class="text-sm font-medium text-red-600">{{ featuredPainPoint.name }}</span>
                    <span class="text-xs bg-red-100 text-red-600 px-1.5 py-0.5 rounded">预计错误率 {{ featuredPainPoint.errorRate }}%</span>
                  </div>
                  <p class="text-xs text-gray-600 mt-1" v-html="marked.parse(featuredPainPoint.strategy || '')"></p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Suggestions -->
      <div class="space-y-6">
        <h4 class="text-sm font-bold text-gray-900">AI 优化建议</h4>
        <div class="space-y-3">
          <div v-for="(suggestion, idx) in resolvedAnalysisData.suggestions" :key="idx" class="flex gap-3 p-4 bg-gray-50 rounded-2xl group hover:bg-white hover:shadow-md transition-all">
            <CheckCircle2 class="w-4 h-4 text-green-500 flex-shrink-0 mt-0.5" />
            <div class="prose prose-sm max-w-none prose-table:border-collapse prose-th:bg-gray-100 prose-th:border prose-td:border prose-td:p-2 prose-headings:font-bold prose-ul:list-disc prose-li:my-1 text-gray-700 min-w-0" v-html="marked.parse(suggestion || '')"></div>
          </div>
        </div>
      </div>
    </div>
  </aside>
</template>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: #e2e8f0;
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: #cbd5e1;
}
</style>
