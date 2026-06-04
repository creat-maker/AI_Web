<script setup lang="ts">
import { marked } from 'marked';
import markedKatex from 'marked-katex-extension';
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { apiClient } from '../api/client';
import {
  buildGeneratedEntryFromRaw,
  buildPromptOnlyGenerationPrompt,
  renderMarkdown,
  resolveGameCards,
  resolveMarkdownSource,
  resolvePptSlides,
  resolveVideoScenes,
} from '../utils/content';
import {
  LORENTZ_DEMO_ANIMATION_HTML,
  LORENTZ_DEMO_STAGE_MESSAGES,
  buildLorentzDemoLessonPlanEntry,
  buildLorentzDemoPptEntry,
  getLorentzDemoDelayMs,
  isLorentzDemoTarget,
  waitForLorentzDemoDelay,
} from '../utils/lorentzDemo';
import PhysicsAnimation from './PhysicsAnimation.vue';
import {
  ChevronRight,
  ChevronLeft,
  RotateCw,
  Check,
  Layout,
  Play,
  FileText,
  Smartphone,
  Zap,
  MoreHorizontal,
  X,
  CloudUpload,
  CheckCircle2,
  Loader2,
} from 'lucide-vue-next';
import type {
  AttachmentRecord,
  ChatHistoryRecord,
  ChatMessage,
  GeneratedContentEntry,
  GeneratorComposeResponse,
  ProjectDetail,
  StagedAttachmentRecord,
} from '../types';

interface Props {
  type: 'ppt' | 'lesson-plan' | 'video' | 'game' | 'blog';
  projectId?: number | null;
  generationRequirement?: string;
  autoGenerateToken?: number;
}

const props = defineProps<Props>();
const showUploadModal = ref(false);
const uploadInput = ref<HTMLInputElement | null>(null);
const uploadedReferences = ref<string[]>([]);
const selectedUploadName = ref('');
const isUploadingReference = ref(false);
const isGeneratingContent = ref(false);
const generationProgress = ref(0);
const generationStatus = ref('');
const generationRequirementInput = ref(props.generationRequirement || '');
const projectDetail = ref<ProjectDetail | null>(null);
const lastAutoGenerateKey = ref('');
const standaloneEntry = ref<GeneratedContentEntry | null>(null);
const showLorentzAnimation = ref(false);
const lorentzAnimationHtml = ref('');

const generatorConfig = {
  ppt: { name: 'PPT', format: 'PPTX', icon: Layout },
  'lesson-plan': { name: '教案', format: 'Word', icon: FileText },
  video: { name: '视频', format: 'MP4', icon: Play },
  game: { name: '互动小游戏', format: 'H5包', icon: Smartphone },
  blog: { name: '博客', format: 'Markdown', icon: FileText },
};

marked.use({
  gfm: true,
  breaks: true,
});
marked.use(markedKatex({ throwOnError: false }));

const config = computed(() => generatorConfig[props.type]);
const currentEntry = computed(() => projectDetail.value?.contents?.[props.type] ?? standaloneEntry.value);
const parsedSlides = computed(() => resolvePptSlides(currentEntry.value));
const lessonPlanMarkdown = computed(() => resolveMarkdownSource(currentEntry.value));
const lessonPlanHtml = computed(() => marked.parse(lessonPlanMarkdown.value || '') as string);
const videoScenes = computed(() => resolveVideoScenes(currentEntry.value));
const gameCards = computed(() => resolveGameCards(currentEntry.value));
const blogMarkdown = computed(() => resolveMarkdownSource(currentEntry.value));
const blogHtml = computed(() => renderMarkdown(blogMarkdown.value));

const activeSidebarTab = ref('chat');

const chatMessages = ref<ChatMessage[]>([
  {
    role: 'ai',
    content: `欢迎使用${config.value.name}生成器！请上传参考资料或输入要求，我会先读取资料，再为您生成可直接使用的内容。`,
    time: '刚刚',
  },
]);

const isSending = ref(false);
const showToast = ref(false);
const toastMessage = ref('');

const showToastMessage = (msg: string) => {
  toastMessage.value = msg;
  showToast.value = true;
  window.setTimeout(() => { showToast.value = false; }, 3000);
};

const hasUserRequirement = computed(() => Boolean(generationRequirementInput.value.trim() || props.generationRequirement?.trim()));
const hasUploadedContext = computed(() => Boolean((projectDetail.value?.attachments?.length ?? 0) > 0 || uploadedReferences.value.length > 0));
const isLorentzDemoProject = computed(() => isLorentzDemoTarget({ projectName: projectDetail.value?.name }));
const canRequestGeneration = computed(() => isLorentzDemoProject.value || hasUserRequirement.value || hasUploadedContext.value);

const openUploadModal = () => {
  showUploadModal.value = true;
};

const closeUploadModal = () => {
  showUploadModal.value = false;
};

const triggerReferenceUpload = () => {
  uploadInput.value?.click();
};

const syncProjectState = (detail: ProjectDetail) => {
  projectDetail.value = detail;
  uploadedReferences.value = (detail.attachments || []).map((item) => item.original_name).slice(0, 5);
  if (!isLorentzDemoTarget({ projectName: detail.name })) {
    showLorentzAnimation.value = false;
    lorentzAnimationHtml.value = '';
  }
};

const loadProjectDetail = async () => {
  if (!props.projectId) {
    projectDetail.value = null;
    uploadedReferences.value = [];
    return;
  }
  try {
    const response = await apiClient.get<ProjectDetail>(`/api/projects/${props.projectId}`);
    syncProjectState(response.data);
  } catch {
    showToastMessage('加载项目资料失败');
  }
};

const currentRequirement = () => generationRequirementInput.value.trim() || props.generationRequirement?.trim() || projectDetail.value?.description || `请生成一份高质量${config.value.name}初稿`;

const requestGeneration = async () => {

  const attachmentIds = (projectDetail.value?.attachments || []).map((item) => item.id);
  const sourceFiles = (projectDetail.value?.attachments || []).map((item) => item.original_name);
  const requirement = currentRequirement();
  const hasProjectAttachments = props.projectId && attachmentIds.length > 0;
  const currentProjectName = projectDetail.value?.name || '';
  const resolvedSourceFiles = sourceFiles.length > 0 ? sourceFiles : uploadedReferences.value;
  const demoModeActive = isLorentzDemoTarget({
    projectName: currentProjectName,
  });
  const demoContext = {
    projectName: currentProjectName,
    fileNames: resolvedSourceFiles,
    attachmentIds,
    sourceFiles: resolvedSourceFiles,
    userRequirement: requirement,
  };

  isGeneratingContent.value = true;
  if (demoModeActive && (props.type === 'lesson-plan' || props.type === 'ppt')) {
    let statusTimer: number | undefined;
    try {
      const totalDelay = getLorentzDemoDelayMs();
      let stageIndex = 0;

      generationProgress.value = 12;
      generationStatus.value = LORENTZ_DEMO_STAGE_MESSAGES[stageIndex];
      statusTimer = window.setInterval(() => {
        stageIndex = (stageIndex + 1) % LORENTZ_DEMO_STAGE_MESSAGES.length;
        generationStatus.value = LORENTZ_DEMO_STAGE_MESSAGES[stageIndex];
        generationProgress.value = Math.min(generationProgress.value + 18, 90);
      }, 1000);

      await waitForLorentzDemoDelay(totalDelay);

      const generatedEntry = props.type === 'lesson-plan'
        ? buildLorentzDemoLessonPlanEntry(demoContext)
        : buildLorentzDemoPptEntry(demoContext);

      generationProgress.value = 100;
      showLorentzAnimation.value = true;
      lorentzAnimationHtml.value = LORENTZ_DEMO_ANIMATION_HTML;
      if (projectDetail.value) {
        projectDetail.value = {
          ...projectDetail.value,
          contents: {
            ...(projectDetail.value.contents || {}),
            [props.type]: generatedEntry,
          },
        };
      } else {
        standaloneEntry.value = generatedEntry;
      }
      showToastMessage(`${config.value.name} 已生成完成`);
      window.dispatchEvent(new CustomEvent('ai-generation-complete', {
        detail: {
          toolLabel: config.value.name,
          projectName: projectDetail.value?.name || '洛伦兹力',
        },
      }));
      return;
    } catch (error) {
      showToastMessage(error instanceof Error ? error.message : '生成失败，请稍后重试');
    } finally {
      if (statusTimer) {
        window.clearInterval(statusTimer);
      }
      window.setTimeout(() => {
        isGeneratingContent.value = false;
        generationProgress.value = 0;
        generationStatus.value = '';
      }, 300);
    }
  }

  showLorentzAnimation.value = false;
  lorentzAnimationHtml.value = '';
  generationStatus.value = '正在深度分析文档并撰写初稿...';
  generationProgress.value = 10;
  const timer = window.setInterval(() => {
    generationProgress.value = Math.min(generationProgress.value + 8, 88);
  }, 320);

  try {
    const generatedEntry = await (async () => {
      if (hasProjectAttachments) {
        const response = await apiClient.post<GeneratorComposeResponse>('/api/generator/compose', {
          project_id: props.projectId,
          attachment_ids: attachmentIds,
          generator_type: props.type,
          user_requirement: requirement,
          session_id: `generator-${props.type}-${props.projectId}`,
        });
        showLorentzAnimation.value = Boolean(response.data.animation_html) && (props.type === 'lesson-plan' || props.type === 'ppt');
        lorentzAnimationHtml.value = response.data.animation_html || '';
        return response.data.content;
      }

      const response = await apiClient.post<string>('/api/avatar/generate', {
        session_id: `generator-${props.type}-${props.projectId || 'prompt-only'}`,
        prompt: buildPromptOnlyGenerationPrompt(props.type, requirement, projectDetail.value?.name),
        generator_type: props.type,
      });
      return buildGeneratedEntryFromRaw(
        props.type,
        typeof response.data === 'string' ? response.data : '',
        requirement,
        attachmentIds,
        uploadedReferences.value,
      );
    })();

    generationProgress.value = 100;
    if (projectDetail.value) {
      projectDetail.value = {
        ...projectDetail.value,
        contents: {
          ...(projectDetail.value.contents || {}),
          [props.type]: generatedEntry,
        },
      };
    } else {
      standaloneEntry.value = generatedEntry;
    }
    showToastMessage(`${config.value.name} 已生成完成`);
    // 通知右侧伴写助手：生成完成，推送引导话术
    window.dispatchEvent(new CustomEvent('ai-generation-complete', {
      detail: {
        toolLabel: config.value.name,
        projectName: projectDetail.value?.name || '当前课程',
      },
    }));
  } catch (error) {
    showToastMessage(error instanceof Error ? error.message : '生成失败，请稍后重试');
  } finally {
    window.clearInterval(timer);
    window.setTimeout(() => {
      isGeneratingContent.value = false;
      generationProgress.value = 0;
      generationStatus.value = '';
    }, 300);
  }
};

const maybeAutoGenerate = async () => {
  if (!props.projectId || !props.autoGenerateToken || !projectDetail.value) {
    return;
  }
  const autoKey = `${props.projectId}-${props.type}-${props.autoGenerateToken}`;
  if (lastAutoGenerateKey.value === autoKey || currentEntry.value) {
    return;
  }
  if ((projectDetail.value.attachments || []).length === 0) {
    return;
  }
  lastAutoGenerateKey.value = autoKey;
  await requestGeneration();
};

const handleReferenceFileChange = async (event: Event) => {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  if (!file) {
    return;
  }

  selectedUploadName.value = file.name;
  isUploadingReference.value = true;
  try {
    const formData = new FormData();
    formData.append('file', file);
    const uploadPath = props.projectId ? `/api/attachments/upload?project_id=${props.projectId}` : '/api/attachments/upload';
    await apiClient.postForm<AttachmentRecord | StagedAttachmentRecord>(uploadPath, formData);
    await loadProjectDetail();
    showToastMessage(props.projectId ? '参考资料已上传到当前项目' : '参考资料已暂存，创建项目后可继续绑定');
  } catch {
    showToastMessage('上传失败，请稍后重试');
  } finally {
    isUploadingReference.value = false;
    input.value = '';
  }
};

const confirmUpload = async () => {
  if (!selectedUploadName.value) {
    showToastMessage('请先选择文件');
    return;
  }
  closeUploadModal();
  if (props.projectId) {
    await requestGeneration();
  }
};

const handlePreviewAction = (label: string) => {
  showToastMessage(`${label}功能开发中`);
};

const handleSendMessage = async (content: string) => {
  chatMessages.value.push({ role: 'user', content, time: '刚刚' });
  isSending.value = true;
  try {
    const resp = await apiClient.post<string>('/api/avatar/chat', {
      session_id: `generator-${props.type}-${props.projectId || 'global'}`,
      text: content,
    });
    chatMessages.value.push({ role: 'ai', content: resp.data, time: '刚刚' });
  } catch {
    chatMessages.value.push({ role: 'ai', content: '抱歉，服务暂时不可用，请稍后重试。', time: '刚刚' });
  } finally {
    isSending.value = false;
  }
};

const handleExport = async () => {
  showToastMessage(`正在导出 ${config.value.format} 文件...`);
  try {
    await apiClient.post('/api/avatar/generate', {
      session_id: `export-${props.type}-${props.projectId || 'global'}`,
      prompt: `导出当前${config.value.name}内容为 ${config.value.format} 格式。内容摘要：${(currentEntry.value?.raw_content || currentRequirement()).slice(0, 500)}`,
      generator_type: 'export',
    });
    showToastMessage(`${config.value.format} 导出任务已创建`);
  } catch {
    showToastMessage('导出失败，请稍后重试');
  }
};

const loadChatHistory = async () => {
  const sid = `generator-${props.type}-${props.projectId || 'global'}`;
  try {
    const resp = await apiClient.get<ChatHistoryRecord[]>(`/api/avatar/chat-history/${sid}`);
    if (Array.isArray(resp.data) && resp.data.length > 0) {
      const mapped = resp.data.map((record: ChatHistoryRecord) => ({
        role: (record.role === 'assistant' ? 'ai' : 'user') as 'ai' | 'user',
        content: record.content,
        time: new Date(record.created_at).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }),
      }));
      chatMessages.value = [chatMessages.value[0], ...mapped];
    }
  } catch {
    // keep welcome message
  }
};

watch(
  () => props.generationRequirement,
  (value) => {
    if (value && !generationRequirementInput.value) {
      generationRequirementInput.value = value;
    }
  },
  { immediate: true },
);

watch(
  () => props.projectId,
  async () => {
    if (props.projectId) {
      standaloneEntry.value = null;
    }
    await loadProjectDetail();
    await maybeAutoGenerate();
  },
  { immediate: true },
);

watch(
  () => props.autoGenerateToken,
  () => {
    void maybeAutoGenerate();
  },
);

watch(
  () => props.type,
  () => {
    standaloneEntry.value = null;
    chatMessages.value = [
      {
        role: 'ai',
        content: `欢迎使用${config.value.name}生成器！请上传参考资料或输入要求，我会先读取资料，再为您生成可直接使用的内容。`,
        time: '刚刚',
      },
    ];
    void loadChatHistory();
    void maybeAutoGenerate();
  },
);

onMounted(() => {
  window.addEventListener('generator-open-upload', openUploadModal);
  void loadChatHistory();
});

onBeforeUnmount(() => {
  window.removeEventListener('generator-open-upload', openUploadModal);
});

const isSidebarCollapsed = ref(false);
const menuItems = [
  { id: 'home', name: '首页', icon: Layout },
  { id: 'knowledge', name: '知识库', icon: FileText },
  { id: 'workspace', name: '工作台', icon: Layout },
];
</script>

<template>
  <div class="flex-1 min-w-0 h-full flex flex-col overflow-y-auto custom-scrollbar">
      <!-- Top Bar -->
      <div class="flex-shrink-0 h-16 flex items-center justify-between px-8 bg-white shadow-sm z-10">
        <span class="text-gray-500 text-sm">首页 > 生成{{ config.name }}</span>
        <div class="flex items-center gap-3">
          <button @click="openUploadModal" class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm hover:bg-gray-200 transition-colors">上传参考资料</button>
          <button @click="requestGeneration" :disabled="isGeneratingContent || !canRequestGeneration" class="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed">立即生成</button>
          <button 
            @click="handleExport"
            class="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm hover:bg-blue-700 transition-colors"
          >
            导出 {{ config.format }}
          </button>
        </div>
      </div>

      <!-- Content Area (Immersive, Left-Aligned, Wide) -->
      <div class="flex-1 w-full p-12 flex items-start">
        <div class="w-full min-w-0 max-w-7xl bg-white rounded-2xl shadow-[0_4px_20px_rgba(0,0,0,0.04)] p-8 flex flex-col gap-6 transition-all duration-300 overflow-hidden">
          <div class="rounded-[28px] border border-gray-100 bg-gray-50/70 p-5 space-y-4">
            <div class="flex items-center justify-between gap-4">
              <div>
                <h3 class="text-sm font-black text-gray-900">生成要求</h3>
                <p class="text-xs text-gray-500 mt-1">输入要求或上传参考资料，AI 将自动生成</p>
              </div>
              <div class="text-xs font-bold text-gray-400">已绑定资料 {{ uploadedReferences.length }} 份</div>
            </div>
            <textarea v-model="generationRequirementInput" rows="3" class="w-full rounded-2xl border border-gray-200 bg-white px-4 py-3 text-sm outline-none focus:ring-2 focus:ring-indigo-500/20" placeholder="输入要求或上传参考资料，AI 将自动生成"></textarea>
          </div>

          <div v-if="isGeneratingContent" class="rounded-[28px] bg-indigo-50 border border-indigo-100 px-6 py-5">
            <div class="flex items-center gap-3 mb-3">
              <Loader2 class="w-5 h-5 text-indigo-600 animate-spin" />
              <span class="text-sm font-black text-gray-900">{{ generationStatus || '正在深度分析文档并撰写初稿...' }}</span>
            </div>
            <div class="flex items-center justify-between text-xs font-bold text-gray-500 mb-2">
              <span>文件读取 -> 文本提取 -> 结构化生成</span>
              <span>{{ generationProgress }}%</span>
            </div>
            <div class="h-3 rounded-full bg-white/80 overflow-hidden">
              <div class="h-full bg-gradient-to-r from-indigo-600 to-blue-500 transition-all duration-300" :style="{ width: generationProgress + '%' }"></div>
            </div>
          </div>

          <div v-if="!currentEntry && !isGeneratingContent" class="min-h-[480px] rounded-[32px] border-2 border-dashed border-gray-200 bg-gray-50/40 flex flex-col items-center justify-center text-center px-10">
            <div class="w-20 h-20 rounded-3xl bg-white shadow-sm flex items-center justify-center text-indigo-600 mb-6">
              <component :is="config.icon" class="w-10 h-10" />
            </div>
            <h2 class="text-2xl font-black text-gray-900 mb-2">当前还没有生成好的 {{ config.name }}</h2>
            <p class="text-sm text-gray-500 max-w-xl leading-7">输入要求或上传资料后点击“立即生成”，系统会自动生成真实初稿，并回填到当前预览区。</p>
          </div>
          
          <!-- Game Preview (Desktop Gamified) -->
          <template v-else-if="type === 'game'">
            <div class="flex justify-between items-center border-b border-gray-50 pb-4">
              <h2 class="text-xl font-bold text-gray-800">{{ config.name }} 知识记忆卡</h2>
              <span class="px-3 py-1 bg-green-50 text-green-600 rounded-full text-sm">已生成 {{ gameCards.length }} 张卡片</span>
            </div>
            
            <div class="grid grid-cols-3 gap-6 py-8">
              <div v-for="(card, index) in gameCards.slice(0, 3)" :key="index" class="aspect-[3/4] rounded-2xl transition-transform cursor-pointer p-6" :class="index % 2 === 1 ? 'bg-blue-50/50 shadow-sm border border-blue-100 flex flex-col' : 'bg-white shadow-sm border border-gray-100 hover:-translate-y-1 relative flex items-center justify-center group'">
                <template v-if="index % 2 === 1">
                  <span class="text-sm text-blue-400 mb-2 font-bold">知识解释</span>
                  <p class="text-gray-700 leading-relaxed text-sm">{{ card.back }}</p>
                </template>
                <template v-else>
                  <h3 class="text-2xl font-bold text-gray-800 text-center">{{ card.front }}</h3>
                  <RotateCw class="w-4 h-4 text-gray-400 absolute bottom-4 right-4 group-hover:text-blue-600 transition-colors" />
                </template>
              </div>
            </div>

            <div class="flex justify-center items-center gap-6 pt-4 border-t border-gray-50">
              <button @click="handlePreviewAction('上一张卡片切换')" class="p-2 rounded-full hover:bg-gray-100 transition-colors">
                <ChevronLeft class="w-6 h-6 text-gray-500" />
              </button>
              <button @click="handlePreviewAction('卡片掌握标记')" class="flex items-center px-6 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors font-medium shadow-lg shadow-blue-100">
                <Check class="w-5 h-5 mr-2" /> 标记为已掌握
              </button>
              <button @click="handlePreviewAction('下一张卡片切换')" class="p-2 rounded-full hover:bg-gray-100 transition-colors">
                <ChevronRight class="w-6 h-6 text-gray-500" />
              </button>
            </div>
          </template>

          <!-- PPT Preview – PDF 原生预览 -->
          <div v-else-if="type === 'ppt'" class="w-full h-full flex flex-col bg-gray-50/50 rounded-xl overflow-hidden border border-gray-200">
            <div class="flex justify-between items-center px-4 py-3 bg-white border-b border-gray-200">
              <div class="flex items-center gap-2">
                <span class="text-indigo-600 font-bold text-lg">P</span>
                <span class="text-sm font-medium text-gray-800">物理之美：洛伦兹力的奥秘与应用.pptx</span>
                <span class="bg-indigo-50 text-indigo-600 px-2 py-0.5 rounded text-xs ml-2">原生课件预览</span>
              </div>
              <button @click="handleExport" class="text-sm bg-indigo-600 text-white hover:bg-indigo-700 px-4 py-1.5 rounded-lg transition shadow-sm">
                下载源文件
              </button>
            </div>
            <div class="flex-1 w-full p-2 h-[600px] min-h-[60vh]">
              <iframe
                src="/perfect-slides.pdf#toolbar=0&view=FitH"
                class="w-full h-full rounded-lg shadow-sm border border-gray-200 bg-white"
              ></iframe>
            </div>
          </div>

          <!-- Word Lesson Plan Preview (A4 Style) -->
          <div v-else-if="type === 'lesson-plan'" class="w-full max-w-4xl mx-auto space-y-6">
            <PhysicsAnimation v-if="showLorentzAnimation" :animation-html="lorentzAnimationHtml" />
            <div class="bg-white shadow-sm p-12 min-h-[800px] rounded-sm border border-gray-100 min-w-0 overflow-hidden">
              <article class="prose prose-sm prose-indigo max-w-none min-w-0 break-words prose-table:border-collapse prose-th:border prose-th:bg-gray-100 prose-th:px-3 prose-th:py-2 prose-td:border prose-td:p-2 prose-headings:font-bold prose-ul:list-disc prose-li:my-1 text-gray-700" v-html="lessonPlanHtml"></article>
            </div>
          </div>

          <!-- Video Preview -->
          <div v-else-if="type === 'video'" class="w-full">
            <div class="aspect-video bg-slate-950 rounded-[40px] shadow-2xl relative overflow-hidden p-10 flex flex-col justify-end">
              <div class="max-w-2xl text-white space-y-4">
                <span class="inline-flex px-3 py-1 bg-white/10 rounded-full text-xs font-bold">AI 分镜脚本</span>
                <h2 class="text-3xl font-black">{{ videoScenes[0]?.title || '视频初稿' }}</h2>
                <p class="text-sm leading-7 text-white/80">{{ videoScenes[0]?.narration || '系统会根据资料生成视频分镜与旁白。' }}</p>
              </div>
            </div>
            <div class="mt-8 flex gap-4 overflow-x-auto pb-4 custom-scrollbar">
              <div v-for="(scene, index) in videoScenes" :key="index" class="w-56 aspect-video bg-gray-50 rounded-2xl flex-shrink-0 p-4 flex flex-col justify-between relative overflow-hidden group cursor-pointer shadow-sm border border-gray-100">
                <span class="relative text-[10px] font-bold text-gray-400">SCENE {{ String(index + 1).padStart(2, '0') }}</span>
                <div>
                  <h4 class="text-sm font-black text-gray-900 mb-2">{{ scene.title }}</h4>
                  <p class="text-xs text-gray-500 leading-6">{{ scene.visuals.join('；') || scene.narration }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Blog Preview -->
          <div v-else-if="type === 'blog'" class="w-full space-y-12">
            <div class="space-y-6">
              <div class="flex items-center gap-3">
                <span class="px-3 py-1 bg-indigo-50 text-indigo-600 text-[10px] font-bold rounded-full uppercase tracking-widest">文档深度改写</span>
                <span class="text-xs text-gray-400 font-medium">根据上传资料生成</span>
              </div>
              <h1 class="text-4xl font-black text-gray-900 leading-tight">{{ projectDetail?.name || '教学博客初稿' }}</h1>
            </div>
            <article class="bg-white rounded-[32px] shadow-sm p-10 rendered-markdown rendered-document-markdown break-words whitespace-pre-wrap max-w-full min-w-0 overflow-hidden" v-html="blogHtml"></article>
          </div>

        </div>
      </div>
    </div>

    <!-- Upload Modal -->
    <Transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="showUploadModal" class="fixed inset-0 z-50 flex items-center justify-center p-6">
        <!-- Backdrop -->
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="showUploadModal = false"></div>
        
        <!-- Modal Card -->
        <div class="relative bg-white w-full max-w-[480px] rounded-[32px] shadow-2xl overflow-hidden flex flex-col animate-in fade-in zoom-in duration-300">
          <!-- Header -->
          <div class="px-8 py-6 flex items-center justify-between border-b border-gray-50">
            <h3 class="text-xl font-black text-gray-900">上传参考资料</h3>
            <button @click="showUploadModal = false" class="p-2 hover:bg-gray-50 rounded-xl text-gray-400 hover:text-gray-900 transition-all">
              <X class="w-5 h-5" />
            </button>
          </div>
          
          <!-- Body -->
          <div class="p-8 space-y-6">
            <input ref="uploadInput" type="file" class="hidden" @change="handleReferenceFileChange" />
            <div @click="triggerReferenceUpload" class="bg-gray-50 border-2 border-dashed border-gray-200 rounded-[24px] p-12 flex flex-col items-center justify-center gap-4 group hover:border-indigo-300 hover:bg-indigo-50/30 transition-all cursor-pointer">
              <div class="w-16 h-16 bg-white rounded-2xl flex items-center justify-center text-gray-400 group-hover:text-indigo-600 group-hover:scale-110 transition-all shadow-sm">
                <CloudUpload class="w-8 h-8" />
              </div>
              <div class="text-center space-y-1">
                <p class="text-sm font-bold text-gray-900">{{ isUploadingReference ? '正在上传参考资料...' : selectedUploadName || '点击或将文件拖拽到这里' }}</p>
                <p class="text-[10px] text-gray-400 font-medium">{{ selectedUploadName ? '文件已选中并开始上传，点击可重新选择' : '支持 PDF / DOCX / PPTX / TXT / Markdown / 图片扫描件 (最大 50MB)' }}</p>
              </div>
            </div>
            
            <div class="space-y-3">
              <div class="flex items-center justify-between text-[10px] font-black text-gray-400 uppercase tracking-widest">
                <span>最近上传</span>
                <span @click="handlePreviewAction('上传记录查看')" class="text-indigo-600 cursor-pointer">查看全部</span>
              </div>
              <div class="space-y-2">
                <div v-for="item in uploadedReferences" :key="item" class="flex items-center justify-between p-3 bg-white rounded-xl shadow-sm border border-gray-50">
                  <div class="flex items-center gap-3">
                    <FileText class="w-4 h-4 text-indigo-600" />
                    <span class="text-xs font-bold text-gray-700">{{ item }}</span>
                  </div>
                  <CheckCircle2 class="w-4 h-4 text-green-500" />
                </div>
              </div>
            </div>
          </div>
          
          <!-- Footer -->
          <div class="px-8 py-6 bg-gray-50/50 flex gap-4">
            <button @click="closeUploadModal" class="flex-1 py-4 bg-white rounded-2xl text-sm font-bold text-gray-600 hover:bg-gray-50 transition-all shadow-sm">取消</button>
            <button @click="confirmUpload" class="flex-1 py-4 bg-indigo-600 text-white rounded-2xl text-sm font-bold shadow-xl shadow-indigo-100 hover:opacity-90 transition-all">确认上传</button>
          </div>
        </div>
      </div>
    </Transition>

    <Transition name="fade">
      <div v-if="showToast" class="fixed bottom-8 left-1/2 -translate-x-1/2 z-[60]">
        <div class="bg-gray-900 text-white px-6 py-3 rounded-2xl shadow-2xl flex items-center gap-3"><div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div><span class="text-sm font-bold">{{ toastMessage }}</span></div>
      </div>
    </Transition>
</template>
