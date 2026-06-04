<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { apiClient } from '../api/client';
import type { StagedAttachmentRecord, ScrapedCard } from '../types';
import { 
  CloudUpload, 
  Globe, 
  Plus, 
  MoreHorizontal, 
  FileText, 
  Clock, 
  ChevronRight, 
  Sparkles, 
  Video, 
  ExternalLink,
  X,
  Search
} from 'lucide-vue-next';

type ScrapedDetailSection = {
  title: string;
  bullets: string[];
};

type ScrapedDetail = {
  source: string;
  origin: string;
  statusNote: string;
  synopsis: string[];
  outline: ScrapedDetailSection[];
  highlights: string[];
};

type RecommendationItem = {
  id: number;
  title: string;
  source: string;
  kind: '文献' | '视频' | '课程' | '案例';
  badge: string;
  accent: string;
  url: string;
};

const showUploadModal = ref(false);
const showCloudImportModal = ref(false);
const showCreateScrapeModal = ref(false);
const selectedCloudItems = ref<number[]>([]);
const cloudSearchQuery = ref('');
const selectedScrapedItem = ref<ScrapedCard | null>(null);

const aiScrapedCards = ref<ScrapedCard[]>([]);
const isScrapeLoading = ref(false);
const recommendationItems = ref<RecommendationItem[]>([
  { id: 101, title: '《大学物理（第三版）》课后习题超详解析', source: '高等教育出版社 · 文献', kind: '文献', badge: '高度相关', accent: 'indigo', url: 'https://www.hep.com.cn/' },
  { id: 102, title: '麻省理工经典物理公开课：电磁学核心', source: 'MIT OpenCourseWare · 课程', kind: '课程', badge: '备课常用', accent: 'emerald', url: 'https://ocw.mit.edu/courses/8-02-physics-ii-electricity-and-magnetism-spring-2007/' },
  { id: 103, title: '法拉第电磁感应与洛伦兹力3D实验演示', source: 'Bilibili · 视频', kind: '视频', badge: '案例补充', accent: 'amber', url: 'https://search.bilibili.com/all?keyword=%E6%B4%9B%E4%BC%A6%E5%85%B9%E5%8A%9B3D%E6%BC%94%E7%A4%BA' },
]);
const isLoadingMoreRecommendations = ref(false);

// 专题私域库聘合数据
type PrivateFile = { id: number; name: string; type: string; time: string; status: string; size: string };
type PrivateCollection = {
  id: number;
  title: string;
  desc: string;
  status: '进行中' | '已完成';
  files: PrivateFile[];
};

const myCollections = ref<PrivateCollection[]>([
  {
    id: 1,
    title: '我的专属物理教学库',
    desc: '包含老师上传的课程大纲、实验视频及学情报告等私有资源',
    status: '进行中',
    files: [
      { id: 1, name: '洛伦兹力与现代物理.pdf', type: 'PDF', time: '昨天 14:30', status: '已学习', size: '3.2 MB' },
      { id: 2, name: '高二物理学情分析报告.docx', type: 'DOCX', time: '3天前', status: '已学习', size: '1.5 MB' },
      { id: 3, name: '磁场核心考点大纲.txt', type: 'TXT', time: '刚刚', status: '解析中...', size: '12 KB' },
    ],
  },
]);

const showCollectionDrawer = ref(false);
const currentCollection = ref<PrivateCollection | null>(null);

const openCollection = (col: PrivateCollection) => {
  currentCollection.value = col;
  showCollectionDrawer.value = true;
};

const closeCollectionDrawer = () => {
  showCollectionDrawer.value = false;
};

const buildScrapedDetail = (card: ScrapedCard): ScrapedDetail => {
  const lowerTitle = card.title.toLowerCase();

  let source = '中国大学 MOOC · 教学专题课';
  let origin = '全网教学资源聚合';
  let statusNote = '已完成全文抓取、摘要提炼与知识点切片。';

  if (lowerTitle.includes('python')) {
    source = 'Coursera · Python Programming Specialization';
    origin = '编程基础与案例实验';
    statusNote = '已补齐代码样例、运行环境说明与课堂练习建议。';
  } else if (lowerTitle.includes('人工智能')) {
    source = '中国大学 MOOC · 人工智能导论';
    origin = '高等教育公开课';
    statusNote = '已同步课程章节、案例链接与模型发展脉络。';
  } else if (lowerTitle.includes('网络') || lowerTitle.includes('架构')) {
    source = 'IEEE Xplore · Network Architecture Survey';
    origin = '论文与行业报告';
    statusNote = '已抽取关键术语、趋势图表与课堂讨论问题。';
  }

  return {
    source,
    origin,
    statusNote,
    synopsis: [
      `${card.title} 当前已进入可直接备课的资料状态，抓取结果围绕“概念解释、案例拆解、课堂应用”三条线重组，便于教师快速二次加工。`,
      card.desc || '系统已针对原始资料进行了摘要压缩，并保留最适合课堂讲解的核心段落与关键词。',
      '在课堂使用上，这份资料更适合作为导入背景、核心知识点补充，以及课后延伸阅读的统一来源。',
    ],
    outline: [
      {
        title: '一、资料核心脉络',
        bullets: [
          '先建立主题定义与知识边界，再用典型案例帮助学生形成直观理解。',
          '每个子主题都可以独立切成 8 至 12 分钟的课堂讲授单元。',
        ],
      },
      {
        title: '二、适合课堂展开的内容',
        bullets: [
          '可直接提炼成课堂提问、板书要点与分层练习。',
          '建议搭配真实场景或实验演示，提升学生对抽象概念的接受度。',
        ],
      },
      {
        title: '三、备课延伸建议',
        bullets: [
          '适合与现有教材章节联动，作为课前导学或课后探究材料。',
          '可继续向知识库追加同主题视频、论文或实验案例，形成完整资源链。',
        ],
      },
    ],
    highlights: [
      `资料类型：${card.type}`,
      `最近更新时间：${card.time}`,
      `抓取状态：${card.status}`,
    ],
  };
};

const loadScrapedCards = () => {
  aiScrapedCards.value = [
    {
      id: 1,
      title: '电磁学核心物理量与定理推导',
      desc: '涵盖静电场、稳恒磁场、麦克斯韦方程组及洛伦兹力的核心公式推导与题型归纳。',
      type: '教学资料',
      time: '同步中',
      status: '进行中',
      color: 'text-green-500',
    },
    {
      id: 2,
      title: '量子物理与波粒二象性指南',
      desc: '梳理光电效应、康普顿散射、薛定谔方程等量子力学基础概念，适合高年级物理科普。',
      type: '教学资料',
      time: '已完成',
      status: '已完成',
      color: 'text-gray-500',
    },
    {
      id: 3,
      title: '刚体力学与角动量守恒动图解析',
      desc: '收集转动惯量计算、角动量定理及定轴转动动力学的经典物理模型与可视化动图。',
      type: '教学素材',
      time: '同步中',
      status: '进行中',
      color: 'text-green-500',
    },
    {
      id: 4,
      title: '热力学第二定律与熵增原理',
      desc: '总结卡诺循环、可逆与不可逆过程在宏观物理过程中的应用分析及课后习题。',
      type: '教学资料',
      time: '同步中',
      status: '进行中',
      color: 'text-green-500',
    },
  ];
};

const filteredScrapedCards = computed(() => {
  if (!cloudSearchQuery.value) return aiScrapedCards.value;
  return aiScrapedCards.value.filter(card => 
    card.title.toLowerCase().includes(cloudSearchQuery.value.toLowerCase()) ||
    card.desc.toLowerCase().includes(cloudSearchQuery.value.toLowerCase())
  );
});

const selectedScrapedDetail = computed(() => (
  selectedScrapedItem.value ? buildScrapedDetail(selectedScrapedItem.value) : null
));

const openScrapedDetail = (card: ScrapedCard) => {
  selectedScrapedItem.value = card;
};

const closeScrapedDetail = () => {
  selectedScrapedItem.value = null;
};

const loadMoreRecommendations = async () => {
  if (isLoadingMoreRecommendations.value) {
    return;
  }

  isLoadingMoreRecommendations.value = true;
  await new Promise((resolve) => {
    window.setTimeout(resolve, 1000);
  });

  const nextBase = recommendationItems.value.length + 1;
  recommendationItems.value = [
    ...recommendationItems.value,
    { id: nextBase, title: '智能实验课堂设计清单', source: '清华学堂在线 · 课程', kind: '课程', badge: '新增推荐', accent: 'sky' },
    { id: nextBase + 1, title: '机器学习导论精讲摘编', source: 'arXiv Digest · 文献', kind: '文献', badge: '最新同步', accent: 'violet' },
    { id: nextBase + 2, title: '课堂板书与讲解节奏案例', source: '教师发展中心 · 案例', kind: '案例', badge: '可直接借鉴', accent: 'rose' },
  ];
  isLoadingMoreRecommendations.value = false;
  showToastMessage('已为你追加 3 条新推荐资源');
};

const toggleCloudItem = (id: number) => {
  const index = selectedCloudItems.value.indexOf(id);
  if (index === -1) {
    selectedCloudItems.value.push(id);
  } else {
    selectedCloudItems.value.splice(index, 1);
  }
};

const isImporting = ref(false);
const isScraping = ref(false);
const showToast = ref(false);
const toastMessage = ref('');
const fileInput = ref<HTMLInputElement | null>(null);
const isUploading = ref(false);
const selectedLocalUploadName = ref('');
const selectedLocalFileObject = ref<File | null>(null);
const uploadedLocalFiles = ref<string[]>([]);

const closeUploadModal = () => {
  showUploadModal.value = false;
  selectedLocalFileObject.value = null;
  selectedLocalUploadName.value = '';
};

const showToastMessage = (msg: string) => {
  toastMessage.value = msg;
  showToast.value = true;
  window.setTimeout(() => { showToast.value = false; }, 3000);
};

const handleCloudImport = async () => {
  if (selectedCloudItems.value.length === 0) return;
  isImporting.value = true;
  try {
    const selectedCount = selectedCloudItems.value.length;
    const selectedTitles = selectedCloudItems.value.map(id => aiScrapedCards.value.find(c => c.id === id)?.title).join(', ');
    await apiClient.post('/api/avatar/generate', {
      prompt: `导入云端资料: ${selectedTitles}`,
      generator_type: 'cloud-import',
    });
    showCloudImportModal.value = false;
    selectedCloudItems.value = [];
    showToastMessage(`已成功导入 ${selectedCount} 份云端资料`);
  } catch (e) {
    
    showToastMessage('导入失败，请稍后重试');
  } finally {
    isImporting.value = false;
  }
};

const scrapeTaskForm = ref({
  topic: '',
  sources: ['Bilibili', '知网'],
  depth: '专业课程'
});

const handleCreateScrapeTask = async () => {
  if (!scrapeTaskForm.value.topic.trim()) {
    showToastMessage('请输入探索主题');
    return;
  }
  isScraping.value = true;
  try {
    await apiClient.post('/api/avatar/generate', {
      session_id: 'knowledge-scrape',
      prompt: `AI 全网抓取任务: 主题="${scrapeTaskForm.value.topic}", 来源=${scrapeTaskForm.value.sources.join(',')}, 深度=${scrapeTaskForm.value.depth}`,
      generator_type: 'scrape-task',
    });
    showCreateScrapeModal.value = false;
    const newTopic = scrapeTaskForm.value.topic;
    showToastMessage(`抓取任务「${newTopic}」已创建`);
    aiScrapedCards.value.unshift({
      id: Date.now(),
      title: newTopic,
      desc: `正在全网检索「${newTopic}」相关学术文献、视频解析及科普文章，请稍候...`,
      type: '跨平台抓取',
      time: '刚刚',
      status: '进行中',
      color: 'text-green-500',
    });
    scrapeTaskForm.value.topic = '';
  } catch (e) {
    showToastMessage('创建任务失败，请稍后重试');
  } finally {
    isScraping.value = false;
  }
};

const toggleScrapeSource = (source: string) => {
  const index = scrapeTaskForm.value.sources.indexOf(source);
  if (index === -1) {
    scrapeTaskForm.value.sources.push(source);
  } else {
    scrapeTaskForm.value.sources.splice(index, 1);
  }
};

const triggerLocalUpload = () => {
  fileInput.value?.click();
};

const handleLocalFileChange = (event: Event) => {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  if (!file) return;
  selectedLocalFileObject.value = file;
  selectedLocalUploadName.value = file.name;
  input.value = '';
};

const handleConfirmUpload = async () => {
  const file = selectedLocalFileObject.value;
  if (!file) return;
  isUploading.value = true;
  try {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.postForm<StagedAttachmentRecord>('/api/attachments/upload', formData);
    uploadedLocalFiles.value = [response.data.original_name, ...uploadedLocalFiles.value.filter((item) => item !== response.data.original_name)].slice(0, 5);
    // 将新文件追加到第一个专题库
    if (myCollections.value.length > 0) {
      const newId = Date.now();
      const ext = response.data.original_name.split('.').pop()?.toUpperCase() || 'FILE';
      myCollections.value[0].files.unshift({
        id: newId,
        name: response.data.original_name,
        type: ext,
        time: '刚刚',
        status: '解析中...',
        size: response.data.file_size ? `${(response.data.file_size / 1024).toFixed(0)} KB` : '-',
      });
      myCollections.value[0].status = '进行中';
    }
    closeUploadModal();
    showToastMessage('✅ 文件上传成功，已添加到专题库！');
    void loadScrapedCards();
  } catch (error) {
    const errMsg = error instanceof Error ? error.message : '未知网络错误';
    showToastMessage(`上传失败：${errMsg}`);
  } finally {
    isUploading.value = false;
  }
};

onMounted(() => {
  void loadScrapedCards();
});
</script>

<template>
  <div class="max-w-6xl mx-auto space-y-8">
    <div class="flex flex-col gap-2">
      <h1 class="text-3xl font-black text-gray-900">我的专属教学知识库</h1>
      <p class="text-gray-500">基于生成式 AI 的深度教学助手，汇集您的学术沉淀与全网优质资源。</p>
    </div>

    <!-- Upload Area -->
    <div class="bg-white p-8 rounded-[32px] border-2 border-dashed border-gray-200 flex items-center justify-between group hover:bg-indigo-50/30 transition-colors">
      <div class="flex items-center gap-6">
        <div class="w-16 h-16 bg-indigo-50 rounded-2xl flex items-center justify-center text-indigo-600 group-hover:scale-110 transition-transform">
          <CloudUpload class="w-8 h-8" />
        </div>
        <div class="flex flex-col">
          <span class="text-lg font-bold">投喂教学灵感</span>
          <span class="text-sm text-gray-400">支持 PDF / DOCX / PPTX / TXT / Markdown / 图片扫描件 OCR 深度解析</span>
        </div>
      </div>
      <div class="flex gap-4">
        <button @click="showUploadModal = true" class="bg-indigo-600 text-white px-6 py-3 rounded-xl font-bold hover:opacity-90 transition-opacity">选择文件上传</button>
        <button @click="showCloudImportModal = true" class="bg-gray-100 text-gray-700 px-6 py-3 rounded-xl font-bold hover:bg-gray-200 transition-colors">导入云端资料</button>
      </div>
    </div>

    <!-- 专属私域库聚合卡片区 -->
    <div class="mb-2">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-xl font-bold">我的专属私域库</h3>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
        <div class="bg-white rounded-2xl p-6 border border-gray-100 shadow-[0_2px_10px_rgba(0,0,0,0.02)] hover:shadow-[0_8px_20px_rgba(0,0,0,0.06)] transition-all cursor-pointer relative group" @click="openCollection(myCollections[0])">
          <div class="flex items-center justify-between mb-4">
            <span class="flex items-center gap-1.5 text-xs font-medium text-green-600 bg-green-50 px-2.5 py-1.5 rounded-full border border-green-100">
              <span class="w-1.5 h-1.5 rounded-full bg-green-500"></span>
              专享私域库
            </span>
            <svg class="w-5 h-5 text-gray-300 hover:text-gray-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h.01M12 12h.01M19 12h.01M6 12a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0z"></path></svg>
          </div>
          <h3 class="text-lg font-bold text-gray-800 mb-2 group-hover:text-indigo-600 transition-colors">高二物理：洛伦兹力与磁场专题</h3>
          <p class="text-sm text-gray-500 line-clamp-2 mb-6">汇集老师本地上传的教案大纲、学情报告与实验视频，已完成深度向量化解析，随时可调用。</p>
          <div class="flex items-center justify-between text-xs text-gray-400 pt-4 border-t border-gray-50">
            <div class="flex items-center gap-2">
              <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
              包含 3 份本地文件 · 已同步
            </div>
            <div class="flex items-center text-indigo-500 font-medium opacity-0 group-hover:opacity-100 transform translate-x-0 group-hover:translate-x-1 transition-all">
              管理库
              <svg class="w-4 h-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 专属私域库文件详情抽屉 -->
    <Transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="showCollectionDrawer && currentCollection" class="fixed inset-0 z-[55] flex justify-end">
        <div class="absolute inset-0 bg-slate-900/10 backdrop-blur-[2px]" @click="closeCollectionDrawer"></div>
        <aside class="relative h-full w-full max-w-[500px] overflow-hidden border-l border-white/80 bg-white/90 shadow-[-24px_0_80px_rgba(15,23,42,0.14)] backdrop-blur-xl flex flex-col animate-slide-left">
          <div class="px-8 py-6 border-b border-gray-100/80 flex items-start justify-between gap-4">
            <div class="space-y-2">
              <div class="flex items-center gap-2">
                <span class="inline-flex items-center rounded-full bg-indigo-50 px-3 py-1 text-[11px] font-black text-indigo-700">专属私域库</span>
                <span class="inline-flex items-center rounded-full px-3 py-1 text-[11px] font-black"
                  :class="currentCollection.status === '进行中' ? 'bg-green-50 text-green-600' : 'bg-gray-100 text-gray-500'">
                  {{ currentCollection.status }}
                </span>
              </div>
              <h3 class="text-xl font-black text-gray-900">{{ currentCollection.title }}</h3>
              <p class="text-sm text-gray-500">{{ currentCollection.desc }}</p>
            </div>
            <button @click="closeCollectionDrawer" class="flex h-11 w-11 items-center justify-center rounded-2xl bg-white/80 text-gray-400 shadow-sm ring-1 ring-black/5 backdrop-blur-md hover:text-gray-900 transition-all flex-shrink-0">
              <X class="w-5 h-5" />
            </button>
          </div>
          <div class="flex-1 overflow-y-auto p-6 space-y-3 custom-scrollbar">
            <div class="text-[10px] font-black text-gray-400 uppercase tracking-widest mb-4">共 {{ currentCollection.files.length }} 份资料</div>
            <div
              v-for="file in currentCollection.files"
              :key="file.id"
              class="flex items-center gap-4 p-4 bg-white rounded-2xl border border-gray-100 shadow-sm hover:border-indigo-100 hover:shadow-md transition-all group"
            >
              <div class="w-10 h-10 rounded-xl bg-gray-50 flex items-center justify-center shrink-0 text-gray-400 group-hover:bg-indigo-50 group-hover:text-indigo-500 transition-colors">
                <FileText class="w-5 h-5" />
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-bold text-gray-800 truncate" :title="file.name">{{ file.name }}</p>
                <div class="flex items-center gap-2 mt-1 text-xs">
                  <span class="flex items-center gap-1" :class="file.status === '已学习' ? 'text-green-500' : 'text-amber-500'">
                    <span class="w-1.5 h-1.5 rounded-full" :class="file.status === '已学习' ? 'bg-green-500' : 'bg-amber-500 animate-pulse'"></span>
                    {{ file.status }}
                  </span>
                  <span class="text-gray-300">·</span>
                  <span class="text-gray-400">{{ file.time }}</span>
                  <span class="text-gray-300">·</span>
                  <span class="text-gray-400">{{ file.size }}</span>
                </div>
              </div>
              <span class="text-[10px] font-black text-gray-300 shrink-0">{{ file.type }}</span>
            </div>
          </div>
          <div class="px-6 py-4 border-t border-gray-100 flex-shrink-0">
            <button @click="showUploadModal = true; closeCollectionDrawer()" class="w-full py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-2xl text-sm font-bold transition-colors flex items-center justify-center gap-2">
              <Plus class="w-4 h-4" /> 继续投喂资料
            </button>
          </div>
        </aside>
      </div>
    </Transition>

    <div class="grid grid-cols-3 gap-8">
      <!-- AI Scraped Grid -->
      <div class="col-span-2 space-y-6">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <Globe class="w-5 h-5 text-indigo-600" />
            <h3 class="text-xl font-bold">全网 AI 自动抓取</h3>
          </div>
          <button @click="showCreateScrapeModal = true" class="text-indigo-600 text-sm font-bold flex items-center gap-1">
            <Plus class="w-4 h-4" /> 创建抓取任务
          </button>
        </div>
        <div class="grid grid-cols-2 gap-6">
          <div v-if="isScrapeLoading" class="col-span-2 bg-white p-12 rounded-3xl text-center">
            <p class="text-sm font-medium text-gray-400">正在从 AI 加载抓取资料...</p>
          </div>
          <div v-else-if="aiScrapedCards.length === 0" class="col-span-2 bg-white p-12 rounded-3xl text-center space-y-3">
            <Globe class="w-10 h-10 text-gray-300 mx-auto" />
            <p class="text-sm font-medium text-gray-400">暂无抓取任务，点击右上角「创建抓取任务」开始</p>
          </div>
          <div v-for="card in aiScrapedCards" :key="card.id" @click="openScrapedDetail(card)" class="bg-white p-6 rounded-3xl hover:shadow-xl transition-all cursor-pointer group relative overflow-hidden">
            <div class="flex items-center justify-between mb-4">
              <div class="flex items-center gap-2">
                <div class="w-2 h-2 rounded-full" :class="card.status === '进行中' ? 'bg-green-500 animate-pulse' : 'bg-amber-400'"></div>
                <span class="text-[10px] font-bold uppercase tracking-widest" :class="card.status === '进行中' ? 'text-green-500' : 'text-gray-400'">{{ card.status }}</span>
              </div>
              <MoreHorizontal class="w-5 h-5 text-gray-300 hover:text-gray-600" />
            </div>
            <h4 class="text-lg font-bold text-gray-900 mb-2 group-hover:text-indigo-600 transition-colors">{{ card.title }}</h4>
            <p class="text-sm text-gray-400 line-clamp-2 mb-6">{{ card.desc }}</p>
            <div class="flex items-center justify-between pt-4">
              <div class="flex items-center gap-4 text-[10px] font-bold text-gray-400">
                <span class="flex items-center gap-1"><FileText class="w-3 h-3" /> {{ card.type }}</span>
                <span class="flex items-center gap-1"><Clock class="w-3 h-3" /> {{ card.time }}</span>
              </div>
              <ChevronRight class="w-5 h-5 text-gray-300 group-hover:translate-x-1 transition-transform" />
            </div>
          </div>
        </div>
      </div>

      <!-- Recommendations -->
      <div class="space-y-6">
        <div class="bg-white p-8 rounded-[32px] shadow-sm space-y-6">
          <div class="flex items-center gap-2">
            <Sparkles class="w-5 h-5 text-purple-600" />
            <h3 class="text-lg font-bold">AI 智能推荐资源</h3>
          </div>
          <div class="space-y-4">
            <a v-for="item in recommendationItems" :key="item.id" :href="item.url" target="_blank" rel="noopener noreferrer" class="block p-4 bg-gray-50 rounded-2xl hover:bg-indigo-50/50 transition-colors cursor-pointer group no-underline">
              <div class="flex items-center gap-3 mb-2">
                <div class="w-10 h-10 bg-white rounded-xl flex items-center justify-center shadow-sm">
                  <component :is="item.kind === '视频' ? Video : FileText" class="w-5 h-5 text-indigo-600" />
                </div>
                <div class="flex flex-col min-w-0">
                  <span class="text-sm font-bold truncate text-gray-900">{{ item.title }}</span>
                  <span class="text-[10px] text-gray-400">{{ item.source }}</span>
                </div>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-[10px] font-bold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-full">{{ item.badge }}</span>
                <ExternalLink class="w-3 h-3 text-gray-300 group-hover:text-indigo-600 transition-colors" />
              </div>
            </a>
          </div>
          <button @click="loadMoreRecommendations" :disabled="isLoadingMoreRecommendations" class="w-full text-center text-sm font-bold text-gray-400 hover:text-indigo-600 transition-colors py-2 disabled:opacity-50 disabled:cursor-not-allowed">
            {{ isLoadingMoreRecommendations ? '加载推荐中...' : '查看更多推荐' }}
          </button>
        </div>

        <!-- System Status -->
        <div class="bg-indigo-50 p-6 rounded-[32px]">
          <span class="text-[10px] font-bold text-indigo-400 uppercase tracking-widest block mb-2">系统状态</span>
          <p class="text-xs text-indigo-700 font-medium">正在为 12 个新抓取的文件建立矢量索引...</p>
          <div class="mt-3 h-1.5 w-full bg-indigo-200 rounded-full overflow-hidden">
            <div class="h-full bg-indigo-600 rounded-full" style="width: 45%"></div>
          </div>
        </div>
      </div>
    </div>

    <Transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="selectedScrapedItem && selectedScrapedDetail" class="fixed inset-0 z-[55] flex justify-end">
        <div class="absolute inset-0 bg-slate-900/10 backdrop-blur-[2px]" @click="closeScrapedDetail"></div>
        <aside class="relative h-full w-full max-w-[560px] overflow-hidden border-l border-white/80 bg-white/90 shadow-[-24px_0_80px_rgba(15,23,42,0.14)] backdrop-blur-xl flex flex-col animate-slide-left">
          <div class="px-8 py-6 border-b border-gray-100/80 flex items-start justify-between gap-4">
            <div class="space-y-3">
              <div class="flex items-center gap-2">
                <span class="inline-flex items-center rounded-full bg-indigo-50 px-3 py-1 text-[11px] font-black text-indigo-700">资料详情</span>
                <span class="inline-flex items-center rounded-full bg-emerald-50 px-3 py-1 text-[11px] font-black text-emerald-600">{{ selectedScrapedItem.status }}</span>
              </div>
              <div>
                <h3 class="text-2xl font-black text-gray-900 leading-tight">{{ selectedScrapedItem.title }}</h3>
                <p class="mt-2 text-sm leading-6 text-gray-500">{{ selectedScrapedDetail.statusNote }}</p>
              </div>
            </div>
            <button @click="closeScrapedDetail" class="flex h-11 w-11 items-center justify-center rounded-2xl bg-white/80 text-gray-400 shadow-sm ring-1 ring-black/5 backdrop-blur-md hover:text-gray-900 transition-all">
              <X class="w-5 h-5" />
            </button>
          </div>

          <div class="flex-1 overflow-y-auto p-8 space-y-8 custom-scrollbar">
            <div class="grid grid-cols-2 gap-4">
              <div class="rounded-[24px] bg-[linear-gradient(180deg,_rgba(238,242,255,0.96),_rgba(255,255,255,0.95))] p-5 shadow-sm border border-white/70">
                <div class="text-[10px] font-black uppercase tracking-[0.22em] text-gray-400">来源</div>
                <div class="mt-2 text-sm font-bold text-gray-900">{{ selectedScrapedDetail.source }}</div>
                <p class="mt-2 text-xs leading-5 text-gray-500">{{ selectedScrapedDetail.origin }}</p>
              </div>
              <div class="rounded-[24px] bg-[linear-gradient(180deg,_rgba(236,253,245,0.96),_rgba(255,255,255,0.95))] p-5 shadow-sm border border-white/70">
                <div class="text-[10px] font-black uppercase tracking-[0.22em] text-gray-400">抓取状态</div>
                <div class="mt-2 text-sm font-bold text-gray-900">{{ selectedScrapedItem.status }}</div>
                <p class="mt-2 text-xs leading-5 text-gray-500">最近同步时间：{{ selectedScrapedItem.time }}</p>
              </div>
            </div>

            <section class="space-y-4">
              <div class="flex items-center justify-between">
                <h4 class="text-sm font-black text-gray-900">正文摘要</h4>
                <span class="text-[10px] font-black uppercase tracking-[0.22em] text-gray-400">Summary</span>
              </div>
              <div class="rounded-[28px] bg-white p-6 shadow-sm border border-gray-100 space-y-4">
                <p v-for="paragraph in selectedScrapedDetail.synopsis" :key="paragraph" class="text-sm leading-7 text-gray-600">
                  {{ paragraph }}
                </p>
              </div>
            </section>

            <section class="space-y-4">
              <div class="flex items-center justify-between">
                <h4 class="text-sm font-black text-gray-900">结构大纲</h4>
                <span class="text-[10px] font-black uppercase tracking-[0.22em] text-gray-400">Outline</span>
              </div>
              <div class="space-y-4">
                <div v-for="section in selectedScrapedDetail.outline" :key="section.title" class="rounded-[28px] bg-[linear-gradient(180deg,_rgba(255,255,255,0.98),_rgba(249,250,251,0.96))] p-6 shadow-sm border border-gray-100">
                  <h5 class="text-base font-black text-gray-900">{{ section.title }}</h5>
                  <ul class="mt-4 space-y-3 text-sm leading-6 text-gray-600">
                    <li v-for="bullet in section.bullets" :key="bullet" class="flex items-start gap-3">
                      <span class="mt-2 h-1.5 w-1.5 rounded-full bg-indigo-500"></span>
                      <span>{{ bullet }}</span>
                    </li>
                  </ul>
                </div>
              </div>
            </section>

            <section class="space-y-4">
              <div class="flex items-center justify-between">
                <h4 class="text-sm font-black text-gray-900">资料标签</h4>
                <span class="text-[10px] font-black uppercase tracking-[0.22em] text-gray-400">Meta</span>
              </div>
              <div class="flex flex-wrap gap-3">
                <span v-for="highlight in selectedScrapedDetail.highlights" :key="highlight" class="rounded-full bg-gray-100 px-4 py-2 text-xs font-bold text-gray-600">
                  {{ highlight }}
                </span>
              </div>
            </section>
          </div>
        </aside>
      </div>
    </Transition>

    <!-- Modals -->
    <Transition name="fade">
      <div v-if="showUploadModal" class="fixed inset-0 z-50 flex items-center justify-center p-6">
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="closeUploadModal"></div>
        <div class="relative bg-white w-full max-w-[500px] rounded-[32px] shadow-2xl overflow-hidden flex flex-col animate-in fade-in zoom-in duration-300">
          <div class="px-8 py-6 flex items-center justify-between">
            <h3 class="text-xl font-black text-gray-900">上传本地教学资料</h3>
            <button @click="closeUploadModal" class="p-2 hover:bg-gray-50 rounded-xl text-gray-400 hover:text-gray-900 transition-all">
              <X class="w-5 h-5" />
            </button>
          </div>
          <div class="p-8 space-y-6">
            <input ref="fileInput" type="file" class="hidden" @change="handleLocalFileChange" />
            <div @click="triggerLocalUpload" class="h-[200px] bg-gray-50 border-2 border-dashed rounded-[24px] flex flex-col items-center justify-center gap-4 group transition-all cursor-pointer" :class="selectedLocalUploadName ? 'border-indigo-400 bg-indigo-50/40' : 'border-gray-200 hover:bg-gray-100'">
              <div class="w-16 h-16 bg-white rounded-2xl flex items-center justify-center text-gray-400 group-hover:text-indigo-600 group-hover:scale-110 transition-all shadow-sm" :class="selectedLocalUploadName ? 'text-indigo-600' : ''">
                <CloudUpload class="w-8 h-8" />
              </div>
              <div class="text-center space-y-1">
                <p class="text-sm font-bold text-gray-900">{{ selectedLocalUploadName || '点击或将文件拖拽至此' }}</p>
                <p class="text-[10px] text-gray-400 font-medium">{{ selectedLocalUploadName ? '文件已选中，点击可重新选择' : '支持 PDF / DOCX / PPTX / TXT / Markdown / 图片扫描件 (最大 50MB)' }}</p>
              </div>
            </div>
            <div v-if="uploadedLocalFiles.length > 0" class="space-y-2">
              <div class="text-[10px] font-black text-gray-400 uppercase tracking-widest">最近上传</div>
              <div class="space-y-2">
                <div v-for="item in uploadedLocalFiles" :key="item" class="flex items-center justify-between p-3 bg-white rounded-xl shadow-sm border border-gray-50">
                  <div class="flex items-center gap-3">
                    <FileText class="w-4 h-4 text-indigo-600" />
                    <span class="text-xs font-bold text-gray-700">{{ item }}</span>
                  </div>
                  <span class="text-[10px] font-bold text-green-600">✓ 已上传</span>
                </div>
              </div>
            </div>
          </div>
          <div class="px-8 py-5 bg-gray-50/60 border-t border-gray-100 flex items-center justify-end gap-3">
            <button @click="closeUploadModal" class="px-5 py-2.5 text-sm font-bold text-gray-500 hover:text-gray-900 transition-colors rounded-xl hover:bg-gray-100">取消</button>
            <button
              @click="handleConfirmUpload"
              :disabled="!selectedLocalFileObject || isUploading"
              class="px-7 py-3 rounded-2xl text-sm font-black text-white shadow-lg transition-all"
              :class="selectedLocalFileObject && !isUploading ? 'bg-indigo-600 hover:opacity-90 shadow-indigo-200' : 'bg-gray-300 cursor-not-allowed shadow-none'"
            >
              {{ isUploading ? '正在上传...' : '🚀 确认上传' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <Transition name="fade">
      <div v-if="showCloudImportModal" class="fixed inset-0 z-50 flex items-center justify-center p-6">
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="showCloudImportModal = false"></div>
        <div class="relative bg-white w-full max-w-[600px] rounded-[32px] shadow-2xl overflow-hidden flex flex-col animate-in fade-in zoom-in duration-300">
          <div class="px-8 py-6 flex items-center justify-between border-b border-gray-50">
            <h3 class="text-xl font-black text-gray-900">从云端导入资料</h3>
            <button @click="showCloudImportModal = false" class="p-2 hover:bg-gray-50 rounded-xl text-gray-400 hover:text-gray-900 transition-all">
              <X class="w-5 h-5" />
            </button>
          </div>
          <div class="p-8 space-y-6">
            <div class="relative">
              <Search class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input 
                v-model="cloudSearchQuery"
                type="text" 
                placeholder="搜索云盘、课程库..." 
                class="w-full bg-gray-50 border-none rounded-2xl py-4 pl-12 pr-6 text-sm focus:ring-2 focus:ring-indigo-500/20 outline-none"
              />
            </div>
            <div class="grid grid-cols-2 gap-4 max-h-[300px] overflow-y-auto custom-scrollbar">
              <div 
                v-for="card in filteredScrapedCards" 
                :key="card.id"
                @click="toggleCloudItem(card.id)"
                class="p-4 rounded-2xl border-2 transition-all cursor-pointer flex flex-col gap-2"
                :class="selectedCloudItems.includes(card.id) ? 'border-indigo-600 bg-indigo-50' : 'border-transparent bg-gray-50 hover:bg-gray-100'"
              >
                <span class="text-sm font-bold text-gray-900">{{ card.title }}</span>
                <span class="text-[10px] text-gray-400">{{ card.type }}</span>
              </div>
            </div>
          </div>
          <div class="px-8 py-6 bg-gray-50/50 flex items-center justify-end gap-4">
            <button @click="showCloudImportModal = false" class="px-6 py-3 text-sm font-bold text-gray-500 hover:text-gray-900 transition-colors">取消</button>
            <button 
              @click="handleCloudImport"
              :disabled="isImporting"
              class="px-8 py-4 bg-indigo-600 text-white rounded-2xl text-sm font-black shadow-xl shadow-indigo-100 hover:opacity-90 transition-all"
            >
              {{ isImporting ? '导入中...' : `确认导入 (${selectedCloudItems.length})` }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <Transition name="fade">
      <div v-if="showCreateScrapeModal" class="fixed inset-0 z-50 flex items-center justify-center p-6">
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="showCreateScrapeModal = false"></div>
        <div class="relative bg-white w-full max-w-[560px] rounded-[32px] shadow-2xl overflow-hidden flex flex-col animate-in fade-in zoom-in duration-300">
          <div class="px-8 py-6 flex items-center justify-between border-b border-gray-50">
            <h3 class="text-xl font-black text-gray-900">新建 AI 全网抓取任务</h3>
            <button @click="showCreateScrapeModal = false" class="p-2 hover:bg-gray-50 rounded-xl text-gray-400 hover:text-gray-900 transition-all">
              <X class="w-5 h-5" />
            </button>
          </div>
          <div class="p-8 space-y-8">
            <div class="space-y-3">
              <label class="text-sm font-black text-gray-900">探索主题 (核心)</label>
              <div class="relative">
                <Search class="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input 
                  v-model="scrapeTaskForm.topic"
                  type="text" 
                  placeholder="输入知识点或教学主题，如：量子纠缠原理" 
                  class="w-full bg-gray-50 border-none rounded-2xl py-4 pl-12 pr-6 text-sm focus:ring-2 focus:ring-indigo-500/20 outline-none"
                />
              </div>
            </div>
            <div class="space-y-3">
              <label class="text-sm font-black text-gray-900">抓取来源 (多选)</label>
              <div class="flex flex-wrap gap-3">
                <button 
                  v-for="source in ['Bilibili', '知网', 'Coursera', 'YouTube', '学术博客']" 
                  :key="source"
                  @click="toggleScrapeSource(source)"
                  class="px-4 py-2 rounded-xl text-xs font-bold transition-all border-2"
                  :class="scrapeTaskForm.sources.includes(source) ? 'bg-indigo-600 text-white border-indigo-600' : 'bg-gray-50 text-gray-500 border-transparent hover:bg-gray-100'"
                >
                  {{ source }}
                </button>
              </div>
            </div>
          </div>
          <div class="px-8 py-6 bg-gray-50/50 flex items-center justify-end gap-4">
            <button @click="showCreateScrapeModal = false" class="px-6 py-3 text-sm font-bold text-gray-500 hover:text-gray-900 transition-colors">取消</button>
            <button 
              @click="handleCreateScrapeTask"
              :disabled="isScraping"
              class="px-8 py-4 bg-indigo-600 text-white rounded-2xl text-sm font-black shadow-xl shadow-indigo-100 hover:opacity-90 transition-all"
            >
              {{ isScraping ? '启动中...' : '启动 AI 抓取' }}
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
