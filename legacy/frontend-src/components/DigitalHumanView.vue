<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { API_BASE_URL, apiClient } from '../api/client';
import type { ChatHistoryRecord } from '../types';
import { renderMarkdown } from '../utils/content';
import { 
  Mic, 
  Video as VideoIcon, 
  Share2, 
  PhoneOff, 
  Zap, 
  BookOpen, 
  CheckCircle2, 
  Settings, 
  Sparkles, 
  Send,
  X,
  Play
} from 'lucide-vue-next';

const props = defineProps<{
  projectId?: number | null;
}>();

const currentVoice = ref('温柔亲切女声');
const showVoiceModal = ref(false);
const showKnowledgeModal = ref(false);
const teacherInput = ref('');
const isSending = ref(false);
const sessionId = `digital-human-${props.projectId || 'global'}`;
const videoPlayer = ref<HTMLVideoElement | null>(null);

type VideoStage = 'INIT' | 'REQUESTING' | 'PLAYING';
type StreamStatus = 'idle' | 'generating' | 'playing';

const buildBackendVideoUrl = (path: string) => `${API_BASE_URL}${path}`;

// ── 视频映射表 ─────────────────────────────────────────────
type VideoMapping = { file: string; keywords: string[]; reply: string };

const VIDEO_MAP: VideoMapping[] = [
  {
    file: 'ans_basic.mp4',
    keywords: ['什么是', '方向', '怎么判断'],
    reply: '洛伦兹力是运动电荷在磁场中受到的力，方向可以用左手定则来判断——让磁感线穿过掌心，四指指向正电荷运动方向，拇指所指的就是洛伦兹力的方向。我在视频中给大家做了详细演示，请注意看手势哦！',
  },
  {
    file: 'ans_apply.mp4',
    keywords: ['应用', '现实', '有什么用'],
    reply: '洛伦兹力在现实中有非常多应用！比如电视机的显像管、质谱仪、回旋加速器，甚至医院的核磁共振成像（MRI）都离不开它。视频中我选了几个最典型的例子给大家讲解，一起来看看吧～',
  },
  {
    file: 'ans_tips.mp4',
    keywords: ['注意', '陷阱', '做题'],
    reply: '做洛伦兹力的题最容易踩这几个坑：① 搞混"安培力"和"洛伦兹力"；② 忘记洛伦兹力不做功；③ 速度方向变了但大小不变这个结论没用好。我在视频里逐个拆解了这些易错点，跟着看一遍就稳了！',
  },
];

const matchVideo = (text: string): VideoMapping | null => {
  for (const mapping of VIDEO_MAP) {
    if (mapping.keywords.some((kw) => text.includes(kw))) {
      return mapping;
    }
  }
  return null;
};

const currentVideoSrc = ref(buildBackendVideoUrl('/static/videos/welcome-video.mp4'));
const isVideoLoading = ref(true);

const handleVideoCanPlay = () => {
  isVideoLoading.value = false;
};

const videoStage = ref<VideoStage>('INIT');
const generateProgress = ref(0);
let progressTimer: ReturnType<typeof setInterval> | null = null;

const streamStatus = computed<StreamStatus>(() => {
  if (videoStage.value === 'REQUESTING') return 'generating';
  if (videoStage.value === 'PLAYING') return 'playing';
  return 'idle';
});
const isGenerating = computed(() => videoStage.value === 'REQUESTING');
const isPlayingKnowledge = computed(() => videoStage.value === 'PLAYING');
const activeKnowledgeName = computed(() => {
  const enabledItem = knowledgeItems.value.find((item) => item.enabled);
  return enabledItem?.name || '洛伦兹力与现代物理.pdf';
});
const currentStageLabel = computed(() => {
  if (streamStatus.value === 'generating') return 'AI 渲染中';
  if (streamStatus.value === 'playing') return '讲解视频播放中';
  return '欢迎视频待机中';
});

const syncVideoPlayback = async () => {
  await nextTick();
  const element = videoPlayer.value;
  if (!element) {
    return;
  }

  element.loop = false;
  element.muted = false;

  try {
    await element.play();
  } catch {
    // 某些浏览器会阻止自动播放，交给用户后续交互触发。
  }
};

const startProgressBar = () => {
  if (progressTimer) {
    clearInterval(progressTimer);
  }
  videoStage.value = 'REQUESTING';
  generateProgress.value = 0;
  // 本地映射模式：进度条约1s内快速爬升到90%，后端约0.5s返回
  progressTimer = setInterval(() => {
    if (generateProgress.value < 90) {
      generateProgress.value = Math.min(90, generateProgress.value + Math.random() * 8 + 6);
    }
  }, 80);
};

const finishProgressBar = async (videoUrl?: string | null) => {
  if (progressTimer) {
    clearInterval(progressTimer);
    progressTimer = null;
  }
  generateProgress.value = 100;
  await new Promise((resolve) => window.setTimeout(resolve, 420));
  currentVideoSrc.value = videoUrl ? buildBackendVideoUrl(videoUrl) : buildBackendVideoUrl('/static/videos/welcome-video.mp4');
  videoStage.value = 'PLAYING';
  await syncVideoPlayback();
};

const resetWelcomeVideo = async () => {
  if (progressTimer) {
    clearInterval(progressTimer);
    progressTimer = null;
  }
  generateProgress.value = 0;
  currentVideoSrc.value = buildBackendVideoUrl('/static/videos/welcome-video.mp4');
  videoStage.value = 'INIT';
  await syncVideoPlayback();
};

const handleGenerate = async (text: string) => {
  startProgressBar();
  let videoUrl: string | null = null;
  try {
    const res = await apiClient.post<{ code: number; video_url?: string | null; message?: string }>(
      '/api/digital-human/ask',
      { text },
    );
    videoUrl = res.data?.video_url ?? null;
  } catch {
    showToastMessage('视频映射接口异常，已进入兜底模式');
  } finally {
    await finishProgressBar(videoUrl);
  }
};

const voices = [
  { id: 1, name: '磁性儒雅男声', desc: '沉稳大气，适合学术讲解', icon: '👨‍🏫' },
  { id: 2, name: '清新亲切女声', desc: '温柔自然，适合基础科普', icon: '👩‍🏫' },
  { id: 3, name: '专业新闻男声', desc: '字正腔圆，适合严谨报告', icon: '🎙️' },
  { id: 4, name: '活力激情女声', desc: '语调上扬，适合互动教学', icon: '✨' },
];

const knowledgeItems = ref<{ id: number; name: string; size: string; enabled: boolean }[]>([]);

const digitalHumanChat = ref<{ role: string; name: string; content: string; time: string }[]>([
  { role: 'ai', name: 'AI 助教', content: '你好同学！我是你的专属 AI 物理助教。今天我们在学习《洛伦兹力》，有什么不明白的概念或题目，随时问我哦！', time: '现在' },
]);

const renderedDigitalHumanChat = computed(() => (
  digitalHumanChat.value.map((msg) => ({
    ...msg,
    renderedContent: renderMarkdown(msg.content),
  }))
));

const handleVoiceSelect = (voice: string) => {
  currentVoice.value = voice;
};

const showToast = ref(false);
const toastMessage = ref('');

const showToastMessage = (msg: string) => {
  toastMessage.value = msg;
  showToast.value = true;
  window.setTimeout(() => { showToast.value = false; }, 3000);
};

const handlePanelAction = (message: string) => {
  showToastMessage(message);
};

const saveVoiceConfig = async () => {
  showVoiceModal.value = false;
  try {
    await apiClient.put('/api/config/DIGITAL_HUMAN_VOICE', { config_value: currentVoice.value });
    showToastMessage(`已切换为 ${currentVoice.value}`);
  } catch (e: any) {
    if (e.message?.includes('404')) {
      await apiClient.post('/api/config/', { config_key: 'DIGITAL_HUMAN_VOICE', config_value: currentVoice.value, description: '数字人默认音色' });
      showToastMessage(`已切换为 ${currentVoice.value}`);
    } else {
      showToastMessage(e instanceof Error ? e.message : '保存失败');
    }
  }
};

const saveKnowledgeConfig = async () => {
  showKnowledgeModal.value = false;
  const enabledNames = knowledgeItems.value.filter(i => i.enabled).map(i => i.name).join(',');
  try {
    await apiClient.put('/api/config/DIGITAL_HUMAN_KNOWLEDGE', { config_value: enabledNames });
    showToastMessage('知识范围配置已保存');
  } catch (e: any) {
    if (e.message?.includes('404')) {
      await apiClient.post('/api/config/', { config_key: 'DIGITAL_HUMAN_KNOWLEDGE', config_value: enabledNames, description: '数字人答疑知识范围' });
      showToastMessage('知识范围配置已保存');
    } else {
      showToastMessage(e instanceof Error ? e.message : '保存失败');
    }
  }
};

const sendTeacherMessage = async () => {
  const text = teacherInput.value.trim();
  if (!text) {
    return;
  }

  digitalHumanChat.value.push({
    role: 'student',
    name: '学生',
    content: text,
    time: '刚刚',
  });
  teacherInput.value = '';
  isSending.value = true;

  try {
    // ── 关键词 → 视频匹配 ──
    const matched = matchVideo(text);

    if (matched) {
      // 切换视频源并播放
      isVideoLoading.value = true;
      currentVideoSrc.value = buildBackendVideoUrl(`/static/videos/${matched.file}`);
      videoStage.value = 'PLAYING';
      await nextTick();
      const el = videoPlayer.value;
      if (el) {
        el.load();
        el.play().catch(() => {});
      }

      // 推送预设播报脚本
      digitalHumanChat.value.push({
        role: 'ai',
        name: 'AI 助教',
        content: matched.reply,
        time: '刚刚',
      });
    } else {
      // 未命中关键词 → 走后端聊天
      const chatResult = await apiClient.post<string>('/api/avatar/chat', {
        session_id: sessionId,
        text,
      });
      digitalHumanChat.value.push({
        role: 'ai',
        name: 'AI 助教',
        content: chatResult.data,
        time: '刚刚',
      });
    }
  } catch {
    showToastMessage('问答发送失败，请检查后端服务');
  } finally {
    isSending.value = false;
  }
};

const loadVoiceConfig = async () => {
  try {
    const resp = await apiClient.get<{ config_value: string }>('/api/config/DIGITAL_HUMAN_VOICE');
    if (resp.data.config_value) currentVoice.value = resp.data.config_value;
  } catch { /* use default */ }
};

const loadKnowledgeItems = async () => {
  try {
    if (props.projectId) {
      const resp = await apiClient.get<{ attachments?: { id: number; original_name: string; file_size?: number }[] }>(`/api/projects/${props.projectId}`);
      const atts = resp.data.attachments || [];
      knowledgeItems.value = atts.map((a, i) => ({
        id: a.id || i + 1,
        name: a.original_name,
        size: a.file_size ? `${(a.file_size / 1024).toFixed(0)}KB` : '未知',
        enabled: true,
      }));
    }
  } catch { /* keep empty */ }
};

const loadChatHistory = async () => {
  try {
    const resp = await apiClient.get<ChatHistoryRecord[]>(`/api/avatar/chat-history/${sessionId}`);
    const records = resp.data || [];
    digitalHumanChat.value = records.map(r => ({
      role: r.role === 'assistant' ? 'ai' : r.role === 'user' ? 'student' : r.role,
      name: r.role === 'assistant' ? 'AI 助教' : '学生',
      content: r.content,
      time: r.created_at ? new Date(r.created_at).toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' }) : '',
    }));
  } catch { /* keep empty */ }
};

onMounted(async () => {
  void loadVoiceConfig();
  void loadKnowledgeItems();
  void loadChatHistory();

  // 确保欢迎视频被加载并播放
  currentVideoSrc.value = buildBackendVideoUrl('/static/videos/welcome-video.mp4');
  await nextTick();
  const el = videoPlayer.value;
  if (el) {
    el.load();
    el.play().catch(() => {});
  }
});

onBeforeUnmount(() => {
  if (progressTimer) {
    clearInterval(progressTimer);
  }
});

const handleVideoEnded = () => {
  // 播放结束，保持当前画面（停在最后一帧），无需任何操作
  console.log('数字人讲解结束，停留在最后一帧');
};

watch(currentVideoSrc, () => {
  if (videoPlayer.value) {
    videoPlayer.value.muted = false;
    videoPlayer.value.play().catch((error) => console.log('等待用户交互以播放音频', error));
  }
  void syncVideoPlayback();
});
</script>

<template>
  <div class="flex h-full w-full overflow-hidden bg-gray-50">
    <!-- Left: Video Stream -->
    <div class="flex-1 min-w-0 h-full p-8 flex flex-col overflow-y-auto">
      <div class="w-full max-w-5xl mx-auto flex flex-col gap-6 h-full">
        <div class="relative w-full aspect-video bg-[#0B0F19] rounded-2xl overflow-hidden shadow-2xl flex items-center justify-center group flex-shrink-0">
          <div class="relative w-full h-full rounded-2xl overflow-hidden bg-gray-50/50 shadow-inner">
            <video
              ref="videoPlayer"
              :src="currentVideoSrc"
              class="w-full h-full object-cover transition-opacity duration-300"
              :class="{ 'opacity-0': isVideoLoading, 'opacity-100': !isVideoLoading }"
              autoplay
              playsinline
              preload="auto"
              @canplay="handleVideoCanPlay"
              @ended="handleVideoEnded"
            ></video>

            <div
              v-if="isVideoLoading"
              class="absolute inset-0 bg-white/70 backdrop-blur-md flex flex-col items-center justify-center z-10 transition-all duration-300"
            >
              <div class="relative w-16 h-16 flex items-center justify-center mb-3">
                <svg class="w-12 h-12 text-indigo-200 absolute animate-spin" fill="none" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="3"></circle></svg>
                <svg class="w-12 h-12 text-indigo-600 absolute animate-spin" style="animation-duration: 1.5s; animation-direction: reverse;" fill="none" viewBox="0 0 24 24"><path fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
              </div>
              <span class="text-indigo-600 font-medium text-sm tracking-widest animate-pulse">助教思考中...</span>
            </div>
          </div>

          <Transition name="fade">
            <div v-if="streamStatus === 'generating'" class="absolute inset-0 z-20 bg-black/70 backdrop-blur-md flex flex-col items-center justify-center transition-all duration-300">
              <div class="flex flex-col items-center gap-4">
                <span class="text-indigo-400 font-bold tracking-widest animate-pulse">AI 正在生成数字人讲解...</span>
                <div class="w-64 h-2 overflow-hidden rounded-full bg-white/10">
                  <div
                    class="h-full rounded-full bg-gradient-to-r from-indigo-400 via-sky-400 to-cyan-300 transition-all duration-150 ease-out"
                    :style="{ width: `${Math.min(generateProgress, 100)}%` }"
                  ></div>
                </div>
                <span class="text-sm font-semibold text-white/90">{{ Math.floor(Math.min(generateProgress, 100)) }}%</span>
              </div>
            </div>
          </Transition>

          <!-- Bottom Controls -->
          <div class="absolute bottom-8 left-1/2 z-10 flex -translate-x-1/2 items-center gap-4 rounded-[32px] border border-white/10 bg-black/40 px-8 py-4 shadow-2xl backdrop-blur-xl opacity-0 transition-opacity duration-300 group-hover:opacity-100">
            <button @click="handlePanelAction('麦克风控制功能开发中')" class="p-3 bg-white/10 hover:bg-white/20 rounded-2xl text-white transition-colors"><Mic class="w-6 h-6" /></button>
            <button @click="handlePanelAction('视频流控制功能开发中')" class="p-3 bg-white/10 hover:bg-white/20 rounded-2xl text-white transition-colors"><VideoIcon class="w-6 h-6" /></button>
            <div class="w-px h-8 bg-white/10 mx-2"></div>
            <button @click="handlePanelAction('屏幕共享功能开发中')" class="px-6 py-3 bg-white/10 hover:bg-white/20 rounded-2xl text-white font-bold flex items-center gap-3 transition-colors">
              <Share2 class="w-5 h-5" />
              <span>共享屏幕</span>
            </button>
            <button @click="void resetWelcomeVideo()" class="p-3 bg-red-500 hover:bg-red-600 rounded-2xl text-white transition-colors shadow-lg shadow-red-500/20"><PhoneOff class="w-6 h-6" /></button>
          </div>
        </div>

        <!-- Settings Bar -->
        <div class="bg-white p-6 rounded-[32px] shadow-sm flex items-center justify-between flex-shrink-0">
          <div class="flex gap-12">
            <div class="flex flex-col gap-1">
              <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">当前音色</span>
              <div class="flex items-center gap-2">
                <div class="w-2 h-2 bg-indigo-600 rounded-full"></div>
                <span class="text-sm font-bold">{{ currentVoice }}</span>
              </div>
            </div>
            <div class="flex flex-col gap-1">
              <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">答疑知识库</span>
              <div class="flex items-center gap-2">
                <CheckCircle2 class="w-4 h-4 text-indigo-600" />
                <span class="text-sm font-bold">{{ activeKnowledgeName }}</span>
              </div>
            </div>
            <div class="flex flex-col gap-1">
              <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">数字人状态</span>
              <div class="flex items-center gap-2">
                <div class="w-2 h-2 rounded-full" :class="isGenerating ? 'bg-yellow-400 animate-pulse' : isPlayingKnowledge ? 'bg-green-500' : 'bg-sky-400 animate-pulse'"></div>
                <span class="text-sm font-bold">{{ currentStageLabel }}</span>
              </div>
            </div>
          </div>
          <div class="flex gap-4">
            <button @click="showVoiceModal = true" class="flex items-center gap-2 px-6 py-3 bg-gray-50 hover:bg-gray-100 rounded-2xl text-sm font-bold text-gray-700 transition-colors">
              <Zap class="w-4 h-4" /> 设置数字人音色
            </button>
            <button @click="showKnowledgeModal = true" class="flex items-center gap-2 px-6 py-3 bg-gray-50 hover:bg-gray-100 rounded-2xl text-sm font-bold text-gray-700 transition-colors">
              <BookOpen class="w-4 h-4" /> 配置答疑知识范围
            </button>
            <button @click="handlePanelAction('数字人高级设置功能开发中')" class="p-3 bg-indigo-50 text-indigo-600 rounded-2xl hover:bg-indigo-100 transition-colors"><Settings class="w-5 h-5" /></button>
          </div>
        </div>
      </div>
    </div>

    <!-- Right: Interaction Sidebar -->
    <div class="w-96 min-w-0 flex-shrink-0 h-full bg-white shadow-[-4px_0_24px_rgba(0,0,0,0.02)] border-l border-gray-100 flex flex-col z-10">
      <div class="h-16 flex items-center justify-between px-6 border-b border-gray-50 flex-shrink-0">
        <div class="flex items-center gap-2">
          <div class="w-2 h-2 bg-indigo-600 rounded-full"></div>
          <h3 class="font-bold">互动问答区</h3>
        </div>
        <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Live Feed</span>
      </div>

      <div class="flex-1 overflow-y-auto p-6 space-y-8 custom-scrollbar">
        <div v-for="(msg, idx) in renderedDigitalHumanChat" :key="idx" class="flex flex-col gap-2">
          <div :class="['flex items-start gap-3', msg.name === 'AI 助教' ? 'flex-row-reverse' : '']">
            <div :class="['w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 text-[10px] font-bold', msg.name === 'AI 助教' ? 'bg-indigo-600 text-white' : 'bg-sky-100 text-sky-700']">
              {{ msg.name === 'AI 助教' ? '助教' : '学生' }}
            </div>
            <div :class="['min-w-0 overflow-hidden p-4 rounded-2xl text-sm leading-relaxed shadow-sm flex-1', msg.name === 'AI 助教' ? 'bg-indigo-600 text-white rounded-tr-none' : 'bg-gray-50 text-gray-800 rounded-tl-none']">
              <div :class="['rendered-markdown rendered-chat-markdown break-words whitespace-pre-wrap', msg.name === 'AI 助教' ? 'rendered-markdown-inverse' : '']" v-html="msg.renderedContent"></div>
            </div>
            <div v-if="msg.name === 'AI 助教'" class="w-8 h-8 rounded-lg bg-indigo-50 flex items-center justify-center flex-shrink-0">
              <Sparkles class="w-4 h-4 text-indigo-600" />
            </div>
          </div>
          <span :class="['text-[10px] text-gray-400', msg.name === 'AI 助教' ? 'text-right pr-12' : 'pl-12']">{{ msg.time }} • {{ msg.name }}</span>
        </div>
      </div>

      <div class="p-4 bg-white border-t border-gray-50 flex-shrink-0">
        <div class="relative">
          <input 
            v-model="teacherInput"
            type="text" 
            placeholder="向数字人助教提问..." 
            @keyup.enter="sendTeacherMessage"
            :disabled="isSending"
            class="w-full bg-gray-50 border-none rounded-2xl py-4 pl-6 pr-14 text-sm focus:ring-2 focus:ring-indigo-500/20 outline-none"
          />
          <button @click="sendTeacherMessage" :disabled="isSending" class="absolute right-2 top-1/2 -translate-y-1/2 w-10 h-10 bg-indigo-600 text-white rounded-xl flex items-center justify-center shadow-lg shadow-indigo-100 hover:scale-105 transition-transform disabled:opacity-60">
            <Send class="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>

    <!-- Modals -->
    <Transition name="fade">
      <div v-if="showVoiceModal" class="fixed inset-0 z-50 flex items-center justify-center p-6">
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="showVoiceModal = false"></div>
        <div class="relative bg-white w-full max-w-[500px] rounded-[32px] shadow-2xl overflow-hidden flex flex-col animate-in fade-in zoom-in duration-300">
          <div class="px-8 py-6 flex items-center justify-between">
            <h3 class="text-xl font-black text-gray-900">选择数字人音色</h3>
            <button @click="showVoiceModal = false" class="p-2 hover:bg-gray-50 rounded-xl text-gray-400 hover:text-gray-900 transition-all">
              <X class="w-5 h-5" />
            </button>
          </div>
          <div class="p-8 pt-0">
            <div class="grid grid-cols-2 gap-4">
              <div 
                v-for="voice in voices" 
                :key="voice.id"
                @click="handleVoiceSelect(voice.name)"
                class="p-6 rounded-3xl border-2 transition-all cursor-pointer group relative overflow-hidden"
                :class="currentVoice === voice.name ? 'border-indigo-600 bg-indigo-50/50' : 'border-transparent bg-gray-50 hover:bg-gray-100'"
              >
                <div class="flex flex-col gap-3">
                  <div class="w-12 h-12 bg-white rounded-2xl flex items-center justify-center text-2xl shadow-sm">
                    {{ voice.icon }}
                  </div>
                  <div class="space-y-1">
                    <span class="block text-sm font-bold text-gray-900">{{ voice.name }}</span>
                    <span class="block text-[10px] text-gray-400 leading-tight">{{ voice.desc }}</span>
                  </div>
                </div>
                <div class="absolute bottom-4 right-4 w-8 h-8 bg-white rounded-full flex items-center justify-center shadow-sm opacity-0 group-hover:opacity-100 transition-opacity">
                  <Play class="w-4 h-4 text-indigo-600 fill-indigo-600" />
                </div>
              </div>
            </div>
          </div>
          <div class="px-8 py-6 bg-gray-50/50 flex items-center justify-end gap-4">
            <button @click="showVoiceModal = false" class="px-6 py-3 text-sm font-bold text-gray-500 hover:text-gray-900 transition-colors">取消</button>
            <button 
              @click="saveVoiceConfig"
              class="px-8 py-4 bg-indigo-600 text-white rounded-2xl text-sm font-black shadow-xl shadow-indigo-100 hover:opacity-90 transition-all"
            >
              确认切换音色
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <Transition name="fade">
      <div v-if="showKnowledgeModal" class="fixed inset-0 z-50 flex items-center justify-center p-6">
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="showKnowledgeModal = false"></div>
        <div class="relative bg-white w-full max-w-[600px] rounded-[32px] shadow-2xl overflow-hidden flex flex-col animate-in fade-in zoom-in duration-300">
          <div class="px-8 py-6 flex items-center justify-between">
            <h3 class="text-xl font-black text-gray-900">配置数字人答疑知识库</h3>
            <button @click="showKnowledgeModal = false" class="p-2 hover:bg-gray-50 rounded-xl text-gray-400 hover:text-gray-900 transition-all">
              <X class="w-5 h-5" />
            </button>
          </div>
          <div class="px-6 py-4">
            <p class="text-sm text-gray-500 mb-4">请勾选数字人助教在回答学生问题时可参考的核心语料库：</p>

            <div class="space-y-3 max-h-[40vh] overflow-y-auto pr-2 custom-scrollbar">
              <label class="flex items-center p-3 border-2 border-indigo-500 bg-indigo-50/30 rounded-xl cursor-pointer transition-all shadow-sm">
                <input type="checkbox" checked class="w-4 h-4 text-indigo-600 rounded border-gray-300 focus:ring-indigo-500">
                <div class="w-8 h-8 rounded bg-rose-100 flex items-center justify-center ml-3 mr-3 shrink-0">
                  <span class="text-rose-600 text-xs font-bold">PDF</span>
                </div>
                <div class="flex-1 overflow-hidden">
                  <h4 class="text-sm font-bold text-gray-800 truncate">洛伦兹力与现代物理.pdf</h4>
                  <p class="text-xs text-gray-400 mt-0.5">2.4 MB · 包含 152 个高频考点</p>
                </div>
                <span class="text-[11px] text-emerald-600 bg-emerald-100 px-2 py-0.5 rounded-full font-bold border border-emerald-200 shrink-0">已向量化</span>
              </label>

              <label class="flex items-center p-3 border border-gray-200 hover:border-indigo-300 hover:bg-indigo-50/10 rounded-xl cursor-pointer transition-all">
                <input type="checkbox" class="w-4 h-4 text-indigo-600 rounded border-gray-300 focus:ring-indigo-500">
                <div class="w-8 h-8 rounded bg-orange-100 flex items-center justify-center ml-3 mr-3 shrink-0">
                  <span class="text-orange-600 text-xs font-bold">PPT</span>
                </div>
                <div class="flex-1 overflow-hidden">
                  <h4 class="text-sm font-medium text-gray-700 truncate">物理之美：洛伦兹力演示.pptx</h4>
                  <p class="text-xs text-gray-400 mt-0.5">5.1 MB · 包含 24 页幻灯片</p>
                </div>
                <span class="text-[11px] text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full font-medium border border-gray-200 shrink-0">待处理</span>
              </label>
            </div>

            <button class="mt-5 w-full py-2.5 border-2 border-dashed border-indigo-200 text-indigo-600 rounded-xl text-sm font-bold hover:bg-indigo-50 hover:border-indigo-400 transition-all flex items-center justify-center gap-2 group">
              <svg class="w-4 h-4 group-hover:scale-110 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
              上传本地专业语料
            </button>
          </div>
          <div class="px-8 py-6 bg-gray-50/50 flex items-center justify-end gap-4">
            <button @click="showKnowledgeModal = false" class="px-6 py-3 text-sm font-bold text-gray-500 hover:text-gray-900 transition-colors">取消</button>
            <button 
              @click="saveKnowledgeConfig"
              class="px-8 py-4 bg-indigo-600 text-white rounded-2xl text-sm font-black shadow-xl shadow-indigo-100 hover:opacity-90 transition-all"
            >
              保存配置
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <Transition name="fade">
      <div v-if="showToast" class="fixed bottom-8 left-1/2 -translate-x-1/2 z-[60]">
        <div class="bg-gray-900 text-white px-6 py-3 rounded-2xl shadow-2xl flex items-center gap-3"><div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div><span class="text-sm font-bold">{{ toastMessage }}</span></div>
      </div>
    </Transition>
  </div>
</template>
