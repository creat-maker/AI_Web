<script setup lang="ts">
import { Loader2, Zap, FileText, AlertCircle, Paperclip, Plus, X, Trash2, Send } from 'lucide-vue-next';
import { useWorkspaceHub } from './useWorkspaceHub';
import LessonEditor from './components/LessonEditor.vue';
import PptPreview from './components/PptPreview.vue';
import FlashCard from './components/FlashCard.vue';
import InteractiveGame from './components/InteractiveGame.vue';
import DistributionModal from './components/DistributionModal.vue';
import Toast from './components/Toast.vue';

const props = defineProps<{
  initialTasks?: string[];
  projectId?: number | null;
  projectName?: string;
  generationRequirement?: string;
  autoGenerateToken?: number;
  mockTemplate?: string;
}>();

const hub = useWorkspaceHub(props);
defineExpose({ isGenerated: hub.isGenerated, activeTab: hub.activeTab, momentumAnalysis: hub.momentumAnalysis });
</script>

<template>
  <div class="flex-1 min-w-0 h-full flex flex-col flex-shrink-0">
    <div class="h-16 flex-shrink-0 border-b border-gray-100 bg-white/80 backdrop-blur-xl flex items-center px-6 w-full gap-4">
      <input ref="hub.fileInput" type="file" class="hidden" @change="hub.handleAttachmentSelected">
      <div class="flex-shrink-0">
        <button @click="hub.showAttachments = !hub.showAttachments"
          class="liquid-glass-button flex items-center rounded-full px-4 py-2 text-sm font-medium text-slate-700"
          :class="hub.showAttachments ? 'bg-sky-500/12 text-sky-700 border-sky-200/70' : ''">
          <Paperclip class="w-4 h-4 mr-2" /> 资料清单 ({{ hub.attachments.length }})
        </button>
      </div>
      <div v-if="hub.showMode !== 'ai-games'" class="flex-1 flex items-center gap-2 overflow-x-auto whitespace-nowrap hide-scrollbar">
        <button v-for="tab in hub.tabs" :key="tab.id" @click="hub.activeTab = tab.id"
          class="px-4 py-2 rounded-xl text-sm font-bold transition-all flex items-center gap-2 flex-shrink-0"
          :class="[hub.activeTab === tab.id ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-100' : 'text-gray-500 hover:bg-gray-50']">
          {{ tab.name }}
          <span v-if="hub.isToolGenerating(tab.id)" class="inline-flex items-center gap-1 rounded-full bg-white/15 px-2 py-0.5 text-[10px] font-bold">
            <Loader2 class="w-3 h-3 animate-spin" /> 生成中
          </span>
        </button>
      </div>
      <div class="flex-shrink-0 ml-auto flex items-center gap-3">
        <button @click="hub.handlePackageDownload" :disabled="hub.isPackaging"
          class="liquid-glass-button flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300"
          :class="hub.isPackaging ? 'bg-indigo-50 text-indigo-400 cursor-wait' : 'text-gray-600 hover:text-indigo-600 hover:bg-indigo-50'">
          <svg v-if="hub.isPackaging" class="w-4 h-4 animate-spin text-indigo-500" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/></svg>
          <span v-else class="text-base">📦</span>
          <span>{{ hub.isPackaging ? '正在云端打包...' : '一键打包下载' }}</span>
        </button>
        <button @click="hub.showDistributeModal = true"
          class="liquid-glass-button flex items-center rounded-full bg-emerald-500/12 px-4 py-2 text-sm font-medium text-slate-800">
          <Send class="w-4 h-4 mr-2" /> 一键发给学生
        </button>
      </div>
    </div>

    <div class="flex-1 flex overflow-hidden bg-gray-50">
      <div class="flex-1 min-w-0 h-full flex flex-col bg-gray-50/50 relative z-0">
        <Transition enter-active-class="transition duration-200 ease-out" enter-from-class="opacity-0 -translate-y-4" enter-to-class="opacity-100 translate-y-0"
          leave-active-class="transition duration-150 ease-in" leave-from-class="opacity-100 translate-y-0" leave-to-class="opacity-0 -translate-y-4">
          <div v-if="hub.showAttachments" class="absolute top-4 left-8 w-72 bg-white rounded-2xl shadow-2xl border border-gray-100 flex flex-col z-50 max-h-[60vh]">
            <div class="p-4 border-b border-gray-50 flex items-center justify-between font-medium text-gray-900">
              <div class="flex items-center"><Paperclip class="w-4 h-4 mr-2 text-indigo-600" /> 资料清单</div>
              <button @click="hub.showAttachments = false" class="text-gray-400 hover:text-gray-600"><X class="w-4 h-4" /></button>
            </div>
            <div class="flex-1 overflow-y-auto p-3 flex flex-col gap-2 custom-scrollbar">
              <div v-if="hub.attachments.length === 0" class="p-3 text-xs font-medium text-gray-400">当前项目还没有上传附件。</div>
              <div v-for="file in hub.attachments" :key="file.id" class="p-2 bg-gray-50 rounded-xl flex items-start justify-between group border border-transparent hover:border-indigo-100 transition-colors">
                <div class="flex items-start gap-2 min-w-0">
                  <div class="w-6 h-6 bg-white rounded-md shadow-sm flex items-center justify-center flex-shrink-0 text-indigo-500"><FileText class="w-3 h-3" /></div>
                  <div class="min-w-0"><p class="text-xs font-bold text-gray-700 truncate">{{ file.original_name }}</p><p class="text-[10px] text-gray-400 mt-0.5">{{ hub.formatFileSize(file.file_size) }}</p></div>
                </div>
                <button @click="hub.deleteAttachment(file.id)" class="p-1 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-md opacity-0 group-hover:opacity-100 transition-all"><Trash2 class="w-3 h-3" /></button>
              </div>
            </div>
            <div class="p-3 border-t border-gray-50">
              <button @click="hub.promptAttachmentUpload" :disabled="hub.isUploading" class="w-full py-2 border-2 border-dashed border-gray-200 rounded-xl text-sm font-bold text-gray-500 hover:text-indigo-600 hover:border-indigo-300 hover:bg-indigo-50/50 transition-all flex items-center justify-center gap-2 disabled:opacity-60">
                <Plus class="w-4 h-4" /> {{ hub.isUploading ? '上传中...' : '继续添加' }}
              </button>
            </div>
          </div>
        </Transition>

        <div class="flex-1 min-w-0 overflow-y-auto p-8 custom-scrollbar relative">
          <div v-if="hub.isProjectLoading" class="mb-6 rounded-2xl bg-white px-5 py-4 text-sm font-medium text-gray-500 shadow-sm">正在从 FastAPI 加载项目与附件...</div>

          <div v-if="hub.showMaterialChangeAlert" class="absolute top-8 left-1/2 -translate-x-1/2 z-20 bg-orange-50 border border-orange-200 rounded-2xl p-4 shadow-xl flex items-center gap-6 animate-in slide-in-from-top-4">
            <div class="flex items-center gap-2 text-orange-700"><AlertCircle class="w-5 h-5" /><span class="text-sm font-bold">检测到参考资料变动，是否重新生成当前内容？</span></div>
            <button @click="hub.regenerateContent" class="px-4 py-2 bg-orange-500 text-white rounded-xl text-sm font-bold hover:bg-orange-600 transition-colors shadow-sm">立即重产</button>
          </div>

          <div class="max-w-5xl mx-auto h-full min-w-0">
            <div v-if="hub.isGeneratingContent" class="mb-6 rounded-[28px] bg-gradient-to-r from-indigo-50 via-blue-50 to-purple-50 px-6 py-5 shadow-sm border border-indigo-100">
              <div class="flex items-center gap-3 mb-4">
                <div class="w-9 h-9 bg-indigo-600 rounded-2xl flex items-center justify-center flex-shrink-0 shadow-lg shadow-indigo-200"><Zap class="w-4 h-4 text-white animate-pulse" /></div>
                <div class="flex-1 min-w-0"><span class="text-sm font-black text-gray-900 block">{{ hub.generationStatus || '✨ AI 正在全力创作中，请稍候...' }}</span><span class="text-xs text-indigo-500 font-medium">大模型自主决策·结构化输出</span></div>
                <div class="text-2xl font-black text-indigo-600">{{ hub.generationProgress }}%</div>
              </div>
              <div class="h-2 rounded-full bg-white/80 overflow-hidden shadow-inner">
                <div class="h-full bg-gradient-to-r from-indigo-500 via-purple-500 to-blue-500 transition-all duration-300 rounded-full relative overflow-hidden" :style="{ width: hub.generationProgress + '%' }">
                  <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer"></div>
                </div>
              </div>
            </div>

            <InteractiveGame v-if="hub.showMode === 'ai-games'" mode="ai-games" />

            <template v-else-if="hub.showMode === 'ai-ppt-demo'">
              <PptPreview v-if="hub.activeTab === 'ppt'" :is-ai-demo="true" />
              <LessonEditor v-else-if="hub.activeTab === 'lesson-plan'" :is-ai-demo="true" />
              <FlashCard v-else-if="hub.activeTab === 'flashcards'" :is-ai-demo="true" />
              <div v-else-if="hub.activeTab === 'blog'" class="flex-1 p-8 overflow-y-auto bg-gray-50">
                <div class="max-w-3xl mx-auto bg-white p-10 rounded-2xl shadow-sm border border-gray-100">
                  <h1 class="text-2xl font-bold text-gray-900 mb-4">AI 时代下的教育：如何让学生秒懂"机器学习"？</h1>
                  <div class="flex items-center text-sm text-gray-500 mb-8 gap-4 border-b pb-4"><span>发布于：刚刚</span><span>作者：织课 AI 助教</span><span>阅读时长：3分钟</span></div>
                  <div class="text-gray-700 leading-relaxed space-y-4">
                    <p>在讲解《人工智能应用基础》时，最大的痛点就是"算法黑盒"。学生很难理解一堆数据是怎么变成一个聪明的 AI 的。</p>
                    <p>今天，我们不再使用枯燥的 PPT，而是引入了<strong>项目制实操</strong>。通过让学生自己给图片打标签（比如分辨猫和狗），然后点击"开始训练"，他们能亲眼看到准确率曲线的上升。</p>
                    <div class="bg-gray-100 p-4 rounded-lg border-l-4 border-indigo-500 my-4 text-gray-600 font-medium">💡 教学小贴士：在实操环节，故意给 AI 喂一些错误的数据，让学生观察 AI 的"翻车现场"，借机引出"数据质量"的重要性。</div>
                  </div>
                </div>
              </div>
            </template>

            <template v-else>
              <div v-if="!hub.hasGeneratedContent(hub.activeTab) && !hub.isGeneratingContent" class="h-full flex flex-col items-center justify-center gap-6">
                <div class="w-24 h-24 bg-gray-100 rounded-3xl flex items-center justify-center text-gray-400"><FileText class="w-10 h-10" /></div>
                <div class="text-center space-y-2"><h3 class="text-2xl font-black text-gray-900">该项内容尚未生成</h3><p class="text-gray-500">系统将基于当前项目资料进行深度解析，并生成可直接编辑的内容初稿。</p></div>
                <div class="rounded-full bg-indigo-50 px-4 py-2 text-xs font-bold text-indigo-700">当前已识别 {{ hub.getCurrentAttachmentList().length }} 份资料</div>
                <button @click="hub.handleGenerate" :disabled="hub.isGeneratingContent"
                  class="mt-4 flex items-center gap-2 rounded-2xl px-8 py-4 font-bold text-white shadow-xl transition-all disabled:cursor-not-allowed disabled:opacity-80"
                  :class="hub.isGeneratingContent ? 'bg-indigo-500 shadow-indigo-100' : 'bg-indigo-600 shadow-indigo-200 hover:scale-105'">
                  <Loader2 v-if="hub.isGeneratingContent" class="w-5 h-5 animate-spin" /><Zap v-else class="w-5 h-5" />
                  {{ hub.isGeneratingContent ? '正在深度解析资料并生成...' : '基于当前资料生成' }}
                </button>
              </div>

              <PptPreview v-else-if="hub.activeTab === 'ppt'" />
              <LessonEditor v-else-if="hub.activeTab === 'lesson-plan'" :is-generating="hub.isGenerating" :is-generated="hub.isGenerated" :project-name="props.projectName" />
              <FlashCard v-else-if="hub.activeTab === 'flashcards'" />
              <InteractiveGame v-else-if="hub.activeTab === 'game'" mode="sandbox" />

              <div v-else-if="hub.activeTab === 'video'" class="w-full h-full flex flex-col items-center justify-center bg-[#F9FAFB] p-8">
                <div class="mb-8 text-center">
                  <div class="inline-flex items-center justify-center w-12 h-12 rounded-full bg-indigo-100 text-indigo-600 mb-4 shadow-sm">
                    <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd"/></svg>
                  </div>
                  <h2 class="text-2xl font-bold text-gray-800 tracking-wide mb-2">演示动画预览</h2>
                  <p class="text-sm text-gray-500 font-medium">《洛伦兹力：粒子在磁场中的舞蹈》</p>
                </div>
                <div class="relative w-full max-w-sm bg-black rounded-2xl shadow-[0_20px_50px_rgba(0,0,0,0.15)] overflow-hidden border border-gray-200/50">
                  <video class="w-full h-auto max-h-[65vh] object-contain outline-none" src="/short-video.mp4" controls autoplay loop playsinline></video>
                </div>
              </div>

              <div v-else-if="hub.activeTab === 'blog'" class="w-full space-y-12"></div>
            </template>
          </div>
        </div>
      </div>
    </div>

    <Transition enter-active-class="transition duration-300 ease-out" enter-from-class="opacity-0 scale-95" enter-to-class="opacity-100 scale-100"
      leave-active-class="transition duration-200 ease-in" leave-from-class="opacity-100 scale-100" leave-to-class="opacity-0 scale-95">
      <DistributionModal v-if="hub.showDistributeModal"
        :selected-channels="hub.selectedChannels" :selected-classes="hub.selectedClasses"
        :distribution-channels="hub.distributionChannels" :distribution-class-options="hub.distributionClassOptions"
        :is-distribution-ready="hub.isDistributionReady" :is-distribution-mock-loading="hub.isDistributionMockLoading"
        @close="hub.showDistributeModal = false"
        @toggle-channel="(id) => hub.toggleSelection(hub.selectedChannels, id)"
        @toggle-class="(cls) => hub.toggleSelection(hub.selectedClasses, cls)"
        @confirm="hub.confirmDistribution"
      />
    </Transition>

    <Transition name="fade">
      <Toast v-if="hub.showToast" :message="hub.toastMessage" />
    </Transition>
  </div>
</template>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.liquid-glass-button { position: relative; overflow: hidden; border: 1px solid rgba(255,255,255,0.82); background: linear-gradient(180deg, rgba(255,255,255,0.84), rgba(255,255,255,0.58)); box-shadow: inset 0 1px 0 rgba(255,255,255,0.88), 0 18px 40px rgba(148,163,184,0.16); backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px); }
@keyframes shimmer { 0% { transform: translateX(-100%); } 100% { transform: translateX(200%); } }
.animate-shimmer { animation: shimmer 1.8s infinite linear; }
</style>
