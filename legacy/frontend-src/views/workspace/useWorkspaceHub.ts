import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue';
import { useRoute } from 'vue-router';
import { apiClient } from '@/api/client';
import {
  type AttachmentRecord,
  type GeneratedContentEntry,
  type GeneratorComposeResponse,
  type ProjectDetail,
} from '@/types';
import {
  type LorentzDemoContext,
  buildLorentzDemoBlogEntry,
  buildLorentzDemoGameEntry,
  buildLorentzDemoLessonPlanEntry,
  buildLorentzDemoPptEntry,
  buildLorentzDemoVideoEntry,
  getLorentzDemoDelayMs,
  isLorentzDemoTarget,
  LORENTZ_DEMO_ANIMATION_HTML,
  LORENTZ_DEMO_STAGE_MESSAGES,
  waitForLorentzDemoDelay,
} from '@/utils/lorentzDemo';
import {
  resetWorkspaceLessonPlanRewrite,
  setWorkspaceLessonPlan,
} from '@/composables/useWorkspaceState';

export type ShowMode = 'normal' | 'ai-games' | 'ai-ppt-demo';

export function useWorkspaceHub(
  props: {
    initialTasks?: string[];
    projectId?: number | null;
    projectName?: string;
    generationRequirement?: string;
    autoGenerateToken?: number;
    mockTemplate?: string;
  },
) {
  const route = useRoute();

  const tabs = [
    { id: 'ppt', name: '演示文稿' },
    { id: 'lesson-plan', name: '标准教案' },
    { id: 'video', name: '短视频' },
    { id: 'game', name: '互动游戏' },
    { id: 'blog', name: '教学博客' },
    { id: 'flashcards', name: '知识闪卡' },
  ];

  const activeTab = ref(props.initialTasks?.[0] || 'ppt');
  const showMode = ref<ShowMode>('normal');
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

  const showDistributeModal = ref(false);
  const showToast = ref(false);
  const toastMessage = ref('');
  const selectedChannels = ref<string[]>([]);
  const selectedClasses = ref<string[]>([]);
  const isDistributionMockLoading = ref(false);

  const isGenerating = ref(false);
  const isGenerated = ref(false);
  const activeGameIndex = ref(0);

  const distributionChannels = [
    { id: 'digital-human', title: '分发至数字人助教答疑库', description: '学生可通过对话向 AI 助教追问知识点。', tag: '实时答疑' },
    { id: 'tablet', title: '同步至学生平板端', description: '作业、素材与互动指令会同步出现在学生学习设备。', tag: '班级终端' },
    { id: 'h5', title: '导出为互动 H5 链接', description: '自动生成可分享链接，方便在班级群与家校端流转。', tag: 'H5 分享' },
  ];
  const distributionClassOptions = ['高二1班', '高二2班', '高二3班', '高二4班'];

  const momentumAnalysis = {
    difficulty: 65,
    coverage: 85,
    warning: '学情预估：学生对"系统内力远大于外力时动量近似守恒"的条件容易混淆，建议在【交互探索】环节增加"开启/关闭桌面摩擦力"的对比演示。',
  };

  const projectContents = computed(() => projectDetail.value?.contents || {});
  const isGeneratingContent = computed(() => generatingToolIds.value.includes(activeTab.value));
  const isLorentzDemoProject = computed(() => isLorentzDemoTarget({ projectName: props.projectName || projectDetail.value?.name || '' }));
  const isDistributionReady = computed(() => selectedChannels.value.length > 0 && selectedClasses.value.length > 0);
  const canGenerateWithoutAttachments = computed(() => Boolean(currentRequirement().trim()));

  const lorentzDemoToolIds = ['ppt', 'lesson-plan', 'game', 'blog', 'video'] as const;

  const hasGeneratedContent = (toolId: string) => {
    if (toolId === 'lesson-plan' && isGenerated.value) return true;
    return Boolean(projectContents.value[toolId]);
  };
  const isToolGenerating = (toolId: string) => generatingToolIds.value.includes(toolId);

  const getCurrentAttachmentList = () => {
    const projectAttachments = projectDetail.value?.attachments || [];
    return projectAttachments.length > 0 ? projectAttachments : attachments.value;
  };

  const currentRequirement = () =>
    props.generationRequirement?.trim() || projectDetail.value?.description || props.projectName || '请根据参考资料生成可直接使用的教学初稿';

  const resolveLessonPlanTitle = (content: string) => {
    const headingMatch = content.match(/^#\s+(.+)$/m);
    if (headingMatch?.[1]) return headingMatch[1].trim();
    return `${props.projectName || projectDetail.value?.name || '当前课程'}教案`;
  };

  const formatFileSize = (size: number) => {
    if (size < 1024) return `${size} B`;
    if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
    return `${(size / (1024 * 1024)).toFixed(1)} MB`;
  };

  const extractErrorDetail = (error: unknown) => {
    if (error && typeof error === 'object') {
      const e = error as { response?: { data?: { detail?: unknown; message?: unknown } }; message?: unknown };
      const detail = e.response?.data?.detail;
      if (typeof detail === 'string' && detail.trim()) return detail;
      const message = e.response?.data?.message;
      if (typeof message === 'string' && message.trim()) return message;
      if (typeof e.message === 'string' && e.message.trim()) return e.message;
    }
    return error instanceof Error ? error.message : '请求失败，请稍后重试';
  };

  const showToastMessage = (message: string) => {
    toastMessage.value = message;
    showToast.value = true;
    window.setTimeout(() => { showToast.value = false; }, 3000);
  };

  const setToolGenerating = (toolId: string, generating: boolean) => {
    if (generating) {
      if (!generatingToolIds.value.includes(toolId)) generatingToolIds.value = [...generatingToolIds.value, toolId];
    } else {
      generatingToolIds.value = generatingToolIds.value.filter((id) => id !== toolId);
    }
  };

  const updateToolContent = (toolId: string, entry: GeneratedContentEntry) => {
    if (!projectDetail.value) return;
    projectDetail.value = {
      ...projectDetail.value,
      contents: { ...(projectDetail.value.contents || {}), [toolId]: entry },
    };
  };

  const applyLorentzDemoBundle = (demoContext: LorentzDemoContext) => {
    updateToolContent('ppt', buildLorentzDemoPptEntry(demoContext));
    updateToolContent('lesson-plan', buildLorentzDemoLessonPlanEntry(demoContext));
    updateToolContent('game', buildLorentzDemoGameEntry(demoContext));
    updateToolContent('blog', buildLorentzDemoBlogEntry(demoContext));
    updateToolContent('video', buildLorentzDemoVideoEntry(demoContext));
  };

  const requestToolGeneration = async (toolId: string, attachmentContext: AttachmentRecord[] = getCurrentAttachmentList()) => {
    if (!props.projectId) { showToastMessage('请先创建或打开项目'); return; }
    const currentProjectName = props.projectName || projectDetail.value?.name || '';
    const attachmentIds = attachmentContext.map((item) => item.id).filter((id) => Number.isInteger(id) && id > 0);
    const sourceFiles = attachmentContext.map((item) => item.original_name).filter(Boolean);
    const demoModeActive = isLorentzDemoTarget({ projectName: currentProjectName });
    const demoContext = { projectName: currentProjectName, fileNames: sourceFiles, attachmentIds, sourceFiles, userRequirement: currentRequirement() };

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
        const demoGeneratedTools = [...lorentzDemoToolIds];
        generatedTools.value = Array.from(new Set([...generatedTools.value, ...demoGeneratedTools]));
        generationProgress.value = 100;
        showMaterialChangeAlert.value = false;
        window.dispatchEvent(new CustomEvent('ai-generation-complete', { detail: { toolLabel: tabs.find((t) => t.id === toolId)?.name || toolId, projectName: currentProjectName || '洛伦兹力' } }));
        return;
      } catch (error) {
        showToastMessage(`生成失败：${extractErrorDetail(error)}`);
      } finally {
        if (statusTimer) window.clearInterval(statusTimer);
        setToolGenerating(toolId, false);
        generationProgress.value = 0;
        generationStatus.value = '';
      }
    }

    generationProgress.value = 12;
    generationStatus.value = `✨ 正在为您自动生成【${toolLabel}】初稿，请稍候...`;
    const timer = window.setInterval(() => { generationProgress.value = Math.min(generationProgress.value + 9, 88); }, 350);

    try {
      const response = await apiClient.post<GeneratorComposeResponse>('/api/generator/compose', {
        project_id: props.projectId,
        attachment_ids: attachmentIds,
        generator_type: toolId,
        user_requirement: currentRequirement(),
        session_id: `workspace-${props.projectId}-${toolId}`,
      });
      generationProgress.value = 100;
      updateToolContent(toolId, response.data.content);
      if (!generatedTools.value.includes(toolId)) generatedTools.value.push(toolId);
      showMaterialChangeAlert.value = false;
      showToastMessage(`${tabs.find((tab) => tab.id === toolId)?.name || toolId} 已根据上传文档生成完成`);
      window.dispatchEvent(new CustomEvent('ai-generation-complete', { detail: { toolLabel: tabs.find((tab) => tab.id === toolId)?.name || toolId, projectName: currentProjectName } }));
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
    const allIds = Array.from(new Set([...lorentzDemoToolIds, ...toolIds]));
    allIds.forEach((id) => setToolGenerating(id, true));
    let stageIndex = 0;
    generationProgress.value = 12;
    generationStatus.value = LORENTZ_DEMO_STAGE_MESSAGES[stageIndex];
    const statusTimer = window.setInterval(() => {
      stageIndex = (stageIndex + 1) % LORENTZ_DEMO_STAGE_MESSAGES.length;
      generationStatus.value = LORENTZ_DEMO_STAGE_MESSAGES[stageIndex];
      generationProgress.value = Math.min(generationProgress.value + 18, 90);
    }, 1000);
    try {
      const ctx = getCurrentAttachmentList();
      await waitForLorentzDemoDelay(getLorentzDemoDelayMs());
      applyLorentzDemoBundle({ projectName: props.projectName || projectDetail.value?.name || '', fileNames: ctx.map(i => i.original_name), attachmentIds: ctx.map(i => i.id), sourceFiles: ctx.map(i => i.original_name), userRequirement: currentRequirement() });
      generatedTools.value = Array.from(new Set([...generatedTools.value, ...allIds]));
      generationProgress.value = 100;
      showMaterialChangeAlert.value = false;
    } finally {
      window.clearInterval(statusTimer);
      allIds.forEach((id) => setToolGenerating(id, false));
      generationProgress.value = 0;
      generationStatus.value = '';
    }
  };

  const maybeAutoGenerate = async () => {
    if (!props.projectId || !props.autoGenerateToken || !projectDetail.value) return;
    const autoKey = `${props.projectId}-${props.autoGenerateToken}`;
    if (lastAutoGenerateKey.value === autoKey) return;
    lastAutoGenerateKey.value = autoKey;
    const allTargets = tabs.map(t => t.id).filter((toolId) => !hasGeneratedContent(toolId));
    if (allTargets.length === 0) return;
    activeTab.value = allTargets[0];
    if (isLorentzDemoProject.value && allTargets.length > 0) {
      await batchLorentzDemoGenerate(allTargets);
      return;
    }
    for (const toolId of allTargets) { await requestToolGeneration(toolId); }
  };

  const syncProjectState = (detail: ProjectDetail) => {
    projectDetail.value = detail;
    attachments.value = detail.attachments || [];
    generatedTools.value = Array.from(new Set([...(props.initialTasks || []), ...Object.keys(detail.contents || {})]));
  };

  const loadProject = async () => {
    if (!props.projectId) { projectDetail.value = null; attachments.value = []; return; }
    isProjectLoading.value = true;
    try {
      const response = await apiClient.get<ProjectDetail>(`/api/projects/${props.projectId}`);
      syncProjectState(response.data);
      await maybeAutoGenerate();
    } catch (error) {
      showToastMessage(error instanceof Error ? error.message : '加载工作台失败');
    } finally { isProjectLoading.value = false; }
  };

  const promptAttachmentUpload = () => {
    if (!props.projectId) { showToastMessage('请先从首页创建或打开一个项目'); return; }
    fileInput.value?.click();
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
      if (projectDetail.value) { projectDetail.value = { ...projectDetail.value, attachments: [response.data, ...(projectDetail.value.attachments || [])] }; }
      showMaterialChangeAlert.value = true;
      showToastMessage('附件上传成功，已同步到后端');
    } catch (error) { showToastMessage(error instanceof Error ? error.message : '上传附件失败'); }
    finally { isUploading.value = false; input.value = ''; }
  };

  const deleteAttachment = async (id: number) => {
    try {
      await apiClient.delete(`/api/attachments/${id}`);
      attachments.value = attachments.value.filter((a) => a.id !== id);
      if (projectDetail.value) { projectDetail.value = { ...projectDetail.value, attachments: attachments.value }; }
      showMaterialChangeAlert.value = true;
      showToastMessage('附件已删除');
    } catch (error) { showToastMessage(error instanceof Error ? error.message : '删除附件失败'); }
  };

  const regenerateContent = async () => { showMaterialChangeAlert.value = false; await requestToolGeneration(activeTab.value); };

  const handleGenerate = async () => {
    if (isGeneratingContent.value) return;
    const currentAttachments = getCurrentAttachmentList();
    const demoModeActive = isLorentzDemoTarget({ projectName: props.projectName || projectDetail.value?.name });
    if (!demoModeActive && currentAttachments.length === 0) { showToastMessage('当前项目暂无资料，请先上传 PDF、DOCX、PPTX、TXT、Markdown 或图片扫描件后再生成'); return; }
    await requestToolGeneration(activeTab.value, currentAttachments);
  };

  const handlePackageDownload = async () => {
    if (isPackaging.value) return;
    isPackaging.value = true;
    try {
      await new Promise((resolve) => { window.setTimeout(resolve, 2000); });
      const mockContent = `【织课 AI 自动生成课件包】\n\n包含文件：\n1. 视觉任务挑战赛-课前.html\n2. 模型训练模拟器-课中.html\n3. 食品识别体验.html\n\n注意：此为演示环境的打包文件。`;
      const blob = new Blob([mockContent], { type: 'application/zip' });
      const downloadUrl = window.URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = downloadUrl; anchor.download = '人工智能应用基础_互动课件包.zip'; anchor.style.display = 'none';
      document.body.appendChild(anchor); anchor.click(); document.body.removeChild(anchor);
      window.setTimeout(() => { window.URL.revokeObjectURL(downloadUrl); }, 1000);
      showToastMessage('课件打包成功，已开始下载！');
    } finally { isPackaging.value = false; }
  };

  const toggleSelection = (list: string[], item: string) => {
    const index = list.indexOf(item);
    if (index > -1) list.splice(index, 1); else list.push(item);
  };

  const confirmDistribution = async () => {
    if (!isDistributionReady.value || isDistributionMockLoading.value) return;
    isDistributionMockLoading.value = true;
    const selectedChannelSnapshot = [...selectedChannels.value];
    const selectedClassSnapshot = [...selectedClasses.value];
    const generatedLink = `https://mock.zhike.ai/share/${props.projectId || 'demo'}-${activeTab.value}-${Date.now().toString(36)}`;
    await new Promise((resolve) => { window.setTimeout(resolve, 1500); });

    let copiedH5Link = false;
    if (selectedChannelSnapshot.includes('h5') && typeof navigator !== 'undefined' && navigator.clipboard?.writeText) {
      try { await navigator.clipboard.writeText(generatedLink); copiedH5Link = true; } catch { copiedH5Link = false; }
    }

    showDistributeModal.value = false;
    isDistributionMockLoading.value = false;
    selectedChannels.value = [];
    selectedClasses.value = [];
    if (selectedChannelSnapshot.includes('h5')) { showToastMessage(copiedH5Link ? '🔗 H5 互动链接已生成并复制到剪贴板！' : '🔗 H5 互动链接已生成，可立即分享给学生！'); return; }
    showToastMessage(selectedClassSnapshot.length === 1 ? `🎉 任务已成功同步至【${selectedClassSnapshot[0]}】！` : `🎉 任务已成功同步至【${selectedClassSnapshot[0]}】等 ${selectedClassSnapshot.length} 个班级！`);
  };

  watch(() => props.projectId, () => { void loadProject(); }, { immediate: true });

  watch(() => route.query.template, (tpl) => {
    if (tpl === 'ai-games') { showMode.value = 'ai-games'; activeGameIndex.value = 0; }
    else if (tpl === 'momentum') {
      isGenerating.value = true; isGenerated.value = false;
      resetWorkspaceLessonPlanRewrite();
      setWorkspaceLessonPlan({ title: '《动量守恒实验的沉浸式课堂设计》', content: '', contentFormat: 'html', analysis: momentumAnalysis });
      activeTab.value = 'lesson-plan';
      window.setTimeout(() => {
        setWorkspaceLessonPlan({
          title: '《动量守恒实验的沉浸式课堂设计》',
          content: '<div class="prose max-w-none text-gray-800"><h2 class="text-2xl font-bold mb-4 text-indigo-900">一、 核心教学目标</h2><p class="mb-2"><strong>1. 物理观念：</strong>深刻理解系统动量守恒的条件，建立"碰撞前后系统总动量保持不变"的微观与宏观联系。</p><p class="mb-4"><strong>2. 科学思维：</strong>通过气垫导轨实验，运用理想化模型（忽略摩擦力），培养通过实验数据验证物理规律的实证思维。</p><h2 class="text-2xl font-bold mt-8 mb-4 text-indigo-900">二、 教学环节设计</h2><div class="pl-4 border-l-4 border-indigo-200 mb-4"><h3 class="text-lg font-semibold mb-1 text-indigo-700">环节一：创设情境 (5分钟)</h3><p class="text-gray-600">播放台球开球的慢动作视频，引入碰撞概念。提问：碰撞前后，什么物理量可能保持不变？</p></div><div class="pl-4 border-l-4 border-indigo-200 mb-4"><h3 class="text-lg font-semibold mb-1 text-indigo-700">环节二：交互探索 (15分钟)</h3><p class="text-gray-600">调用 3D 物理沙盒引擎，让学生在屏幕上拖拽不同质量的滑块进行对心碰撞，记录碰撞前后的速度。</p></div><div class="pl-4 border-l-4 border-indigo-200 mb-4"><h3 class="text-lg font-semibold mb-1 text-indigo-700">环节三：公式推导与总结 (10分钟)</h3><p class="text-gray-600">引导学生发现 m₁v₁ + m₂v₂ = m₁v₁\' + m₂v₂\'</p></div></div>',
          contentFormat: 'html', analysis: momentumAnalysis,
        });
        isGenerating.value = false; isGenerated.value = true;
      }, 1500);
    } else { showMode.value = 'normal'; }
  }, { immediate: true });

  watch(() => route.query.demoMode, (mode) => {
    if (mode === 'ai-ppt') { showMode.value = 'ai-ppt-demo'; activeTab.value = 'ppt'; }
  }, { immediate: true });

  const handleExternalUploadRequest = () => { promptAttachmentUpload(); };
  onMounted(() => { window.addEventListener('workspace-open-upload', handleExternalUploadRequest); });
  onBeforeUnmount(() => { window.removeEventListener('workspace-open-upload', handleExternalUploadRequest); });

  return {
    tabs, activeTab, showMode, generatedTools, attachments, projectDetail,
    showMaterialChangeAlert, showAttachments, isProjectLoading, isUploading, isPackaging,
    generatingToolIds, generationProgress, generationStatus, fileInput,
    showDistributeModal, showToast, toastMessage, selectedChannels, selectedClasses, isDistributionMockLoading,
    isGenerating, isGenerated, activeGameIndex,
    distributionChannels, distributionClassOptions, momentumAnalysis,
    projectContents, isGeneratingContent, isLorentzDemoProject, isDistributionReady,
    hasGeneratedContent, isToolGenerating, getCurrentAttachmentList,
    formatFileSize, handleGenerate, regenerateContent, requestToolGeneration,
    promptAttachmentUpload, handleAttachmentSelected, deleteAttachment,
    handlePackageDownload, toggleSelection, confirmDistribution, showToastMessage,
  };
}
