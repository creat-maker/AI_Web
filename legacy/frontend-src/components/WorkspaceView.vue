<script setup lang="ts">
import confetti from 'canvas-confetti';
import { marked } from 'marked';
import markedKatex from 'marked-katex-extension';
import 'katex/dist/katex.min.css';
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import { apiClient } from '../api/client';
import {
  renderMarkdown,
  resolveGameCards,
  resolveMarkdownSource,
  resolvePptSlides,
  resolveVideoScenes,
} from '../utils/content';
import PhysicsAnimation from './PhysicsAnimation.vue';
import {
  LORENTZ_DEMO_ANIMATION_HTML,
  LORENTZ_DEMO_STAGE_MESSAGES,
  type LorentzDemoContext,
  buildLorentzDemoBlogEntry,
  buildLorentzDemoGameEntry,
  buildLorentzDemoLessonPlanEntry,
  buildLorentzDemoPptEntry,
  buildLorentzDemoVideoEntry,
  getLorentzDemoDelayMs,
  isLorentzDemoTarget,
  waitForLorentzDemoDelay,
} from '../utils/lorentzDemo';
import {
  Plus,
  Zap,
  FileText,
  ChevronLeft,
  ChevronRight,
  Check,
  RotateCw,
  FileQuestion,
  Send,
  Loader2,
  Trash2,
  X,
  MonitorSmartphone,
  MessageSquare,
  Link,
  Presentation,
  Gamepad2,
  FileJson,
  Video,
  AlertCircle,
  Paperclip,
  FlaskConical,
  GraduationCap,
} from 'lucide-vue-next';
import type {
  AttachmentRecord,
  GeneratedContentEntry,
  GeneratorComposeResponse,
  ProjectDetail,
} from '../types';
import {
  isLessonPlanRewriteActive,
  isRegenerating,
  resetWorkspaceLessonPlanRewrite,
  setWorkspaceLessonPlan,
  workspaceData,
} from '@/composables/useWorkspaceState';

type GameDeckCard = {
  id: string;
  front: string;
  back: string;
  reviewCount: number;
};

type SwipeAction = 'mastered' | 'review';

const props = defineProps<{
  initialTasks?: string[];
  projectId?: number | null;
  projectName?: string;
  generationRequirement?: string;
  autoGenerateToken?: number;
  mockTemplate?: string;
}>();

const tabs = [
  { id: 'ppt', name: '演示文稿', icon: Presentation },
  { id: 'lesson-plan', name: '标准教案', icon: FileText },
  { id: 'video', name: '短视频', icon: Video },
  { id: 'game', name: '互动游戏', icon: Gamepad2 },
  { id: 'blog', name: '教学博客', icon: FileJson },
  { id: 'flashcards', name: '知识闪卡', icon: GraduationCap },
];

const activeTab = ref(props.initialTasks?.[0] || 'ppt');
const generatedTools = ref<string[]>(props.initialTasks || []);
const attachments = ref<AttachmentRecord[]>([]);
const projectDetail = ref<ProjectDetail | null>(null);
const showMaterialChangeAlert = ref(false);
const showAttachments = ref(false);
const isProjectLoading = ref(false);
const isUploading = ref(false);
const isPackaging = ref(false);
const generatingToolIds = ref<string[]>([]);
const generationProgress = ref(0);
const generationStatus = ref('');
const fileInput = ref<HTMLInputElement | null>(null);
const lastAutoGenerateKey = ref('');

const isGeneratingQuiz = ref(false);
const showDistributeModal = ref(false);
const showToast = ref(false);
const toastMessage = ref('');
const selectedChannels = ref<string[]>([]);
const selectedClasses = ref<string[]>([]);
const quizzes = ref<{ id: number; question: string; options: string[]; answer: number }[]>([]);
const isDistributionMockLoading = ref(false);
const showLorentzAnimation = ref(false);
const lorentzAnimationHtml = ref('');
const route = useRoute();
const isAiGamesMode = ref(false);
const showAiPptDemo = ref(false);
const isAiPptDemoMode = computed(() => showAiPptDemo.value || route.query.demoMode === 'ai-ppt');
const activeGameIndex = ref(0);
const aiGames = [
  { id: 0, title: '视觉任务挑战赛', file: '/视觉任务挑战赛-课前.html', tag: '课前预热' },
  { id: 1, title: '模型训练模拟器', file: '/模型训练模拟器-课中.html', tag: '课中核心' },
  { id: 2, title: '食品识别体验', file: '/food-recognition-simple.html', tag: '课后拓展' },
];
const isGenerating = ref(false);
const isGenerated = ref(false);
const aiDemoCurrentCardIndex = ref(0);
const isAiDemoCardFlipped = ref(false);
const aiDemoFlashcards = ref([
  {
    q: '什么是计算机视觉 (CV)？',
    a: '让计算机像人类一样“看”懂图像和视频的技术，常用于人脸识别和自动驾驶。',
  },
  {
    q: '监督学习与无监督学习的核心区别？',
    a: '监督学习的训练数据带有“标签”（标准答案），而无监督学习的数据没有标签，靠算法自行发现规律。',
  },
  {
    q: '什么是“过拟合 (Overfitting)”？',
    a: '模型在训练数据上表现极好，但在没见过的新数据上表现很差，就像“死记硬背”的学生不会举一反三。',
  },
]);
const aiDemoCurrentFlashcard = computed(() => (
  aiDemoFlashcards.value[aiDemoCurrentCardIndex.value] || aiDemoFlashcards.value[0]
));
const momentumAnalysis = {
  difficulty: 65,
  coverage: 85,
  warning: '学情预估：学生对"系统内力远大于外力时动量近似守恒"的条件容易混淆，建议在【交互探索】环节增加"开启/关闭桌面摩擦力"的对比演示。',
};
const gameDeck = ref<GameDeckCard[]>([]);
const masteredCardIds = ref<string[]>([]);
const streakCount = ref(0);
const isGameAnimating = ref(false);
const isTopCardFlipped = ref(false);
const swipeOffsetX = ref(0);
const swipeOffsetY = ref(0);
const activeSwipeAction = ref<SwipeAction | null>(null);
const activePointerId = ref<number | null>(null);
const pointerStartX = ref(0);
const pointerStartY = ref(0);
const pointerHasMoved = ref(false);

const distributionChannels = [
  {
    id: 'digital-human',
    title: '分发至数字人助教答疑库',
    description: '学生可通过对话向 AI 助教追问知识点。',
    tag: '实时答疑',
    icon: MessageSquare,
  },
  {
    id: 'tablet',
    title: '同步至学生平板端',
    description: '作业、素材与互动指令会同步出现在学生学习设备。',
    tag: '班级终端',
    icon: MonitorSmartphone,
  },
  {
    id: 'h5',
    title: '导出为互动 H5 链接',
    description: '自动生成可分享链接，方便在班级群与家校端流转。',
    tag: 'H5 分享',
    icon: Link,
  },
];

const distributionClassOptions = ['高二1班', '高二2班', '高二3班', '高二4班'];
const streakGoal = 5;

marked.use(markedKatex({ throwOnError: false }));
marked.use({
  gfm: true,
  breaks: true,
});

const projectContents = computed(() => projectDetail.value?.contents || {});

// 动量守恒克隆展示模板数据
const MOMENTUM_MOCK_MARKDOWN = `# 《动量守恒实验的沉洸式课堂设计》

## 一、 核心教学目标

**物理观念：** 深刻理解系统动量守恒的条件，建立“碰撞前后系统总动量保持不变”的微观与宮观联系。

**科学思维：** 通过气垫导轨实验，运用理想化模型（忽略摩擦力），培养通过实验数据验证物理规律的实证思维。

**科学探究：** 设计对比实验，自主探究弹性/非弹性碰撞的差异，形成“提问—假设—实验—结论”闭环。

---

## 二、 教学环节设计

### 1. 创设情境 （5 分钟）

播放台球开球的慢动作视频（建议一 YouTube 或 B 站縇高速摄影），引入碰撞概念和动量守恒的直观感受。

> 🚀 **导入问题：** “为什么台球砸球后，No.1 球几乎自冻了，其他球却窘然射出？”

### 2. 交互探索 （15 分钟）

调用 **3D 物理引擎**，让学生在屏幕上拖拽不同质量的滑块进行对心碰撞：

- 设置两滑块质量相等 → 观察刻度变化
- 设置质量之比 1:3 → 记录碰前碰后送度
- 把数据填入表格，验证 $m_1v_1 + m_2v_2 = m_1v_1' + m_2v_2'$

### 3. 深度总结 （10 分钟）

推导动量守恒定律：

$$m_1v_1 + m_2v_2 = m_1v_1' + m_2v_2'$$

**适用条件：** 系统内力远大于外力（或合外力为零）时，系统总动量守恒。

---

## 三、 作业与评估

| 项目 | 内容 | 分値 |
|---|---|---|
| 实验报告 | 数据记录与误差分析 | 40分 |
| 公式推导 | 步骤完整性 | 30分 |
| 思考题 | 火箭推射场景应用 | 30分 |
`;


const parsedSlides = computed(() => (
  resolvePptSlides(projectContents.value.ppt).map((slide, index) => ({
    id: String(index + 1).padStart(2, '0'),
    title: slide.title,
    type: slide.type,
    subtitle: slide.subtitle,
    bullets: slide.bullets,
  }))
));

const lessonPlanMarkdown = computed(() => {
  if (props.mockTemplate === 'momentum') {
    return MOMENTUM_MOCK_MARKDOWN;
  }
  return resolveMarkdownSource(projectContents.value['lesson-plan']);
});

const videoMarkdown = computed(() => {
  const entry = projectContents.value.video;
  if (!entry || entry.format !== 'markdown') {
    return '';
  }

  return resolveMarkdownSource(entry);
});

const canExportPptx = computed(() => parsedSlides.value.length > 0);
const canExportDocx = computed(() => Boolean(lessonPlanMarkdown.value.trim()));
const canExportAssetPack = computed(() => canExportPptx.value || canExportDocx.value);

const lessonPlanHtml = computed(() => marked.parse(lessonPlanMarkdown.value || '') as string);
const renderedContent = computed(() => {
  const content = workspaceData.value.content || '';
  if (!content.trim()) {
    return '';
  }
  return workspaceData.value.contentFormat === 'html'
    ? content
    : marked.parse(content) as string;
});
const videoHtml = computed(() => renderMarkdown(videoMarkdown.value));
const hasVideoMarkdown = computed(() => Boolean(videoMarkdown.value.trim()));

const videoScenes = computed(() => {
  return resolveVideoScenes(projectContents.value.video);
});

const gameCards = computed(() => {
  return resolveGameCards(projectContents.value.game);
});

const gameCardsSignature = computed(() => gameCards.value.map((card) => `${card.front}::${card.back}`).join('||'));

const blogMarkdown = computed(() => {
  return resolveMarkdownSource(projectContents.value.blog);
});

const blogHtml = computed(() => marked.parse(blogMarkdown.value || '') as string);
const stackedGameCards = computed(() => gameDeck.value.slice(0, 3));
const topGameCard = computed(() => stackedGameCards.value[0] ?? null);
const completedGameCount = computed(() => masteredCardIds.value.length);
const overallGameProgress = computed(() => (
  gameCards.value.length === 0 ? 0 : Math.round((completedGameCount.value / gameCards.value.length) * 100)
));
const streakProgress = computed(() => Math.min((streakCount.value / streakGoal) * 100, 100));
const swipePreviewAction = computed<SwipeAction | null>(() => {
  if (swipeOffsetX.value >= 90) return 'mastered';
  if (swipeOffsetX.value <= -90) return 'review';
  return null;
});
const gameStatusLabel = computed(() => {
  if (gameDeck.value.length === 0) return '本轮卡片已全部刷完';
  if (activeSwipeAction.value === 'mastered' || swipePreviewAction.value === 'mastered') return '松手即可标记为已掌握';
  if (activeSwipeAction.value === 'review' || swipePreviewAction.value === 'review') return '松手后将回到底部稍后复习';
  return '点击翻面查看解释，左右滑动决定去向';
});
const pendingReviewCount = computed(() => gameDeck.value.filter((card) => card.reviewCount > 0).length);
const isDistributionReady = computed(() => selectedChannels.value.length > 0 && selectedClasses.value.length > 0);
const canGenerateWithoutAttachments = computed(() => Boolean(currentRequirement().trim()));
const isGeneratingContent = computed(() => generatingToolIds.value.includes(activeTab.value));
const isLorentzDemoProject = computed(() => isLorentzDemoTarget({
  projectName: props.projectName || projectDetail.value?.name || '',
}));
const shouldShowSharedLessonPlan = computed(() => (
  activeTab.value === 'lesson-plan' && (isGenerated.value || isLessonPlanRewriteActive.value || isRegenerating.value)
));
const lorentzDemoToolIds = ['ppt', 'lesson-plan', 'game', 'blog', 'video'] as const;

// ── 知识闪卡 ──────────────────────────────────────────────────────────────────
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

const flashcardData = computed(() => LORENTZ_FLASHCARDS);
const flashcardQueue = ref<number[]>([]);
const flashcardMasteredCount = ref(0);
const isFlashcardFlipped = ref(false);
const flashcardIsAnimating = ref(false);
const flashcardExitClass = ref('');

const currentFlashcard = computed(() =>
  flashcardQueue.value.length > 0 ? (flashcardData.value[flashcardQueue.value[0]] ?? null) : null,
);

const renderFlashcardContent = (text: string) => marked.parse(text) as string;

const resetFlashcards = () => {
  flashcardQueue.value = Array.from({ length: flashcardData.value.length }, (_, i) => i);
  flashcardMasteredCount.value = 0;
  isFlashcardFlipped.value = false;
  flashcardExitClass.value = '';
  flashcardIsAnimating.value = false;
};

const settleFlashcard = (action: 'mastered' | 'review') => {
  if (flashcardIsAnimating.value || flashcardQueue.value.length === 0) return;
  flashcardIsAnimating.value = true;
  flashcardExitClass.value = action === 'mastered' ? 'fc-exit-right' : 'fc-exit-left';

  window.setTimeout(() => {
    const [head, ...rest] = flashcardQueue.value;
    if (action === 'mastered') {
      flashcardMasteredCount.value += 1;
      flashcardQueue.value = rest;
    } else if (head !== undefined) {
      flashcardQueue.value = [...rest, head];
    }
    isFlashcardFlipped.value = false;
    flashcardExitClass.value = 'fc-enter-pop';
    window.setTimeout(() => {
      flashcardExitClass.value = '';
      flashcardIsAnimating.value = false;
    }, 320);
  }, 420);
};

const currentCardIndex = ref(0);
const handleNextCard = (action: 'mastered' | 'review') => {
  if (flashcardIsAnimating.value) return;
  isFlashcardFlipped.value = false;
  flashcardIsAnimating.value = true;
  if (action === 'mastered') {
    flashcardMasteredCount.value += 1;
  }
  window.setTimeout(() => {
    currentCardIndex.value = (currentCardIndex.value + 1) % LORENTZ_FLASHCARDS.length;
    flashcardIsAnimating.value = false;
  }, 300);
};

const hasGeneratedContent = (toolId: string) => {
  if (toolId === 'lesson-plan' && isGenerated.value) return true;
  return Boolean(projectContents.value[toolId]);
};
const isToolGenerating = (toolId: string) => generatingToolIds.value.includes(toolId);

const setLorentzAnimationState = (enabled: boolean, animationHtml = '') => {
  showLorentzAnimation.value = enabled;
  lorentzAnimationHtml.value = enabled ? animationHtml : '';
};

const setToolGenerating = (toolId: string, generating: boolean) => {
  if (generating) {
    if (!generatingToolIds.value.includes(toolId)) {
      generatingToolIds.value = [...generatingToolIds.value, toolId];
    }
    return;
  }

  generatingToolIds.value = generatingToolIds.value.filter((id) => id !== toolId);
};

const resetGameInteractionState = () => {
  activePointerId.value = null;
  pointerHasMoved.value = false;
  swipeOffsetX.value = 0;
  swipeOffsetY.value = 0;
  activeSwipeAction.value = null;
  isGameAnimating.value = false;
};

const rebuildGameDeck = () => {
  gameDeck.value = gameCards.value.map((card, index) => ({
    id: `game-${index}-${card.front}-${card.back}`,
    front: card.front,
    back: card.back,
    reviewCount: 0,
  }));
  masteredCardIds.value = [];
  streakCount.value = 0;
  isTopCardFlipped.value = false;
  resetGameInteractionState();
};

const getStackCardStyle = (depth: number) => {
  const scale = 1 - depth * 0.06;
  const translateY = depth * 18;
  const translateZ = -depth * 72;

  if (depth === 0) {
    return {
      transform: `translate3d(${swipeOffsetX.value}px, ${swipeOffsetY.value}px, ${translateZ}px) rotate(${swipeOffsetX.value / 18}deg) scale(1)`,
      opacity: '1',
      zIndex: '30',
    };
  }

  return {
    transform: `translate3d(0, ${translateY}px, ${translateZ}px) scale(${scale})`,
    opacity: String(1 - depth * 0.24),
    zIndex: String(30 - depth),
  };
};

const triggerCompletionConfetti = () => {
  const burst = (originX: number, particleCount: number, delay: number) => {
    window.setTimeout(() => {
      confetti({
        angle: originX < 0.5 ? 60 : 120,
        origin: { x: originX, y: 0.72 },
        particleCount,
        spread: 80,
        startVelocity: 42,
        ticks: 220,
        zIndex: 999,
      });
    }, delay);
  };

  burst(0.18, 120, 0);
  burst(0.5, 180, 180);
  burst(0.82, 120, 320);
};

const settleGameCard = (action: SwipeAction) => {
  if (!topGameCard.value || isGameAnimating.value) {
    return;
  }

  isGameAnimating.value = true;
  activeSwipeAction.value = action;
  swipeOffsetX.value = action === 'mastered' ? 460 : -460;
  swipeOffsetY.value = action === 'mastered' ? -18 : 26;
  streakCount.value = action === 'mastered' ? streakCount.value + 1 : 0;

  window.setTimeout(() => {
    const [currentCard, ...rest] = gameDeck.value;
    if (!currentCard) {
      resetGameInteractionState();
      return;
    }

    if (action === 'mastered') {
      masteredCardIds.value = [...masteredCardIds.value, currentCard.id];
      gameDeck.value = rest;
    } else {
      gameDeck.value = [...rest, { ...currentCard, reviewCount: currentCard.reviewCount + 1 }];
    }

    isTopCardFlipped.value = false;
    resetGameInteractionState();

    if (gameDeck.value.length === 0) {
      triggerCompletionConfetti();
      showToastMessage('🎉 互动卡片全部刷完，当前知识点已完成一轮掌握！');
    }
  }, 520);
};

const handleGameDecision = (action: SwipeAction) => {
  settleGameCard(action);
};

const handleCardPointerDown = (event: PointerEvent) => {
  if (!topGameCard.value || isGameAnimating.value) {
    return;
  }

  activePointerId.value = event.pointerId;
  pointerStartX.value = event.clientX;
  pointerStartY.value = event.clientY;
  pointerHasMoved.value = false;
  (event.currentTarget as HTMLElement | null)?.setPointerCapture?.(event.pointerId);
};

const handleCardPointerMove = (event: PointerEvent) => {
  if (activePointerId.value !== event.pointerId || isGameAnimating.value) {
    return;
  }

  const deltaX = event.clientX - pointerStartX.value;
  const deltaY = event.clientY - pointerStartY.value;
  if (Math.abs(deltaX) > 4 || Math.abs(deltaY) > 4) {
    pointerHasMoved.value = true;
  }

  swipeOffsetX.value = deltaX;
  swipeOffsetY.value = deltaY * 0.18;
};

const handleCardPointerUp = (event: PointerEvent) => {
  if (activePointerId.value !== event.pointerId) {
    return;
  }

  (event.currentTarget as HTMLElement | null)?.releasePointerCapture?.(event.pointerId);
  activePointerId.value = null;

  if (!pointerHasMoved.value && Math.abs(swipeOffsetX.value) < 6 && Math.abs(swipeOffsetY.value) < 6) {
    isTopCardFlipped.value = !isTopCardFlipped.value;
    swipeOffsetX.value = 0;
    swipeOffsetY.value = 0;
    return;
  }

  if (swipeOffsetX.value >= 110) {
    handleGameDecision('mastered');
    return;
  }

  if (swipeOffsetX.value <= -110) {
    handleGameDecision('review');
    return;
  }

  swipeOffsetX.value = 0;
  swipeOffsetY.value = 0;
};

const handleCardPointerCancel = (event: PointerEvent) => {
  if (activePointerId.value === event.pointerId) {
    (event.currentTarget as HTMLElement | null)?.releasePointerCapture?.(event.pointerId);
    resetGameInteractionState();
  }
};

const formatFileSize = (size: number) => {
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
};

const extractErrorDetail = (error: unknown) => {
  if (error && typeof error === 'object') {
    const responseError = error as {
      response?: { data?: { detail?: unknown; message?: unknown } };
      message?: unknown;
    };

    const detail = responseError.response?.data?.detail;
    if (typeof detail === 'string' && detail.trim()) {
      return detail;
    }

    const message = responseError.response?.data?.message;
    if (typeof message === 'string' && message.trim()) {
      return message;
    }

    if (typeof responseError.message === 'string' && responseError.message.trim()) {
      return responseError.message;
    }
  }

  return error instanceof Error ? error.message : '请求失败，请稍后重试';
};

const getCurrentAttachmentList = () => {
  const projectAttachments = projectDetail.value?.attachments || [];
  return projectAttachments.length > 0 ? projectAttachments : attachments.value;
};

const showToastMessage = (message: string) => {
  toastMessage.value = message;
  showToast.value = true;
  window.setTimeout(() => {
    showToast.value = false;
  }, 3000);
};

const handlePackageDownload = async () => {
  if (isPackaging.value) {
    return;
  }

  isPackaging.value = true;

  try {
    await new Promise((resolve) => {
      window.setTimeout(resolve, 2000);
    });

    const mockContent = `【织课 AI 自动生成课件包】

包含文件：
1. 视觉任务挑战赛-课前.html
2. 模型训练模拟器-课中.html
3. 食品识别体验.html

注意：此为演示环境的打包文件。`;
    const blob = new Blob([mockContent], { type: 'application/zip' });
    const downloadUrl = window.URL.createObjectURL(blob);
    const anchor = document.createElement('a');
    anchor.href = downloadUrl;
    anchor.download = '人工智能应用基础_互动课件包.zip';
    anchor.style.display = 'none';
    document.body.appendChild(anchor);
    anchor.click();
    document.body.removeChild(anchor);
    window.setTimeout(() => {
      window.URL.revokeObjectURL(downloadUrl);
    }, 1000);
    showToastMessage('课件打包成功，已开始下载！');
  } finally {
    isPackaging.value = false;
  }
};

const syncProjectState = (detail: ProjectDetail) => {
  projectDetail.value = detail;
  attachments.value = detail.attachments || [];
  generatedTools.value = Array.from(new Set([...(props.initialTasks || []), ...Object.keys(detail.contents || {})]));
  if (isLorentzDemoTarget({ projectName: detail.name })) {
    const hasLorentzGameContent = Boolean(detail.contents?.game);
    setLorentzAnimationState(
      hasLorentzGameContent,
      hasLorentzGameContent ? (lorentzAnimationHtml.value || LORENTZ_DEMO_ANIMATION_HTML) : '',
    );
    return;
  }

  setLorentzAnimationState(false);
};

const currentRequirement = () => props.generationRequirement?.trim() || projectDetail.value?.description || props.projectName || '请根据参考资料生成可直接使用的教学初稿';

const resolveLessonPlanTitle = (content: string) => {
  const headingMatch = content.match(/^#\s+(.+)$/m);
  if (headingMatch?.[1]) {
    return headingMatch[1].trim();
  }
  return `${props.projectName || projectDetail.value?.name || '当前课程'}教案`;
};

const updateToolContent = (toolId: string, entry: GeneratedContentEntry) => {
  if (!projectDetail.value) {
    return;
  }

  projectDetail.value = {
    ...projectDetail.value,
    contents: {
      ...(projectDetail.value.contents || {}),
      [toolId]: entry,
    },
  };
};

const applyLorentzDemoBundle = (demoContext: LorentzDemoContext) => {
  updateToolContent('ppt', buildLorentzDemoPptEntry(demoContext));
  updateToolContent('lesson-plan', buildLorentzDemoLessonPlanEntry(demoContext));
  updateToolContent('game', buildLorentzDemoGameEntry(demoContext));
  updateToolContent('blog', buildLorentzDemoBlogEntry(demoContext));
  updateToolContent('video', buildLorentzDemoVideoEntry(demoContext));
  setLorentzAnimationState(true, LORENTZ_DEMO_ANIMATION_HTML);
};

const requestToolGeneration = async (toolId: string, attachmentContext: AttachmentRecord[] = getCurrentAttachmentList()) => {
  if (!props.projectId) {
    showToastMessage('请先创建或打开项目');
    return;
  }

  const currentProjectName = props.projectName || projectDetail.value?.name || '';
  const attachmentIds = attachmentContext
    .map((item) => item.id)
    .filter((id) => Number.isInteger(id) && id > 0);
  const sourceFiles = attachmentContext.map((item) => item.original_name).filter(Boolean);
  const demoModeActive = isLorentzDemoTarget({
    projectName: currentProjectName,
  });
  const demoContext = {
    projectName: currentProjectName,
    fileNames: sourceFiles,
    attachmentIds,
    sourceFiles,
    userRequirement: currentRequirement(),
  };

  setToolGenerating(toolId, true);
  const toolLabel = tabs.find((tab) => tab.id === toolId)?.name || toolId;

  if (demoModeActive) {
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

      applyLorentzDemoBundle(demoContext);
      const demoGeneratedTools = toolId === 'simulation'
        ? [...lorentzDemoToolIds, 'simulation']
        : [...lorentzDemoToolIds];
      generatedTools.value = Array.from(new Set([...generatedTools.value, ...demoGeneratedTools]));
      generationProgress.value = 100;
      showMaterialChangeAlert.value = false;
      window.dispatchEvent(new CustomEvent('ai-generation-complete', {
        detail: {
          toolLabel: tabs.find((t) => t.id === toolId)?.name || toolId,
          projectName: props.projectName || projectDetail.value?.name || '洛伦兹力',
        },
      }));
      return;
    } catch (error) {
      showToastMessage(`生成失败：${extractErrorDetail(error)}`);
    } finally {
      if (statusTimer) {
        window.clearInterval(statusTimer);
      }
      setToolGenerating(toolId, false);
      generationProgress.value = 0;
      generationStatus.value = '';
    }
  }

  generationProgress.value = 12;
  generationStatus.value = `✨ 正在为您自动生成【${toolLabel}】初稿，请稍候...`;

  const timer = window.setInterval(() => {
    generationProgress.value = Math.min(generationProgress.value + 9, 88);
  }, 350);

  try {
    const response = await apiClient.post<GeneratorComposeResponse>('/api/generator/compose', {
      project_id: props.projectId,
      attachment_ids: attachmentIds,
      generator_type: toolId,
      user_requirement: currentRequirement(),
      session_id: `workspace-${props.projectId}-${toolId}`,
    });
    const generatedEntry: GeneratedContentEntry = response.data.content;

    generationProgress.value = 100;
    updateToolContent(toolId, generatedEntry);
    if (toolId === 'game') {
      setLorentzAnimationState(Boolean(response.data.animation_html), response.data.animation_html || '');
    }
    if (!generatedTools.value.includes(toolId)) {
      generatedTools.value.push(toolId);
    }
    showMaterialChangeAlert.value = false;
    showToastMessage(`${tabs.find((tab) => tab.id === toolId)?.name || toolId} 已根据上传文档生成完成`);
    // 通知右侧伴写助手：生成完成，推送引导话术
    window.dispatchEvent(new CustomEvent('ai-generation-complete', {
      detail: {
        toolLabel: tabs.find((tab) => tab.id === toolId)?.name || toolId,
        projectName: props.projectName || projectDetail.value?.name || '当前课程',
      },
    }));
  } catch (error) {
    showToastMessage(`生成失败：${extractErrorDetail(error)}`);
  } finally {
    window.clearInterval(timer);
    setToolGenerating(toolId, false);
    generationProgress.value = 0;
    generationStatus.value = '';
  }
};

const batchLorentzDemoGenerate = async (toolIds: string[]) => {
  const currentProjectName = props.projectName || projectDetail.value?.name || '';
  const attachmentContext = getCurrentAttachmentList();
  const attachmentIds = attachmentContext.map((item) => item.id).filter((id) => Number.isInteger(id) && id > 0);
  const sourceFiles = attachmentContext.map((item) => item.original_name).filter(Boolean);
  const demoContext = {
    projectName: currentProjectName,
    fileNames: sourceFiles,
    attachmentIds,
    sourceFiles,
    userRequirement: currentRequirement(),
  };
  const demoGeneratedTools = Array.from(new Set([
    ...lorentzDemoToolIds,
    ...toolIds.filter((toolId) => toolId === 'simulation'),
  ]));

  demoGeneratedTools.forEach((id) => setToolGenerating(id, true));
  let stageIndex = 0;
  generationProgress.value = 12;
  generationStatus.value = LORENTZ_DEMO_STAGE_MESSAGES[stageIndex];
  const statusTimer = window.setInterval(() => {
    stageIndex = (stageIndex + 1) % LORENTZ_DEMO_STAGE_MESSAGES.length;
    generationStatus.value = LORENTZ_DEMO_STAGE_MESSAGES[stageIndex];
    generationProgress.value = Math.min(generationProgress.value + 18, 90);
  }, 1000);

  try {
    await waitForLorentzDemoDelay(getLorentzDemoDelayMs());
    applyLorentzDemoBundle(demoContext);
    generatedTools.value = Array.from(new Set([...generatedTools.value, ...demoGeneratedTools]));
    generationProgress.value = 100;
    showMaterialChangeAlert.value = false;
    window.dispatchEvent(new CustomEvent('ai-generation-complete', {
      detail: {
        toolLabel: toolIds.map((id) => tabs.find((t) => t.id === id)?.name || id).join(' / '),
        projectName: currentProjectName || '洛伦兹力',
      },
    }));
  } finally {
    window.clearInterval(statusTimer);
    demoGeneratedTools.forEach((id) => setToolGenerating(id, false));
    generationProgress.value = 0;
    generationStatus.value = '';
  }
};

const maybeAutoGenerate = async () => {
  if (!props.projectId || !props.autoGenerateToken || !projectDetail.value) {
    return;
  }
  const autoKey = `${props.projectId}-${props.autoGenerateToken}`;
  if (lastAutoGenerateKey.value === autoKey) {
    return;
  }
  lastAutoGenerateKey.value = autoKey;

  const targets = (props.initialTasks?.length ? props.initialTasks : [activeTab.value]).filter((toolId) => !hasGeneratedContent(toolId) && toolId !== 'simulation');
  const allTargets = (props.initialTasks?.length ? props.initialTasks : [activeTab.value]).filter((toolId) => !hasGeneratedContent(toolId));
  if (allTargets.length === 0) {
    return;
  }

  activeTab.value = props.initialTasks?.[0] || allTargets[0] || activeTab.value;

  // In Lorentz demo mode with multiple tools: batch-inject all at once with a single animation pass
  if (isLorentzDemoProject.value && allTargets.length > 0) {
    await batchLorentzDemoGenerate(allTargets);
    return;
  }

  for (const toolId of targets) {
    await requestToolGeneration(toolId);
  }
};

const loadProject = async () => {
  if (!props.projectId) {
    projectDetail.value = null;
    attachments.value = [];
    return;
  }

  isProjectLoading.value = true;
  try {
    const response = await apiClient.get<ProjectDetail>(`/api/projects/${props.projectId}`);
    syncProjectState(response.data);
    await maybeAutoGenerate();
  } catch (error) {
    showToastMessage(error instanceof Error ? error.message : '加载工作台失败');
  } finally {
    isProjectLoading.value = false;
  }
};

const promptAttachmentUpload = () => {
  if (!props.projectId) {
    showToastMessage('请先从首页创建或打开一个项目');
    return;
  }
  fileInput.value?.click();
};

const handlePlaceholderAction = (message: string) => {
  showToastMessage(message);
};

const handleAttachmentSelected = async (event: Event) => {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  if (!file || !props.projectId) return;

  isUploading.value = true;
  try {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.postForm<AttachmentRecord>(`/api/attachments/upload?project_id=${props.projectId}`, formData);
    attachments.value.unshift(response.data);
    if (projectDetail.value) {
      projectDetail.value = {
        ...projectDetail.value,
        attachments: [response.data, ...(projectDetail.value.attachments || [])],
      };
    }
    showMaterialChangeAlert.value = true;
    showToastMessage('附件上传成功，已同步到后端');
  } catch (error) {
    showToastMessage(error instanceof Error ? error.message : '上传附件失败');
  } finally {
    isUploading.value = false;
    input.value = '';
  }
};

const deleteAttachment = async (id: number) => {
  try {
    await apiClient.delete(`/api/attachments/${id}`);
    attachments.value = attachments.value.filter((attachment) => attachment.id !== id);
    if (projectDetail.value) {
      projectDetail.value = {
        ...projectDetail.value,
        attachments: attachments.value,
      };
    }
    showMaterialChangeAlert.value = true;
    showToastMessage('附件已删除');
  } catch (error) {
    showToastMessage(error instanceof Error ? error.message : '删除附件失败');
  }
};

const regenerateContent = async () => {
  showMaterialChangeAlert.value = false;
  await requestToolGeneration(activeTab.value);
};

const handleGenerate = async () => {
  if (isGeneratingContent.value) {
    return;
  }

  const currentAttachments = getCurrentAttachmentList();
  const demoModeActive = isLorentzDemoTarget({
    projectName: props.projectName || projectDetail.value?.name,
  });
  if (!demoModeActive && currentAttachments.length === 0) {
    showToastMessage('当前项目暂无资料，请先上传 PDF、DOCX、PPTX、TXT、Markdown 或图片扫描件后再生成');
    return;
  }

  await requestToolGeneration(activeTab.value, currentAttachments);
};

const addNewSlide = () => {
  const nextSlide = { title: '新幻灯片', bullets: ['请在此输入正文要点...'] };
  const existingEntry = projectContents.value.ppt;
  const existingSlides = resolvePptSlides(existingEntry);
  const nextEntry: GeneratedContentEntry = {
    format: 'json',
    data: [...existingSlides, nextSlide],
    raw_content: JSON.stringify([...existingSlides, nextSlide], null, 2),
    attachment_ids: existingEntry?.attachment_ids || [],
    source_files: existingEntry?.source_files || [],
    user_requirement: existingEntry?.user_requirement || currentRequirement(),
    updated_at: new Date().toISOString(),
  };

  updateToolContent('ppt', nextEntry);
  if (!generatedTools.value.includes('ppt')) {
    generatedTools.value.push('ppt');
  }
  activeTab.value = 'ppt';
  showToastMessage('已新增一页空白幻灯片');
};

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

const flipAiDemoCard = () => {
  isAiDemoCardFlipped.value = !isAiDemoCardFlipped.value;
};

const nextAiDemoCard = () => {
  if (aiDemoCurrentCardIndex.value < aiDemoFlashcards.value.length - 1) {
    aiDemoCurrentCardIndex.value += 1;
    isAiDemoCardFlipped.value = false;
  }
};

const openActiveGameInNewWindow = () => {
  const game = aiGames[activeGameIndex.value];
  if (!game) {
    return;
  }
  window.open(game.file, '_blank', 'noopener,noreferrer');
};

const generateQuiz = async () => {
  isGeneratingQuiz.value = true;
  try {
    const topicSource = lessonPlanMarkdown.value || blogMarkdown.value || projectDetail.value?.description || projectDetail.value?.name || '当前课程内容';
    const resp = await apiClient.post<{ question: string; options: string[]; answer: number }[]>('/api/avatar/generate-quiz', {
      session_id: `workspace-quiz-${props.projectId || 'global'}`,
      topic: topicSource.slice(0, 300),
      count: 5,
    });
    quizzes.value = resp.data.map((q, i) => ({ id: i + 1, ...q }));
  } catch {
    showToastMessage('AI 出题失败，请稍后重试');
  } finally {
    isGeneratingQuiz.value = false;
  }
};

const deleteQuiz = (id: number) => {
  quizzes.value = quizzes.value.filter((quiz) => quiz.id !== id);
};

const toggleSelection = (list: string[], item: string) => {
  const index = list.indexOf(item);
  if (index > -1) {
    list.splice(index, 1);
  } else {
    list.push(item);
  }
};

const confirmDistribution = async () => {
  if (!isDistributionReady.value || isDistributionMockLoading.value) return;

  isDistributionMockLoading.value = true;

  const selectedChannelSnapshot = [...selectedChannels.value];
  const selectedClassSnapshot = [...selectedClasses.value];
  const generatedLink = `https://mock.zhike.ai/share/${props.projectId || 'demo'}-${activeTab.value}-${Date.now().toString(36)}`;

  await new Promise((resolve) => {
    window.setTimeout(resolve, 1500);
  });

  let copiedH5Link = false;
  if (selectedChannelSnapshot.includes('h5') && typeof navigator !== 'undefined' && navigator.clipboard?.writeText) {
    try {
      await navigator.clipboard.writeText(generatedLink);
      copiedH5Link = true;
    } catch {
      copiedH5Link = false;
    }
  }

  showDistributeModal.value = false;
  isDistributionMockLoading.value = false;
  selectedChannels.value = [];
  selectedClasses.value = [];

  if (selectedChannelSnapshot.includes('h5')) {
    showToastMessage(copiedH5Link ? '🔗 H5 互动链接已生成并复制到剪贴板！' : '🔗 H5 互动链接已生成，可立即分享给学生！');
    return;
  }

  if (selectedClassSnapshot.length === 1) {
    showToastMessage(`🎉 任务已成功同步至【${selectedClassSnapshot[0]}】！`);
    return;
  }

  showToastMessage(`🎉 任务已成功同步至【${selectedClassSnapshot[0]}】等 ${selectedClassSnapshot.length} 个班级！`);
};

watch(
  () => props.projectId,
  () => {
    void loadProject();
  },
  { immediate: true },
);

// 克隆模板到工作台：自动切换到教案 tab
watch(
  () => props.mockTemplate,
  (tpl) => {
    if (tpl === 'momentum') {
      activeTab.value = 'lesson-plan';
    }
  },
  { immediate: true },
);

// 核心生成函数：触发动量守恒 mock 动画并注入数据
const triggerMomentumGeneration = () => {
  isGenerating.value = true;
  isGenerated.value = false;
  resetWorkspaceLessonPlanRewrite();
  setWorkspaceLessonPlan({
    title: '《动量守恒实验的沉浸式课堂设计》',
    content: '',
    contentFormat: 'html',
    analysis: momentumAnalysis,
  });
  activeTab.value = 'lesson-plan';
  window.setTimeout(() => {
    setWorkspaceLessonPlan({
      title: '《动量守恒实验的沉浸式课堂设计》',
      content: `
        <div class="prose max-w-none text-gray-800">
          <h2 class="text-2xl font-bold mb-4 text-indigo-900">一、 核心教学目标</h2>
          <p class="mb-2"><strong>1. 物理观念：</strong>深刻理解系统动量守恒的条件，建立"碰撞前后系统总动量保持不变"的微观与宏观联系。</p>
          <p class="mb-4"><strong>2. 科学思维：</strong>通过气垫导轨实验，运用理想化模型（忽略摩擦力），培养通过实验数据验证物理规律的实证思维。</p>
          <h2 class="text-2xl font-bold mt-8 mb-4 text-indigo-900">二、 教学环节设计</h2>
          <div class="pl-4 border-l-4 border-indigo-200 mb-4">
            <h3 class="text-lg font-semibold mb-1 text-indigo-700">环节一：创设情境 (5分钟)</h3>
            <p class="text-gray-600">播放台球开球的慢动作视频，引入碰撞概念。提问：碰撞前后，什么物理量可能保持不变？</p>
          </div>
          <div class="pl-4 border-l-4 border-indigo-200 mb-4">
            <h3 class="text-lg font-semibold mb-1 text-indigo-700">环节二：交互探索 (15分钟)</h3>
            <p class="text-gray-600">调用 3D 物理沙盒引擎，让学生在屏幕上拖拽不同质量的滑块进行对心碰撞，记录碰撞前后的速度。</p>
          </div>
          <div class="pl-4 border-l-4 border-indigo-200 mb-4">
            <h3 class="text-lg font-semibold mb-1 text-indigo-700">环节三：公式推导与总结 (10分钟)</h3>
            <p class="text-gray-600">引导学生发现 m₁v₁ + m₂v₂ = m₁v₁' + m₂v₂' 的规律，得出动量守恒定律。</p>
          </div>
          <h2 class="text-2xl font-bold mt-8 mb-4 text-indigo-900">三、 作业与评估</h2>
          <table class="w-full text-sm border-collapse">
            <thead><tr class="bg-indigo-50"><th class="border border-indigo-100 px-4 py-2 text-left">项目</th><th class="border border-indigo-100 px-4 py-2 text-left">内容</th><th class="border border-indigo-100 px-4 py-2 text-left">分值</th></tr></thead>
            <tbody>
              <tr><td class="border border-gray-100 px-4 py-2">实验报告</td><td class="border border-gray-100 px-4 py-2">数据记录与误差分析</td><td class="border border-gray-100 px-4 py-2">40分</td></tr>
              <tr><td class="border border-gray-100 px-4 py-2">公式推导</td><td class="border border-gray-100 px-4 py-2">步骤完整性</td><td class="border border-gray-100 px-4 py-2">30分</td></tr>
              <tr><td class="border border-gray-100 px-4 py-2">思考题</td><td class="border border-gray-100 px-4 py-2">火箭推射场景应用</td><td class="border border-gray-100 px-4 py-2">30分</td></tr>
            </tbody>
          </table>
        </div>
      `,
      contentFormat: 'html',
      analysis: momentumAnalysis,
    });
    isGenerating.value = false;
    isGenerated.value = true;
  }, 1500);
};

// 监听路由参数变化（应对导航时组件已挂载的情况）
watch(
  () => route.query.template,
  (tpl) => {
    isAiGamesMode.value = tpl === 'ai-games';
    if (isAiGamesMode.value) {
      activeGameIndex.value = 0;
    }

    if (tpl === 'momentum' && !isGenerated.value && !isGenerating.value) {
      triggerMomentumGeneration();
    }
  },
  { immediate: true },
);

watch(
  () => route.query.demoMode,
  (mode) => {
    showAiPptDemo.value = mode === 'ai-ppt';
    if (showAiPptDemo.value) {
      activeTab.value = 'ppt';
    }
  },
  { immediate: true },
);

watch(
  () => activeTab.value,
  (tab) => {
    if (isAiPptDemoMode.value && tab === 'flashcards') {
      isAiDemoCardFlipped.value = false;
    }
  },
);

watch(
  [lessonPlanMarkdown, () => props.projectId, () => props.projectName, () => projectDetail.value?.name],
  ([markdown]) => {
    if (isGenerated.value) {
      return;
    }
    resetWorkspaceLessonPlanRewrite();
    setWorkspaceLessonPlan({
      title: resolveLessonPlanTitle(markdown),
      content: markdown,
      contentFormat: 'markdown',
      analysis: momentumAnalysis,
    });
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
  gameCardsSignature,
  () => {
    rebuildGameDeck();
  },
  { immediate: true },
);

watch(
  flashcardData,
  () => {
    resetFlashcards();
  },
  { immediate: true },
);

watch(
  () => activeTab.value,
  (tab) => {
    if (tab === 'flashcards' && flashcardQueue.value.length === 0 && flashcardData.value.length > 0) {
      resetFlashcards();
    }
  },
);

const handleExternalUploadRequest = () => {
  promptAttachmentUpload();
};

onMounted(() => {
  window.addEventListener('workspace-open-upload', handleExternalUploadRequest);
  if (route.query.template === 'ai-games') {
    isAiGamesMode.value = true;
    activeGameIndex.value = 0;
  }
  if (route.query.template === 'momentum') {
    triggerMomentumGeneration();
  }
});

onBeforeUnmount(() => {
  window.removeEventListener('workspace-open-upload', handleExternalUploadRequest);
});

defineExpose({ isGenerated, activeTab, momentumAnalysis });
</script>

<template>
  <div class="flex-1 min-w-0 h-full flex flex-col flex-shrink-0">
      <!-- Top Bar -->
      <div class="h-16 flex-shrink-0 border-b border-gray-100 bg-white/80 backdrop-blur-xl flex items-center px-6 w-full gap-4">
        <input ref="fileInput" type="file" class="hidden" @change="handleAttachmentSelected">
        <div class="flex-shrink-0">
          <button 
            @click="showAttachments = !showAttachments"
            class="liquid-glass-button flex items-center rounded-full px-4 py-2 text-sm font-medium text-slate-700"
            :class="showAttachments ? 'bg-sky-500/12 text-sky-700 border-sky-200/70' : ''"
          >
            <Paperclip class="w-4 h-4 mr-2" /> 资料清单 ({{ attachments.length }})
          </button>
        </div>

        <div v-if="!isAiGamesMode" class="flex-1 flex items-center gap-2 overflow-x-auto whitespace-nowrap hide-scrollbar">
          <button 
            v-for="tab in tabs"
            :key="tab.id"
            @click="activeTab = tab.id"
            class="px-4 py-2 rounded-xl text-sm font-bold transition-all flex items-center gap-2 flex-shrink-0"
            :class="[activeTab === tab.id ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-100' : 'text-gray-500 hover:bg-gray-50']"
          >
            <component :is="tab.icon" class="w-4 h-4" />
            {{ tab.name }}
            <span v-if="isToolGenerating(tab.id)" class="inline-flex items-center gap-1 rounded-full bg-white/15 px-2 py-0.5 text-[10px] font-bold">
              <Loader2 class="w-3 h-3 animate-spin" />
              生成中
            </span>
          </button>
        </div>

        <div class="flex-shrink-0 ml-auto flex items-center gap-3">
          <button
            @click="handlePackageDownload"
            :disabled="isPackaging"
            class="liquid-glass-button flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300"
            :class="isPackaging ? 'bg-indigo-50 text-indigo-400 cursor-wait' : 'text-gray-600 hover:text-indigo-600 hover:bg-indigo-50'"
          >
            <svg v-if="isPackaging" class="w-4 h-4 animate-spin text-indigo-500" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <span v-else class="text-base">📦</span>
            <span>{{ isPackaging ? '正在云端打包...' : '一键打包下载' }}</span>
          </button>
          <button 
            @click="showDistributeModal = true"
            class="liquid-glass-button flex items-center rounded-full bg-emerald-500/12 px-4 py-2 text-sm font-medium text-slate-800"
          >
            <Send class="w-4 h-4 mr-2" /> 一键发给学生
          </button>
        </div>
      </div>

      <!-- Main Content Area -->
      <div class="flex-1 flex overflow-hidden bg-gray-50">
        
        <!-- Center: Canvas -->
        <div class="flex-1 min-w-0 h-full flex flex-col bg-gray-50/50 relative z-0">
          
          <!-- Floating Attachment Popover -->
          <Transition
            enter-active-class="transition duration-200 ease-out"
            enter-from-class="opacity-0 -translate-y-4"
            enter-to-class="opacity-100 translate-y-0"
            leave-active-class="transition duration-150 ease-in"
            leave-from-class="opacity-100 translate-y-0"
            leave-to-class="opacity-0 -translate-y-4"
          >
            <div v-if="showAttachments" class="absolute top-4 left-8 w-72 bg-white rounded-2xl shadow-2xl border border-gray-100 flex flex-col z-50 max-h-[60vh]">
              <div class="p-4 border-b border-gray-50 flex items-center justify-between font-medium text-gray-900">
                <div class="flex items-center">
                  <Paperclip class="w-4 h-4 mr-2 text-indigo-600" /> 资料清单
                </div>
                <button @click="showAttachments = false" class="text-gray-400 hover:text-gray-600">
                  <X class="w-4 h-4" />
                </button>
              </div>
              <div class="flex-1 overflow-y-auto p-3 flex flex-col gap-2 custom-scrollbar">
                <div v-if="attachments.length === 0" class="p-3 text-xs font-medium text-gray-400">当前项目还没有上传附件。</div>
                <div v-for="file in attachments" :key="file.id" class="p-2 bg-gray-50 rounded-xl flex items-start justify-between group border border-transparent hover:border-indigo-100 transition-colors">
                  <div class="flex items-start gap-2 min-w-0">
                    <div class="w-6 h-6 bg-white rounded-md shadow-sm flex items-center justify-center flex-shrink-0 text-indigo-500">
                      <FileText class="w-3 h-3" />
                    </div>
                    <div class="min-w-0">
                      <p class="text-xs font-bold text-gray-700 truncate">{{ file.original_name }}</p>
                      <p class="text-[10px] text-gray-400 mt-0.5">{{ formatFileSize(file.file_size) }}</p>
                    </div>
                  </div>
                  <button @click="deleteAttachment(file.id)" class="p-1 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-md opacity-0 group-hover:opacity-100 transition-all">
                    <Trash2 class="w-3 h-3" />
                  </button>
                </div>
              </div>
              <div class="p-3 border-t border-gray-50">
                <button @click="promptAttachmentUpload" :disabled="isUploading" class="w-full py-2 border-2 border-dashed border-gray-200 rounded-xl text-sm font-bold text-gray-500 hover:text-indigo-600 hover:border-indigo-300 hover:bg-indigo-50/50 transition-all flex items-center justify-center gap-2 disabled:opacity-60">
                  <Plus class="w-4 h-4" />
                  {{ isUploading ? '上传中...' : '继续添加' }}
                </button>
              </div>
            </div>
          </Transition>

          <div class="flex-1 min-w-0 overflow-y-auto p-8 custom-scrollbar relative">
          <div v-if="isProjectLoading" class="mb-6 rounded-2xl bg-white px-5 py-4 text-sm font-medium text-gray-500 shadow-sm">正在从 FastAPI 加载项目与附件...</div>
          <!-- Material Change Alert -->
          <div v-if="showMaterialChangeAlert" class="absolute top-8 left-1/2 -translate-x-1/2 z-20 bg-orange-50 border border-orange-200 rounded-2xl p-4 shadow-xl flex items-center gap-6 animate-in slide-in-from-top-4">
            <div class="flex items-center gap-2 text-orange-700">
              <AlertCircle class="w-5 h-5" />
              <span class="text-sm font-bold">检测到参考资料变动，是否重新生成当前内容？</span>
            </div>
            <button @click="regenerateContent" class="px-4 py-2 bg-orange-500 text-white rounded-xl text-sm font-bold hover:bg-orange-600 transition-colors shadow-sm">
              立即重产
            </button>
          </div>

            <div class="max-w-5xl mx-auto h-full min-w-0">
          <div v-if="isGeneratingContent" class="mb-6 rounded-[28px] bg-gradient-to-r from-indigo-50 via-blue-50 to-purple-50 px-6 py-5 shadow-sm border border-indigo-100">
            <div class="flex items-center gap-3 mb-4">
              <div class="w-9 h-9 bg-indigo-600 rounded-2xl flex items-center justify-center flex-shrink-0 shadow-lg shadow-indigo-200">
                <Zap class="w-4 h-4 text-white animate-pulse" />
              </div>
              <div class="flex-1 min-w-0">
                <span class="text-sm font-black text-gray-900 block">{{ generationStatus || '✨ AI 正在全力创作中，请稍候...' }}</span>
                <span class="text-xs text-indigo-500 font-medium">大模型自主决策·结构化输出</span>
              </div>
              <div class="text-2xl font-black text-indigo-600">{{ generationProgress }}%</div>
            </div>
            <div class="h-2 rounded-full bg-white/80 overflow-hidden shadow-inner">
              <div class="h-full bg-gradient-to-r from-indigo-500 via-purple-500 to-blue-500 transition-all duration-300 rounded-full relative overflow-hidden"
                :style="{ width: generationProgress + '%' }">
                <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/30 to-transparent animate-shimmer"></div>
              </div>
            </div>
            <div class="mt-3 flex gap-2 flex-wrap">
              <span v-for="tab in tabs" :key="tab.id"
                class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-[11px] font-bold transition-all"
                :class="activeTab === tab.id && isGeneratingContent
                  ? 'bg-indigo-600 text-white shadow-sm'
                  : hasGeneratedContent(tab.id)
                    ? 'bg-emerald-50 text-emerald-600 border border-emerald-200'
                    : 'bg-gray-100 text-gray-400'">
                <component :is="tab.icon" class="w-3 h-3" />
                {{ tab.name }}
                <span v-if="hasGeneratedContent(tab.id)">✓</span>
              </span>
            </div>
          </div>
            
            <div v-if="isAiGamesMode" class="flex-1 flex flex-col bg-gray-50 rounded-2xl shadow-sm border border-gray-100 overflow-hidden min-h-[700px]">
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
                    :src="aiGames[activeGameIndex].file"
                    class="absolute inset-0 w-full h-full border-0"
                  ></iframe>
                </transition>
              </div>
            </div>

            <template v-else-if="isAiPptDemoMode && ['ppt', 'lesson-plan', 'blog', 'flashcards'].includes(activeTab)">
              <div v-if="activeTab === 'ppt'" class="w-full h-full flex flex-col bg-gray-50 rounded-2xl overflow-hidden border border-gray-200">
                <div class="h-10 bg-white border-b border-gray-200 flex items-center justify-between px-4">
                  <span class="text-sm font-medium text-gray-700">《人工智能应用基础 - 老年餐饮智能辅助平台》</span>
                  <button @click="handleDownloadAiPptDemo" class="text-indigo-600 hover:text-indigo-800 text-sm flex items-center gap-1">
                    <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"></path></svg>
                    导出 PPTX
                  </button>
                </div>
                <iframe src="/老年餐饮智能辅助平台项目实战.pdf#toolbar=0" class="flex-1 w-full border-0" title="AI 生成演示文稿预览"></iframe>
              </div>

              <div v-else-if="activeTab === 'lesson-plan'" class="flex-1 p-8 overflow-y-auto bg-gray-50">
                <div class="max-w-4xl mx-auto bg-white p-10 rounded-2xl shadow-sm border border-gray-100">
                  <h1 class="text-3xl font-extrabold text-gray-900 mb-6 pb-4 border-b">《人工智能应用基础》标准示范教案</h1>
                  <div class="prose max-w-none text-gray-800">
                    <div class="bg-indigo-50 text-indigo-700 p-4 rounded-lg mb-6 text-sm">
                      <strong>适用年级：</strong> 高二/职高二年级 | <strong>预计课时：</strong> 45分钟 | <strong>核心素养：</strong> 计算思维、信息意识
                    </div>
                    <h3 class="text-xl font-bold mb-3 mt-6 text-indigo-900">一、 核心教学目标</h3>
                    <ul class="list-disc pl-5 mb-4 space-y-2">
                      <li><strong>知识与技能：</strong>理解人工智能的基本概念，掌握图像识别的基础逻辑。</li>
                      <li><strong>过程与方法：</strong>通过“模型训练模拟器”实操，体验数据标注与模型生成的全过程。</li>
                    </ul>
                    <h3 class="text-xl font-bold mb-3 mt-6 text-indigo-900">二、 教学过程设计 (45分钟)</h3>
                    <p class="mb-2"><strong>1. 情境导入 (5分钟)：</strong> 播放无人驾驶汽车避让行人的视频，提问“汽车是怎么‘看’到人的？”</p>
                    <p class="mb-2"><strong>2. 核心概念 (15分钟)：</strong> 讲解计算机视觉（CV）与监督学习的基本原理。</p>
                    <p class="mb-2"><strong>3. 互动实操 (20分钟)：</strong> 学生使用系统内置的【食品识别体验】互动件，收集数据并训练分类器。</p>
                  </div>
                </div>
              </div>

              <div v-else-if="activeTab === 'blog'" class="flex-1 p-8 overflow-y-auto bg-gray-50">
                <div class="max-w-3xl mx-auto bg-white p-10 rounded-2xl shadow-sm border border-gray-100">
                  <h1 class="text-2xl font-bold text-gray-900 mb-4">AI 时代下的教育：如何让学生秒懂“机器学习”？</h1>
                  <div class="flex items-center text-sm text-gray-500 mb-8 gap-4 border-b pb-4">
                    <span>发布于：刚刚</span><span>作者：织课 AI 助教</span><span>阅读时长：3分钟</span>
                  </div>
                  <div class="text-gray-700 leading-relaxed space-y-4">
                    <p>在讲解《人工智能应用基础》时，最大的痛点就是“算法黑盒”。学生很难理解一堆数据是怎么变成一个聪明的 AI 的。</p>
                    <p>今天，我们不再使用枯燥的 PPT，而是引入了<strong>项目制实操</strong>。通过让学生自己给图片打标签（比如分辨猫和狗），然后点击“开始训练”，他们能亲眼看到准确率曲线的上升。这种可视化反馈，比讲一万遍梯度下降都有效！</p>
                    <div class="bg-gray-100 p-4 rounded-lg border-l-4 border-indigo-500 my-4 text-gray-600 font-medium">
                      💡 教学小贴士：在实操环节，故意给 AI 喂一些错误的数据，让学生观察 AI 的“翻车现场”，借机引出“数据质量”的重要性。
                    </div>
                  </div>
                </div>
              </div>

              <div v-else-if="activeTab === 'flashcards'" class="flex-1 flex flex-col items-center justify-center bg-gray-50 p-6">
                <h2 class="text-2xl font-bold text-gray-800 mb-2">人工智能基础复习</h2>
                <div class="text-sm font-medium text-indigo-600 bg-indigo-100 px-3 py-1 rounded-full mb-8">
                  PROGRESS : {{ aiDemoCurrentCardIndex + 1 }} / {{ aiDemoFlashcards.length }}
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
              </div>
            </template>

            <!-- Placeholder for ungenerated tools -->
            <div v-else-if="!hasGeneratedContent(activeTab) && activeTab !== 'simulation' && activeTab !== 'flashcards' && !isGenerating" class="h-full flex flex-col items-center justify-center gap-6">
              <div class="w-24 h-24 bg-gray-100 rounded-3xl flex items-center justify-center text-gray-400">
                <component :is="tabs.find(t => t.id === activeTab)?.icon" class="w-10 h-10" />
              </div>
              <div class="text-center space-y-2">
                <h3 class="text-2xl font-black text-gray-900">该项内容尚未生成</h3>
                <p class="text-gray-500">系统将基于当前项目资料进行深度解析，并生成可直接编辑的内容初稿。</p>
              </div>
              <div class="rounded-full bg-indigo-50 px-4 py-2 text-xs font-bold text-indigo-700">
                当前已识别 {{ getCurrentAttachmentList().length }} 份资料
              </div>
              <button
                @click="handleGenerate"
                :disabled="isGeneratingContent"
                class="mt-4 flex items-center gap-2 rounded-2xl px-8 py-4 font-bold text-white shadow-xl transition-all disabled:cursor-not-allowed disabled:opacity-80"
                :class="isGeneratingContent ? 'bg-indigo-500 shadow-indigo-100' : 'bg-indigo-600 shadow-indigo-200 hover:scale-105'"
              >
                <Loader2 v-if="isGeneratingContent" class="w-5 h-5 animate-spin" />
                <Zap v-else class="w-5 h-5" />
                {{ isGeneratingContent ? '正在深度解析资料并生成...' : '基于当前资料生成' }}
              </button>
              <div v-if="isGeneratingContent" class="w-full max-w-md space-y-3">
                <p class="text-center text-sm font-medium text-gray-500">资料正在送入后端生成链路，请勿重复点击。</p>
                <div class="h-2 overflow-hidden rounded-full bg-indigo-100">
                  <div class="h-full rounded-full bg-indigo-600 transition-all duration-300" :style="{ width: `${generationProgress}%` }"></div>
                </div>
              </div>
            </div>

            <!-- PPT View – PDF 原生预览 -->
            <div v-else-if="activeTab === 'ppt'" class="w-full h-full flex flex-col items-center justify-start bg-gradient-to-br from-slate-100 via-gray-50 to-indigo-50 min-h-[600px] py-8 px-6">
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

          <!-- Word View -->
          <div v-else-if="activeTab === 'lesson-plan'">

            <!-- State 1: AI Generating spinner -->
            <div v-if="isGenerating" class="flex flex-col items-center justify-center min-h-[500px] gap-5">
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

            <!-- State 2: Generated (momentum mock content) -->
            <div v-else-if="shouldShowSharedLessonPlan" class="p-10 relative">
              <div :class="{ 'blur-sm opacity-50': isRegenerating }" class="transition-all duration-500">
                <h1 class="text-3xl font-extrabold text-gray-900 mb-8 pb-4 border-b border-gray-100">
                  {{ workspaceData.title }}
                </h1>
                <div class="prose prose-sm prose-indigo max-w-none math-render-area rendered-markdown rendered-document-markdown break-words" v-html="renderedContent"></div>
              </div>
              <!-- Regenerating overlay -->
              <div v-if="isRegenerating" class="absolute inset-0 z-10 flex flex-col items-center justify-center bg-white/70 backdrop-blur-sm rounded-2xl">
                <svg class="w-12 h-12 text-indigo-600 animate-spin mb-3" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                <span class="text-indigo-700 font-bold tracking-widest">AI 正在根据您的要求重写教案...</span>
              </div>
            </div>

            <!-- State 3: Normal lesson-plan (real project content) -->
            <div v-else class="relative max-w-4xl mx-auto">

            <!-- Floating Action Bar for Word View -->
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
              <article class="prose prose-sm prose-indigo max-w-none min-w-0 break-words math-render-area prose-table:border-collapse prose-th:border prose-th:bg-gray-100 prose-th:px-3 prose-th:py-2 prose-td:border prose-td:p-2 prose-headings:font-bold prose-ul:list-disc prose-li:my-1 text-gray-700 rendered-markdown rendered-document-markdown" v-html="lessonPlanHtml"></article>
            </div>

            <!-- Generated Quizzes Section -->
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
            </div><!-- /State 3: normal lesson-plan -->
          </div><!-- /lesson-plan tab -->

          <!-- Interactive View (3D Physics Sandbox) -->
          <div v-else-if="activeTab === 'game'" class="w-full h-full flex flex-col p-4 bg-gray-50/50">
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

          <div v-else-if="activeTab === 'video'" class="w-full h-full flex flex-col items-center justify-center bg-[#F9FAFB] p-8">
            <!-- 标题区 -->
            <div class="mb-8 text-center">
              <div class="inline-flex items-center justify-center w-12 h-12 rounded-full bg-indigo-100 text-indigo-600 mb-4 shadow-sm">
                <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clip-rule="evenodd"></path></svg>
              </div>
              <h2 class="text-2xl font-bold text-gray-800 tracking-wide mb-2">演示动画预览</h2>
              <p class="text-sm text-gray-500 font-medium">《洛伦兹力：粒子在磁场中的舞蹈》</p>
            </div>
            <!-- 播放器 -->
            <div class="relative w-full max-w-sm bg-black rounded-2xl shadow-[0_20px_50px_rgba(0,0,0,0.15)] overflow-hidden border border-gray-200/50 transition-all hover:shadow-[0_25px_60px_rgba(0,0,0,0.2)]">
              <video
                class="w-full h-auto max-h-[65vh] object-contain outline-none"
                src="/short-video.mp4"
                controls
                autoplay
                loop
                playsinline
              ></video>
            </div>
          </div>

          <div v-else-if="activeTab === 'blog'" class="w-full space-y-12">
            <div class="space-y-6">
              <div class="flex items-center gap-3">
                <span class="px-3 py-1 bg-indigo-50 text-indigo-600 text-[10px] font-bold rounded-full uppercase tracking-widest">文档深度改写</span>
                <span class="text-xs text-gray-400 font-medium">根据上传资料生成</span>
              </div>
              <h1 class="text-4xl font-black text-gray-900 leading-tight">{{ props.projectName || '教学博客初稿' }}</h1>
            </div>
            <article class="bg-white rounded-[32px] shadow-sm p-10 rendered-markdown rendered-document-markdown break-words whitespace-pre-wrap max-w-full min-w-0 overflow-hidden" v-html="blogHtml"></article>
          </div>

          <!-- 🧪 拟真演示 Tab -->
          <div v-else-if="activeTab === 'simulation'" class="w-full pb-8">
            <div class="h-full min-h-[500px] flex flex-col items-center justify-center gap-6">
              <div class="w-24 h-24 bg-gray-100 rounded-3xl flex items-center justify-center text-gray-400">
                <FlaskConical class="w-10 h-10" />
              </div>
              <div class="text-center space-y-2 max-w-md">
                <h3 class="text-2xl font-black text-gray-900">拟真演示入口已收口</h3>
                <p class="text-gray-500">交互式物理动画现已严格迁移到“互动游戏”Tab 中展示，这里不再渲染动画内容，避免页面穿透。</p>
              </div>
              <button
                @click="activeTab = 'game'"
                class="mt-2 flex items-center gap-2 rounded-2xl px-8 py-4 font-bold text-white shadow-xl transition-all bg-indigo-600 shadow-indigo-200 hover:scale-105"
              >
                <Gamepad2 class="w-5 h-5" />
                前往互动游戏
              </button>
            </div>
          </div>

          <!-- 🃏 知识闪卡 Tab -->
          <div v-else-if="activeTab === 'flashcards'" class="w-full h-full flex flex-col items-center justify-center bg-[#F4F5F7] p-8 overflow-hidden relative">

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
              <!-- 待加强 -->
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

              <!-- 已掌握 -->
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
          </div>
        </div>
      </div>
    </div>
    </div>

    <!-- Distribution Modal -->
    <Transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="opacity-0 scale-95"
      enter-to-class="opacity-100 scale-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="opacity-100 scale-100"
      leave-to-class="opacity-0 scale-95"
    >
      <div v-if="showDistributeModal" class="fixed inset-0 z-50 flex items-center justify-center p-6">
        <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="showDistributeModal = false"></div>
        
        <div class="relative w-full max-w-[560px] rounded-[36px] border border-white/80 bg-white/88 shadow-[0_30px_90px_rgba(99,102,241,0.12)] backdrop-blur-xl overflow-hidden flex flex-col">
          <div class="px-8 py-6 flex items-center justify-between border-b border-gray-50">
            <h3 class="text-xl font-black text-gray-900">分发教学任务</h3>
            <button @click="showDistributeModal = false" class="p-2 hover:bg-gray-50 rounded-xl text-gray-400 hover:text-gray-900 transition-all">
              <X class="w-5 h-5" />
            </button>
          </div>
          
          <div class="p-8 space-y-8">
            <!-- Channels -->
            <div class="space-y-4">
              <div class="flex items-center justify-between gap-4">
                <h4 class="text-sm font-bold text-gray-900">选择分发渠道</h4>
                <span class="rounded-full bg-indigo-50 px-3 py-1 text-[11px] font-black text-indigo-700">已选 {{ selectedChannels.length }} 项</span>
              </div>
              <div class="grid grid-cols-1 gap-3">
                <button
                  v-for="channel in distributionChannels"
                  :key="channel.id"
                  type="button"
                  @click="toggleSelection(selectedChannels, channel.id)"
                  class="group relative overflow-hidden rounded-[24px] border-2 p-4 text-left transition-all"
                  :class="selectedChannels.includes(channel.id) ? 'border-indigo-500 bg-[linear-gradient(135deg,_rgba(238,242,255,0.95),_rgba(245,243,255,0.9))] shadow-[0_16px_40px_rgba(79,70,229,0.14)]' : 'border-gray-100 bg-white hover:border-indigo-200 hover:shadow-sm'"
                >
                  <div class="absolute inset-0 opacity-0 transition-opacity" :class="selectedChannels.includes(channel.id) ? 'opacity-100 bg-[radial-gradient(circle_at_top_right,_rgba(129,140,248,0.18),_transparent_45%)]' : ''"></div>
                  <div class="relative flex items-start gap-4">
                    <div class="flex h-12 w-12 items-center justify-center rounded-2xl transition-all" :class="selectedChannels.includes(channel.id) ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-200' : 'bg-gray-100 text-gray-500 group-hover:bg-indigo-50 group-hover:text-indigo-600'">
                      <component :is="channel.icon" class="w-5 h-5" />
                    </div>
                    <div class="flex-1 min-w-0">
                      <div class="flex items-center justify-between gap-3">
                        <p class="text-sm font-bold text-gray-900">{{ channel.title }}</p>
                        <span class="rounded-full px-2.5 py-1 text-[10px] font-black uppercase tracking-[0.2em]" :class="selectedChannels.includes(channel.id) ? 'bg-white text-indigo-700' : 'bg-gray-100 text-gray-400'">{{ channel.tag }}</span>
                      </div>
                      <p class="mt-1 text-xs leading-5 text-gray-500">{{ channel.description }}</p>
                    </div>
                    <div class="mt-1 flex h-6 w-6 items-center justify-center rounded-full border-2 transition-all" :class="selectedChannels.includes(channel.id) ? 'border-indigo-600 bg-indigo-600 text-white scale-100' : 'border-gray-300 text-transparent scale-90'">
                      <Check class="w-3.5 h-3.5" />
                    </div>
                  </div>
                </button>
              </div>
            </div>

            <!-- Classes -->
            <div class="space-y-4">
              <div class="flex items-center justify-between gap-4">
                <h4 class="text-sm font-bold text-gray-900">选择目标班级</h4>
                <span class="rounded-full bg-violet-50 px-3 py-1 text-[11px] font-black text-violet-700">已选 {{ selectedClasses.length }} 个班级</span>
              </div>
              <div class="flex flex-wrap gap-3">
                <button 
                  v-for="cls in distributionClassOptions" 
                  :key="cls"
                  @click="toggleSelection(selectedClasses, cls)"
                  class="px-4 py-2.5 rounded-2xl text-sm font-bold transition-all border-2 flex items-center gap-2"
                  :class="selectedClasses.includes(cls) ? 'border-indigo-500 bg-[linear-gradient(135deg,_rgba(238,242,255,0.98),_rgba(245,243,255,0.94))] text-indigo-700 shadow-sm' : 'border-gray-100 bg-white text-gray-600 hover:border-indigo-200'"
                >
                  <span class="flex h-5 w-5 items-center justify-center rounded-full border text-[10px]" :class="selectedClasses.includes(cls) ? 'border-indigo-600 bg-indigo-600 text-white' : 'border-gray-300 text-transparent'">
                    <Check class="w-3 h-3" />
                  </span>
                  {{ cls }}
                </button>
              </div>
            </div>

          </div>
          
          <div class="px-8 py-6 bg-gray-50/50 flex gap-4">
            <button @click="showDistributeModal = false" :disabled="isDistributionMockLoading" class="liquid-glass-secondary-button flex-1 rounded-full px-6 py-4 text-sm font-bold text-gray-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed">取消</button>
            <button 
              @click="confirmDistribution" 
              class="liquid-glass-primary-button flex-1 rounded-full px-6 py-4 text-sm font-bold transition-all flex items-center justify-center gap-2"
              :class="isDistributionReady && !isDistributionMockLoading ? 'text-indigo-700 hover:-translate-y-0.5' : 'text-indigo-400 cursor-not-allowed opacity-70'"
              :disabled="!isDistributionReady || isDistributionMockLoading"
            >
              <Loader2 v-if="isDistributionMockLoading" class="w-4 h-4 animate-spin" />
              {{ isDistributionMockLoading ? '分发中...' : '确认分发' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Global Toast -->
    <Transition name="fade">
      <div v-if="showToast" class="fixed bottom-8 left-1/2 -translate-x-1/2 z-[60]">
        <div class="bg-gray-900 text-white px-6 py-3 rounded-2xl shadow-2xl flex items-center gap-3 border border-white/10 backdrop-blur-md">
          <div class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
          <span class="text-sm font-bold">{{ toastMessage }}</span>
        </div>
      </div>
    </Transition>
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

.math-render-area :deep(.katex-display) {
  margin: 1.25rem 0;
  overflow-x: auto;
  overflow-y: hidden;
  padding: 0.35rem 0;
}

.math-render-area :deep(.katex) {
  font-size: 1.06em;
}

.math-render-area :deep(.katex-display > .katex) {
  display: block;
  text-align: center;
}

.game-stack-stage {
  perspective: 1800px;
}

.game-stack-card {
  transform-style: preserve-3d;
  transition: transform 0.52s cubic-bezier(0.22, 1, 0.36, 1), opacity 0.42s ease, filter 0.42s ease;
  will-change: transform, opacity;
}

.game-card-3d {
  position: relative;
  transform-style: preserve-3d;
  transition: transform 0.72s cubic-bezier(0.22, 1, 0.36, 1);
}

.game-card-3d.is-flipped {
  transform: rotateY(180deg);
}

.liquid-glass-icon-button,
.liquid-glass-pill-button,
.liquid-glass-primary-button,
.liquid-glass-secondary-button {
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.82);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.84), rgba(255, 255, 255, 0.58));
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.88), 0 18px 40px rgba(148, 163, 184, 0.16);
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
}

.liquid-glass-icon-button::before,
.liquid-glass-pill-button::before,
.liquid-glass-primary-button::before,
.liquid-glass-secondary-button::before {
  content: '';
  position: absolute;
  inset: 1px;
  border-radius: inherit;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.66), rgba(255, 255, 255, 0.08));
  pointer-events: none;
}

.liquid-glass-danger {
  color: #ef4444;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.92), 0 22px 44px rgba(251, 113, 133, 0.24), 0 0 0 1px rgba(255, 255, 255, 0.3);
}

.liquid-glass-success {
  color: #16a34a;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.92), 0 22px 44px rgba(74, 222, 128, 0.24), 0 0 0 1px rgba(255, 255, 255, 0.3);
}

.liquid-glass-primary-button {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.96), rgba(238, 242, 255, 0.9));
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.96), 0 22px 48px rgba(129, 140, 248, 0.2);
}

.liquid-glass-secondary-button {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.92), rgba(255, 255, 255, 0.74));
}

.liquid-glass-icon-stroke {
  position: relative;
  z-index: 1;
}

.game-card-face {
  position: absolute;
  inset: 0;
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
}

.game-card-face-back {
  transform: rotateY(180deg);
}

.review-shatter-piece {
  position: absolute;
  inset: 0;
  opacity: 0.8;
  background: linear-gradient(135deg, rgba(248, 113, 113, 0.34), rgba(239, 68, 68, 0.08) 50%, transparent 72%);
  animation: review-shatter 0.52s ease forwards;
}

.review-shatter-piece:nth-child(1) {
  clip-path: polygon(0 0, 48% 0, 24% 42%, 0 60%);
  --move-x: -64px;
  --move-y: -88px;
  --rotate: -18deg;
}

.review-shatter-piece:nth-child(2) {
  clip-path: polygon(48% 0, 100% 0, 100% 32%, 62% 46%);
  --move-x: 82px;
  --move-y: -74px;
  --rotate: 22deg;
}

.review-shatter-piece:nth-child(3) {
  clip-path: polygon(0 60%, 26% 42%, 44% 100%, 0 100%);
  --move-x: -96px;
  --move-y: 70px;
  --rotate: -20deg;
}

.review-shatter-piece:nth-child(4) {
  clip-path: polygon(24% 42%, 52% 10%, 64% 54%, 44% 100%);
  --move-x: -16px;
  --move-y: -28px;
  --rotate: -8deg;
}

.review-shatter-piece:nth-child(5) {
  clip-path: polygon(52% 10%, 100% 32%, 72% 100%, 64% 54%);
  --move-x: 92px;
  --move-y: 48px;
  --rotate: 18deg;
}

.review-shatter-piece:nth-child(6) {
  clip-path: polygon(64% 54%, 72% 100%, 44% 100%);
  --move-x: 12px;
  --move-y: 96px;
  --rotate: 12deg;
}

@keyframes review-shatter {
  100% {
    opacity: 0;
    transform: translate(var(--move-x), var(--move-y)) rotate(var(--rotate)) scale(0.88);
  }
}

@keyframes shimmer {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(200%); }
}
.animate-shimmer {
  animation: shimmer 1.8s infinite linear;
}

@keyframes progress {
  0% { width: 0%; }
  100% { width: 100%; }
}

/* ── 知识闪卡 ────────────────────────────────────────────────────────────────── */

/* 3D翻转核心 */
.flashcard-3d {
  position: relative;
  transform-style: preserve-3d;
  transition: transform 0.72s cubic-bezier(0.22, 1, 0.36, 1);
  will-change: transform;
}

.flashcard-3d.is-flipped {
  transform: rotateY(180deg);
}

/* 卡面公共样式 */
.flashcard-face {
  position: absolute;
  inset: 0;
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
}

.flashcard-face-back {
  transform: rotateY(180deg);
}

/* 动画包裹层 */
.flashcard-anim-wrapper {
  width: 100%;
}

/* 向左滑出（待加强） */
@keyframes fc-exit-left {
  from { transform: translateX(0) rotate(0deg); opacity: 1; }
  to   { transform: translateX(-130%) rotate(-18deg); opacity: 0; }
}

/* 向右滑出（已掌握） */
@keyframes fc-exit-right {
  from { transform: translateX(0) rotate(0deg); opacity: 1; }
  to   { transform: translateX(130%) rotate(18deg); opacity: 0; }
}

/* 新卡入场 */
@keyframes fc-enter-pop {
  from { transform: scale(0.88) translateY(12px); opacity: 0; }
  to   { transform: scale(1) translateY(0); opacity: 1; }
}

.fc-exit-left  { animation: fc-exit-left  0.42s ease forwards; }
.fc-exit-right { animation: fc-exit-right 0.42s ease forwards; }
.fc-enter-pop  { animation: fc-enter-pop  0.32s cubic-bezier(0.22, 1, 0.36, 1) forwards; }

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
