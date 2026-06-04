<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import {
  ArrowUpRight,
  Clock,
  FileText,
  Loader2,
  Megaphone,
  Paperclip,
  Search,
  Send,
  Share2,
  Sparkles,
  Trash2,
  UserCircle2,
  X,
} from 'lucide-vue-next';
import { apiClient } from '../api/client';
import type { ProjectDetail, ProjectRecord } from '../types';
import { useShowcaseCenter } from '../utils/showcaseCenter';

const emit = defineEmits<{
  (e: 'switch-view', view: string, payload?: unknown): void;
  (e: 'open-project', projectId: number, projectName?: string): void;
}>();

const searchQuery = ref('');
const isLoading = ref(false);
const isDeleting = ref<number | null>(null);
const projects = ref<ProjectRecord[]>([]);
const selectedProject = ref<ProjectDetail | null>(null);
const isLoadingDetail = ref(false);
const showToast = ref(false);
const toastMessage = ref('');
const editingCategoryProjectId = ref<number | null>(null);
const editingCategoryContext = ref<'list' | 'detail' | null>(null);
const categoryDraft = ref('');
const categorySavingId = ref<number | null>(null);
const categoryOptions = ref(['物理', '数学', '化学', '语文', '英语', '计算机']);
const showShareModal = ref(false);
const teacherQuery = ref('');
const selectedTeacher = ref('李老师');
const isSharing = ref(false);
const isPublishing = ref(false);

const teacherOptions = ['李老师', '王老师', '陈老师', '赵老师', '周老师', '教研组长'];
const { publishProjectToShowcase, isProjectPublished } = useShowcaseCenter();

const showToastMessage = (msg: string) => {
  toastMessage.value = msg;
  showToast.value = true;
  window.setTimeout(() => {
    showToast.value = false;
  }, 3000);
};

const getErrorDetail = (error: unknown) => {
  if (error && typeof error === 'object') {
    const response = error as { response?: { data?: { detail?: unknown; message?: unknown } }; message?: unknown };
    const detail = response.response?.data?.detail;
    if (typeof detail === 'string' && detail.trim()) {
      return detail;
    }

    const message = response.response?.data?.message;
    if (typeof message === 'string' && message.trim()) {
      return message;
    }

    if (typeof response.message === 'string' && response.message.trim()) {
      return response.message;
    }
  }

  return error instanceof Error ? error.message : '未知错误';
};

const wait = (duration: number) => new Promise((resolve) => {
  window.setTimeout(resolve, duration);
});

const filteredProjects = computed(() => {
  if (!searchQuery.value.trim()) return projects.value;
  const keyword = searchQuery.value.toLowerCase();
  return projects.value.filter((project) => {
    const content = [project.name, project.description || '', project.subject || ''].join(' ').toLowerCase();
    return content.includes(keyword);
  });
});

const availableCategoryOptions = computed(() => Array.from(new Set([
  ...categoryOptions.value,
  ...projects.value.map((project) => project.subject).filter((subject): subject is string => Boolean(subject)),
])));

const filteredTeachers = computed(() => {
  if (!teacherQuery.value.trim()) return teacherOptions;
  return teacherOptions.filter((teacher) => teacher.includes(teacherQuery.value.trim()));
});

const generatedAssetLabels = computed(() => {
  if (!selectedProject.value) return [];

  return Object.keys(selectedProject.value.contents || {}).map((key) => {
    const labelMap: Record<string, string> = {
      ppt: 'PPT',
      'lesson-plan': '教案',
      video: '短视频',
      game: '互动游戏',
      blog: '博客',
    };
    return labelMap[key] || key;
  });
});

const projectPublished = computed(() => {
  if (!selectedProject.value) return false;
  return isProjectPublished(selectedProject.value.id);
});

const loadProjects = async () => {
  isLoading.value = true;
  try {
    const response = await apiClient.get<ProjectRecord[] | { data?: ProjectRecord[] }>('/api/projects');
    const payload = response as unknown;
    const projectList = Array.isArray(payload)
      ? payload as ProjectRecord[]
      : Array.isArray(response.data)
        ? response.data
        : Array.isArray((response.data as { data?: ProjectRecord[] } | undefined)?.data)
          ? (response.data as { data?: ProjectRecord[] }).data || []
          : [];

    projects.value = projectList;
    if (projectList.length > 0) {
      const nextProjectId = selectedProject.value && projectList.some((project) => project.id === selectedProject.value?.id)
        ? selectedProject.value.id
        : projectList[0].id;
      await loadProjectDetail(nextProjectId);
    } else {
      selectedProject.value = null;
    }
  } catch (error) {
    const detail = getErrorDetail(error);
    console.error('加载历史项目失败:', error);
    showToastMessage(`加载历史项目失败：${detail}`);
  } finally {
    isLoading.value = false;
  }
};

const loadProjectDetail = async (id: number) => {
  isLoadingDetail.value = true;
  try {
    const resp = await apiClient.get<ProjectDetail>(`/api/projects/${id}`);
    selectedProject.value = resp.data;
  } catch (error) {
    const detail = getErrorDetail(error);
    console.error('加载项目详情失败:', error);
    showToastMessage(`加载项目详情失败：${detail}`);
  } finally {
    isLoadingDetail.value = false;
  }
};

const selectCourse = (id: number) => {
  void loadProjectDetail(id);
};

const openCategoryEditor = (project: ProjectRecord | ProjectDetail, context: 'list' | 'detail') => {
  editingCategoryProjectId.value = project.id;
  editingCategoryContext.value = context;
  categoryDraft.value = project.subject || '';
};

const closeCategoryEditor = () => {
  editingCategoryProjectId.value = null;
  editingCategoryContext.value = null;
  categoryDraft.value = '';
};

const syncProjectCategory = (projectId: number, subject: string | null) => {
  projects.value = projects.value.map((project) => (
    project.id === projectId ? { ...project, subject } : project
  ));

  if (selectedProject.value?.id === projectId) {
    selectedProject.value = {
      ...selectedProject.value,
      subject,
    };
  }
};

const saveProjectCategory = async (projectId: number, categoryValue = categoryDraft.value) => {
  const normalized = categoryValue.trim();
  categorySavingId.value = projectId;
  try {
    await apiClient.put(`/api/projects/${projectId}`, { subject: normalized || null });
    if (normalized && !categoryOptions.value.includes(normalized)) {
      categoryOptions.value = [...categoryOptions.value, normalized];
    }
    syncProjectCategory(projectId, normalized || null);
    closeCategoryEditor();
    showToastMessage(normalized ? `项目分类已更新为「${normalized}」` : '项目分类已清空');
  } catch (error) {
    showToastMessage(error instanceof Error ? error.message : '分类更新失败');
  } finally {
    categorySavingId.value = null;
  }
};

const deleteProject = async (id: number) => {
  if (!confirm('确定要删除此项目吗？')) return;
  isDeleting.value = id;
  try {
    await apiClient.delete(`/api/projects/${id}`);
    projects.value = projects.value.filter((project) => project.id !== id);
    if (selectedProject.value?.id === id) {
      selectedProject.value = null;
      if (projects.value.length > 0) {
        await loadProjectDetail(projects.value[0].id);
      }
    }
    showToastMessage('项目已删除');
  } catch (error) {
    showToastMessage(error instanceof Error ? error.message : '删除失败');
  } finally {
    isDeleting.value = null;
  }
};

const continueEditing = () => {
  if (selectedProject.value) {
    emit('open-project', selectedProject.value.id, selectedProject.value.name);
  }
};

const openShareModal = () => {
  if (!selectedProject.value) return;
  teacherQuery.value = '';
  selectedTeacher.value = '李老师';
  showShareModal.value = true;
};

const confirmShare = async () => {
  if (!selectedTeacher.value || isSharing.value) return;
  isSharing.value = true;
  await wait(1000);
  isSharing.value = false;
  showShareModal.value = false;
  showToastMessage(`🎉 已成功共享给 ${selectedTeacher.value}！`);
};

const publishCurrentProject = async () => {
  if (!selectedProject.value || isPublishing.value) return;
  isPublishing.value = true;
  await wait(1000);
  publishProjectToShowcase(selectedProject.value);
  isPublishing.value = false;
  showToastMessage('✅ 上传成功！已同步至优秀案例。');
};

const formatDate = (dateText: string) => new Date(dateText).toLocaleString('zh-CN', {
  year: 'numeric',
  month: '2-digit',
  day: '2-digit',
  hour: '2-digit',
  minute: '2-digit',
});

watch(filteredTeachers, (teachers) => {
  if (teachers.length === 0) {
    selectedTeacher.value = '';
    return;
  }

  if (!teachers.includes(selectedTeacher.value)) {
    selectedTeacher.value = teachers[0];
  }
}, { immediate: true });

onMounted(() => {
  void loadProjects();
});
</script>

<template>
  <div class="flex h-full min-w-0 flex-1 overflow-hidden bg-[radial-gradient(circle_at_top_left,_rgba(186,230,253,0.2),_transparent_28%),linear-gradient(180deg,_rgba(248,250,252,0.96),_rgba(255,255,255,0.98))]">
    <aside class="w-[340px] flex-shrink-0 border-r border-white/60 bg-white/30 p-5 backdrop-blur-xl">
      <div class="liquid-glass flex h-full flex-col rounded-[34px] p-5">
        <div>
          <div class="text-sm font-black uppercase tracking-[0.24em] text-slate-400">历史档案</div>
          <h2 class="mt-2 text-2xl font-black text-slate-900">项目沉淀中心</h2>
          <p class="mt-2 text-sm leading-7 text-slate-500">搜索项目、调整分类，并从这里发起分享与发布。</p>
        </div>

        <label class="liquid-glass-input mt-5 flex items-center gap-3 rounded-[22px] px-4 py-3">
          <Search class="h-4 w-4 text-slate-400" />
          <input v-model="searchQuery" type="text" placeholder="搜索课程名称、知识点..." class="w-full bg-transparent text-sm font-medium text-slate-700 outline-none placeholder:text-slate-400" />
        </label>

        <div class="mt-5 flex-1 space-y-3 overflow-y-auto pr-1 custom-scrollbar">
          <div v-if="isLoading" class="liquid-glass-soft rounded-[24px] px-4 py-4 text-sm font-medium text-slate-500">加载中...</div>
          <div v-else-if="filteredProjects.length === 0" class="liquid-glass-soft rounded-[24px] px-4 py-4 text-sm font-medium text-slate-500">暂无项目记录</div>
          <button
            v-for="project in filteredProjects"
            :key="project.id"
            @click="selectCourse(project.id)"
            :class="selectedProject?.id === project.id ? 'border-sky-200 bg-sky-50/70 shadow-[0_18px_36px_rgba(125,211,252,0.2)]' : 'border-white/70 bg-white/48 hover:bg-white/68'"
            class="group w-full rounded-[24px] border px-4 py-4 text-left backdrop-blur-xl transition-all"
          >
            <div class="flex items-start justify-between gap-3">
              <div>
                <div class="line-clamp-2 text-base font-black text-slate-900">{{ project.name }}</div>
                <div class="mt-2 flex items-center gap-2 text-xs font-semibold text-slate-400">
                  <Clock class="h-3.5 w-3.5" />
                  {{ formatDate(project.updated_at || project.created_at) }}
                </div>
              </div>
              <button @click.stop="deleteProject(project.id)" class="rounded-full p-2 text-slate-300 transition-colors hover:bg-rose-50 hover:text-rose-500">
                <Trash2 v-if="isDeleting !== project.id" class="h-4 w-4" />
                <Loader2 v-else class="h-4 w-4 animate-spin" />
              </button>
            </div>
            <div class="mt-4 flex flex-wrap items-center gap-2">
              <div class="relative">
                <button @click.stop="openCategoryEditor(project, 'list')" class="rounded-full border border-white/80 bg-white/72 px-3 py-1 text-xs font-bold text-slate-600 shadow-[inset_0_1px_0_rgba(255,255,255,0.65)]">
                  {{ project.subject || '未分类' }}
                </button>
                <div v-if="editingCategoryProjectId === project.id && editingCategoryContext === 'list'" class="liquid-glass absolute left-0 top-full z-20 mt-3 w-64 rounded-[24px] p-4 shadow-[0_20px_50px_rgba(15,23,42,0.18)]">
                  <div class="mb-3 flex flex-wrap gap-2">
                    <button v-for="option in availableCategoryOptions" :key="option" @click.stop="saveProjectCategory(project.id, option)" class="liquid-glass-chip text-[11px]">
                      {{ option }}
                    </button>
                  </div>
                  <input v-model="categoryDraft" @keydown.enter.prevent="saveProjectCategory(project.id)" type="text" placeholder="输入新分类并回车" class="liquid-glass-input w-full rounded-[18px] px-3 py-2 text-xs text-slate-700 outline-none placeholder:text-slate-400" />
                  <div class="mt-3 flex justify-end gap-2">
                    <button @click.stop="closeCategoryEditor" class="px-3 py-1 text-xs font-bold text-slate-400">取消</button>
                    <button @click.stop="saveProjectCategory(project.id)" class="px-3 py-1 text-xs font-bold text-sky-600">
                      <span v-if="categorySavingId !== project.id">保存</span>
                      <span v-else>保存中...</span>
                    </button>
                  </div>
                </div>
              </div>
              <span class="rounded-full border border-emerald-100 bg-emerald-50/78 px-3 py-1 text-xs font-bold text-emerald-600">
                {{ project.status || 'active' }}
              </span>
            </div>
          </button>
        </div>
      </div>
    </aside>

    <main class="flex-1 overflow-y-auto p-6 custom-scrollbar lg:p-8">
      <div v-if="isLoadingDetail" class="flex h-full items-center justify-center text-slate-400">
        <Loader2 class="h-8 w-8 animate-spin" />
      </div>
      <div v-else-if="!selectedProject" class="flex h-full items-center justify-center">
        <div class="liquid-glass rounded-[34px] px-8 py-10 text-center">
          <div class="text-xl font-black text-slate-900">{{ projects.length === 0 ? '暂无历史项目' : '请选择一个项目查看详情' }}</div>
          <p class="mt-3 text-sm text-slate-500">发布、分享和继续编辑都将在这里完成。</p>
        </div>
      </div>
      <div v-else class="mx-auto max-w-6xl space-y-6">
        <section class="liquid-glass overflow-hidden rounded-[36px] p-7 md:p-8">
          <div class="flex flex-col gap-6 xl:flex-row xl:items-start xl:justify-between">
            <div class="max-w-3xl space-y-4">
              <div class="flex flex-wrap items-center gap-2 text-sm font-black text-sky-700">
                <span class="rounded-full border border-white/80 bg-white/72 px-3 py-1 shadow-[inset_0_1px_0_rgba(255,255,255,0.7)]">{{ selectedProject.grade || '未设置学段' }}</span>
                <div class="relative">
                  <button @click="openCategoryEditor(selectedProject, 'detail')" class="rounded-full border border-white/80 bg-white/72 px-3 py-1 shadow-[inset_0_1px_0_rgba(255,255,255,0.7)]">
                    {{ selectedProject.subject || '未分类' }}
                  </button>
                  <div v-if="editingCategoryProjectId === selectedProject.id && editingCategoryContext === 'detail'" class="liquid-glass absolute left-0 top-full z-20 mt-3 w-72 rounded-[26px] p-4 shadow-[0_20px_50px_rgba(15,23,42,0.18)]">
                    <div class="text-[11px] font-black uppercase tracking-[0.22em] text-slate-400">选择或创建分类</div>
                    <div class="mt-3 flex flex-wrap gap-2">
                      <button v-for="option in availableCategoryOptions" :key="option" @click="saveProjectCategory(selectedProject.id, option)" class="liquid-glass-chip text-[11px]">
                        {{ option }}
                      </button>
                    </div>
                    <input v-model="categoryDraft" @keydown.enter.prevent="saveProjectCategory(selectedProject.id)" type="text" placeholder="输入自定义分类并回车" class="liquid-glass-input mt-3 w-full rounded-[18px] px-4 py-3 text-sm text-slate-700 outline-none placeholder:text-slate-400" />
                    <div class="mt-3 flex items-center justify-between">
                      <button @click="saveProjectCategory(selectedProject.id, '')" class="text-xs font-bold text-slate-400">清空分类</button>
                      <div class="flex gap-2">
                        <button @click="closeCategoryEditor" class="px-3 py-1 text-xs font-bold text-slate-400">取消</button>
                        <button @click="saveProjectCategory(selectedProject.id)" class="px-3 py-1 text-xs font-bold text-sky-600">保存</button>
                      </div>
                    </div>
                  </div>
                </div>
                <span v-if="projectPublished" class="rounded-full border border-emerald-200 bg-emerald-100/76 px-3 py-1 text-emerald-700">已同步到优秀案例</span>
              </div>
              <div>
                <h1 class="text-4xl font-black text-slate-900">{{ selectedProject.name }}</h1>
                <p class="mt-4 max-w-3xl text-sm leading-8 text-slate-600">{{ selectedProject.description || '暂无项目描述' }}</p>
              </div>
              <div class="flex flex-wrap gap-2">
                <span v-for="label in generatedAssetLabels" :key="label" class="rounded-full border border-white/80 bg-white/72 px-3 py-1 text-xs font-bold text-slate-600">
                  {{ label }}
                </span>
                <span v-if="generatedAssetLabels.length === 0" class="rounded-full border border-white/80 bg-white/72 px-3 py-1 text-xs font-bold text-slate-400">尚未生成教学资产</span>
              </div>
            </div>
            <div class="grid w-full max-w-[360px] gap-3">
              <button @click="continueEditing" class="liquid-glass-button flex items-center justify-between rounded-[24px] px-5 py-4 text-sm font-black text-slate-800">
                继续编辑项目
                <ArrowUpRight class="h-4 w-4" />
              </button>
              <button @click="openShareModal" class="liquid-glass-button flex items-center justify-between rounded-[24px] bg-sky-500/10 px-5 py-4 text-sm font-black text-slate-800">
                <span class="inline-flex items-center gap-2">
                  <Share2 class="h-4 w-4" />
                  👥 分享给老师
                </span>
                <ArrowUpRight class="h-4 w-4" />
              </button>
              <button @click="publishCurrentProject" :disabled="isPublishing" class="liquid-glass-button flex items-center justify-between rounded-[24px] bg-emerald-500/12 px-5 py-4 text-sm font-black text-slate-800 disabled:cursor-not-allowed disabled:opacity-60">
                <span class="inline-flex items-center gap-2">
                  <Megaphone class="h-4 w-4" />
                  🚀 一键发布到优秀案例
                </span>
                <Loader2 v-if="isPublishing" class="h-4 w-4 animate-spin" />
                <ArrowUpRight v-else class="h-4 w-4" />
              </button>
            </div>
          </div>
        </section>

        <section class="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
          <div class="space-y-6">
            <div class="liquid-glass rounded-[32px] p-6">
              <div class="flex items-center justify-between">
                <h3 class="flex items-center gap-2 text-lg font-black text-slate-900">
                  <Paperclip class="h-4 w-4 text-sky-600" />
                  参考资料
                </h3>
                <span class="rounded-full border border-white/80 bg-white/72 px-3 py-1 text-xs font-bold text-slate-500">{{ selectedProject.attachments.length }} 份</span>
              </div>
              <div class="mt-5 space-y-3">
                <div v-if="selectedProject.attachments.length === 0" class="liquid-glass-soft rounded-[22px] px-4 py-4 text-sm text-slate-400">暂无附件</div>
                <div v-for="attachment in selectedProject.attachments" :key="attachment.id" class="liquid-glass-soft flex items-start gap-3 rounded-[22px] px-4 py-4">
                  <div class="flex h-10 w-10 items-center justify-center rounded-2xl bg-white/75 text-sky-600 shadow-[inset_0_1px_0_rgba(255,255,255,0.7)]">
                    <FileText class="h-4 w-4" />
                  </div>
                  <div class="min-w-0">
                    <div class="truncate text-sm font-black text-slate-800">{{ attachment.original_name }}</div>
                    <div class="mt-1 text-xs text-slate-400">{{ (attachment.file_size / 1024).toFixed(1) }} KB</div>
                  </div>
                </div>
              </div>
            </div>

            <div class="liquid-glass rounded-[32px] p-6">
              <h3 class="text-lg font-black text-slate-900">项目说明</h3>
              <div class="liquid-glass-soft mt-5 rounded-[24px] px-5 py-5">
                <p class="text-sm leading-8 text-slate-600">{{ selectedProject.description || '暂无项目说明' }}</p>
              </div>
            </div>
          </div>

          <div class="space-y-6">
            <div class="liquid-glass rounded-[32px] p-6">
              <h3 class="flex items-center gap-2 text-lg font-black text-slate-900">
                <Sparkles class="h-4 w-4 text-emerald-500" />
                💡 资产流转指南
              </h3>
              <div class="mt-5 space-y-4">
                <div class="liquid-glass-soft rounded-[24px] px-5 py-5">
                  <div class="text-xs font-black uppercase tracking-[0.22em] text-slate-400">共享协同</div>
                  <div class="mt-2 text-base font-black text-slate-900">支持教师一键共享</div>
                  <div class="mt-2 text-sm leading-7 text-slate-500">点击上方【分享给老师】，即可将当前课件、教案等核心资产打包发送给教研组同事，支持跨年级、跨学科高效协同备课。</div>
                </div>
                <div class="liquid-glass-soft rounded-[24px] px-5 py-5">
                  <div class="text-xs font-black uppercase tracking-[0.22em] text-slate-400">成果沉淀</div>
                  <div class="mt-2 text-base font-black text-slate-900">沉淀至校级优秀案例</div>
                  <div class="mt-2 text-sm leading-7 text-slate-500">点击【一键发布到优秀案例】，将您的优质教学成果沉淀至公共资源库，供全校教师检索、学习与复用，最大化教学价值。</div>
                </div>
              </div>
            </div>

            <div class="liquid-glass rounded-[32px] p-6">
              <h3 class="text-lg font-black text-slate-900">项目信息</h3>
              <div class="mt-5 space-y-4">
                <div class="liquid-glass-soft rounded-[24px] px-5 py-5">
                  <div class="flex items-center justify-between text-xs font-black uppercase tracking-[0.22em] text-slate-400">
                    <span>状态</span>
                    <span>{{ selectedProject.status || 'active' }}</span>
                  </div>
                  <div class="mt-4 space-y-2 text-sm text-slate-500">
                    <p>创建时间：{{ formatDate(selectedProject.created_at) }}</p>
                    <p>更新时间：{{ formatDate(selectedProject.updated_at || selectedProject.created_at) }}</p>
                    <p>附件数量：{{ selectedProject.attachments.length }}</p>
                  </div>
                </div>
                <button @click="deleteProject(selectedProject.id)" class="w-full rounded-[24px] border border-rose-200 bg-rose-50/78 px-5 py-4 text-sm font-black text-rose-500 transition-colors hover:bg-rose-100/86">
                  <span class="inline-flex items-center gap-2">
                    <Trash2 class="h-4 w-4" />
                    删除此项目
                  </span>
                </button>
              </div>
            </div>
          </div>
        </section>
      </div>
    </main>

    <Transition name="scale">
      <div v-if="showShareModal" class="fixed inset-0 z-[120] flex items-center justify-center p-6">
        <div class="absolute inset-0 bg-slate-950/22 backdrop-blur-md" @click="showShareModal = false"></div>
        <div class="liquid-glass relative w-full max-w-2xl rounded-[34px] p-6 shadow-[0_28px_80px_rgba(15,23,42,0.22)]">
          <div class="flex items-start justify-between gap-4">
            <div>
              <div class="text-sm font-black uppercase tracking-[0.22em] text-slate-400">教师共享</div>
              <h3 class="mt-2 text-2xl font-black text-slate-900">👥 分享给老师</h3>
              <p class="mt-2 text-sm leading-7 text-slate-500">搜索教师并发送当前项目，模拟协同备课共享链路。</p>
            </div>
            <button @click="showShareModal = false" class="liquid-glass-button flex h-11 w-11 items-center justify-center rounded-full text-slate-500">
              <X class="h-5 w-5" />
            </button>
          </div>

          <label class="liquid-glass-input mt-6 flex items-center gap-3 rounded-[22px] px-4 py-3">
            <Search class="h-4 w-4 text-slate-400" />
            <input v-model="teacherQuery" type="text" placeholder="搜索老师，例如：李老师" class="w-full bg-transparent text-sm font-medium text-slate-700 outline-none placeholder:text-slate-400" />
          </label>

          <div class="mt-5 grid gap-3 sm:grid-cols-2">
            <button
              v-for="teacher in filteredTeachers"
              :key="teacher"
              @click="selectedTeacher = teacher"
              :class="selectedTeacher === teacher ? 'border-sky-200 bg-sky-50/80 text-sky-700' : 'border-white/80 bg-white/65 text-slate-600'"
              class="rounded-[22px] border px-4 py-4 text-left transition-colors"
            >
              <div class="flex items-center gap-3">
                <div class="flex h-11 w-11 items-center justify-center rounded-2xl bg-white/80 shadow-[inset_0_1px_0_rgba(255,255,255,0.7)]">
                  <UserCircle2 class="h-5 w-5" />
                </div>
                <div>
                  <div class="text-sm font-black">{{ teacher }}</div>
                  <div class="mt-1 text-xs text-slate-400">可接收当前项目共享</div>
                </div>
              </div>
            </button>
          </div>

          <div v-if="filteredTeachers.length === 0" class="liquid-glass-soft mt-5 rounded-[22px] px-4 py-4 text-sm text-slate-500">没有匹配到教师，请调整搜索关键词。</div>

          <div class="mt-6 flex flex-col gap-3 sm:flex-row sm:justify-end">
            <button @click="showShareModal = false" class="liquid-glass-button rounded-[22px] px-5 py-3 text-sm font-bold text-slate-600">取消</button>
            <button @click="confirmShare" :disabled="isSharing || !selectedTeacher" class="liquid-glass-button flex items-center justify-center gap-2 rounded-[22px] bg-sky-500/12 px-5 py-3 text-sm font-black text-slate-800 disabled:cursor-not-allowed disabled:opacity-60">
              <Loader2 v-if="isSharing" class="h-4 w-4 animate-spin" />
              <Send v-else class="h-4 w-4" />
              {{ isSharing ? '发送中...' : '发送给老师' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>

    <Transition name="fade">
      <div v-if="showToast" class="fixed bottom-8 left-1/2 z-[130] -translate-x-1/2">
        <div class="liquid-glass flex items-center gap-3 rounded-full px-5 py-3 shadow-[0_20px_40px_rgba(15,23,42,0.16)]">
          <div class="h-2.5 w-2.5 rounded-full bg-emerald-400"></div>
          <span class="text-sm font-bold text-slate-700">{{ toastMessage }}</span>
        </div>
      </div>
    </Transition>
  </div>
</template>