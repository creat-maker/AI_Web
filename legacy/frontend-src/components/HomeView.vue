<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import {
  ArrowUpRight,
  Clock,
  FileJson,
  FileText,
  Gamepad2,
  Search,
  Sparkles,
  Upload,
  UserCircle,
  Video,
  X,
} from 'lucide-vue-next';
import { apiClient } from '../api/client';
import type { ProjectRecord, ShowcaseCase } from '../types';
import { useShowcaseCenter } from '../utils/showcaseCenter';

const emit = defineEmits<{
  (e: 'switch-view', view: string, type?: string): void;
  (e: 'open-wizard', intent: string): void;
  (e: 'open-project', projectId: number, projectName?: string): void;
  (e: 'clone-template', template: string): void;
}>();

const quickTools = [
  { name: '生成PPT', type: 'ppt', icon: Upload, accent: 'from-sky-400/70 to-cyan-300/70' },
  { name: '生成教案', type: 'lesson-plan', icon: FileText, accent: 'from-amber-300/70 to-orange-300/70' },
  { name: '生成视频', type: 'video', icon: Video, accent: 'from-emerald-300/70 to-teal-300/70' },
  { name: '生成互动小游戏', type: 'game', icon: Gamepad2, accent: 'from-rose-300/70 to-pink-300/70' },
  { name: '生成博客', type: 'blog', icon: FileJson, accent: 'from-violet-300/70 to-fuchsia-300/70' },
] as const;

const iconBySubject: Record<string, string> = {
  物理: '🧪',
  数学: '📐',
  语文: '📚',
  英语: '🌍',
  生物: '🧬',
  化学: '⚗️',
  计算机: '💻',
};

const historyList = ref<ProjectRecord[]>([]);
const isHistoryLoading = ref(false);
const showAllHistory = ref(false);
const selectedCase = ref<ShowcaseCase | null>(null);
const showToast = ref(false);
const toastMessage = ref('');
const caseQuery = ref('');
const selectedCategory = ref('全部');

const { showcaseCases, initializeShowcaseCenter } = useShowcaseCenter();

const showToastMessage = (message: string) => {
  toastMessage.value = message;
  showToast.value = true;
  window.setTimeout(() => {
    showToast.value = false;
  }, 3000);
};

const formatDate = (dateText: string) => new Date(dateText).toLocaleString('zh-CN', {
  year: 'numeric',
  month: '2-digit',
  day: '2-digit',
  hour: '2-digit',
  minute: '2-digit',
});

const loadProjects = async () => {
  isHistoryLoading.value = true;
  try {
    const response = await apiClient.get<ProjectRecord[]>('/api/projects/');
    historyList.value = response.data;
  } catch {
    showToastMessage('加载历史项目失败');
  } finally {
    isHistoryLoading.value = false;
  }
};

const recentHistory = computed(() => historyList.value.slice(0, 4));

const categoryOptions = computed(() => {
  const defaults = ['全部', '物理', '数学', '计算机', '化学', '语文'];
  return Array.from(new Set([
    ...defaults,
    ...showcaseCases.value.map((item) => item.category).filter(Boolean),
  ]));
});

const filteredShowcaseCases = computed(() => {
  const keyword = caseQuery.value.trim().toLowerCase();

  return showcaseCases.value.filter((item) => {
    const matchesCategory = selectedCategory.value === '全部' || item.category === selectedCategory.value;
    if (!matchesCategory) {
      return false;
    }

    if (!keyword) {
      return true;
    }

    const searchableText = [
      item.title,
      item.desc,
      item.author,
      item.category,
      ...item.knowledgePoints,
    ].join(' ').toLowerCase();

    return searchableText.includes(keyword);
  });
});

const openProject = (project: ProjectRecord) => {
  emit('open-project', project.id, project.name);
};

const openShowcaseCase = (item: ShowcaseCase) => {
  selectedCase.value = item;
};

const cloneShowcaseCase = (item: ShowcaseCase) => {
  if (item.sourceProjectId) {
    emit('open-project', item.sourceProjectId, item.title);
    selectedCase.value = null;
    return;
  }

  // 平台模板→跳转工作台并注入动量守恒展示数据
  selectedCase.value = null;
  emit('clone-template', 'momentum');
};

const deleteProject = async (id: number) => {
  if (!confirm('确定要删除此项目吗？')) return;
  try {
    await apiClient.delete(`/api/projects/${id}`);
    historyList.value = historyList.value.filter((project) => project.id !== id);
    showToastMessage('项目已删除');
  } catch (error) {
    showToastMessage(error instanceof Error ? error.message : '删除失败');
  }
};

onMounted(() => {
  initializeShowcaseCenter();
  void loadProjects();
});
</script>

<template>
  <div class="mx-auto max-w-6xl space-y-10 pb-10">
    <section class="liquid-glass relative overflow-hidden rounded-[40px] px-8 py-10 md:px-12 md:py-12">
      <div class="absolute inset-0 bg-[radial-gradient(circle_at_top_left,_rgba(125,211,252,0.24),_transparent_32%),radial-gradient(circle_at_top_right,_rgba(253,224,71,0.22),_transparent_28%)]"></div>
      <div class="relative flex flex-col gap-6 lg:flex-row lg:items-end lg:justify-between">
        <div class="max-w-3xl space-y-4">
          <div class="inline-flex items-center gap-2 rounded-full border border-white/70 bg-white/55 px-4 py-2 text-xs font-black tracking-[0.24em] text-sky-700 shadow-[inset_0_1px_0_rgba(255,255,255,0.65)]">
            <Sparkles class="h-4 w-4" />
            生产 · 打包 · 分享 · 沉淀
          </div>
          <h1 class="text-4xl font-black tracking-tight text-slate-900 md:text-5xl">织课 AI 教学闭环平台</h1>
          <p class="max-w-2xl text-[15px] leading-8 text-slate-600 md:text-base">
            从生成课件到沉淀为优秀案例，所有教学资产都在一个工作台里闭环流转，兼顾教师创作效率与校本教研复用价值。
          </p>
        </div>
        <div class="grid gap-4 rounded-[28px] border border-white/80 bg-white/48 p-5 shadow-[0_14px_40px_rgba(148,163,184,0.18)] backdrop-blur-xl sm:grid-cols-2">
          <div>
            <div class="text-xs font-black uppercase tracking-[0.22em] text-slate-400">当前沉淀</div>
            <div class="mt-2 text-3xl font-black text-slate-900">{{ showcaseCases.length }}</div>
            <div class="mt-1 text-sm text-slate-500">优秀案例总量</div>
          </div>
          <div>
            <div class="text-xs font-black uppercase tracking-[0.22em] text-slate-400">最新案例来源</div>
            <div class="mt-2 text-lg font-black text-slate-900">{{ showcaseCases[0]?.category || '综合' }}</div>
            <div class="mt-1 text-sm text-slate-500">支持首页实时联动展示</div>
          </div>
        </div>
      </div>
    </section>

    <section class="space-y-5">
      <div class="flex items-center justify-between">
        <h2 class="text-sm font-black uppercase tracking-[0.26em] text-slate-400">极速生成工具</h2>
        <button @click="emit('open-wizard', 'general')" class="liquid-glass-button rounded-full px-5 py-2 text-sm font-bold text-slate-700">
          新建教学项目
        </button>
      </div>
      <div class="grid gap-5 md:grid-cols-2 xl:grid-cols-5">
        <button
          v-for="tool in quickTools"
          :key="tool.name"
          @click="emit('open-wizard', tool.type)"
          class="liquid-glass-button group rounded-[30px] p-6 text-left"
        >
          <div class="flex items-start justify-between gap-4">
            <div>
              <div :class="['flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br text-slate-900 shadow-[inset_0_1px_0_rgba(255,255,255,0.65)]', tool.accent]">
                <component :is="tool.icon" class="h-6 w-6" />
              </div>
              <div class="mt-5 text-lg font-black text-slate-900">{{ tool.name }}</div>
              <div class="mt-1 text-sm leading-6 text-slate-500">直接进入 AI 工作流，生成可编辑的教学初稿。</div>
            </div>
            <ArrowUpRight class="mt-1 h-5 w-5 text-slate-400 transition-transform duration-300 group-hover:-translate-y-0.5 group-hover:translate-x-0.5" />
          </div>
        </button>
      </div>
    </section>

    <section class="space-y-6">
      <div class="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
        <div>
          <div class="text-sm font-black uppercase tracking-[0.26em] text-slate-400">优秀案例</div>
          <h2 class="mt-2 text-3xl font-black text-slate-900">优秀案例</h2>
          <p class="mt-2 text-sm leading-7 text-slate-500">支持按案例名称、知识点和学科快速检索，历史档案发布后会实时同步到这里。</p>
        </div>
        <div class="rounded-full border border-white/80 bg-white/60 px-4 py-2 text-sm font-semibold text-slate-500 shadow-[0_12px_32px_rgba(148,163,184,0.18)] backdrop-blur-xl">
          当前命中 {{ filteredShowcaseCases.length }} 个案例
        </div>
      </div>

      <div class="liquid-glass rounded-[34px] p-5 md:p-6">
        <div class="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
          <label class="liquid-glass-input flex min-h-[60px] flex-1 items-center gap-3 rounded-[24px] px-4 py-3">
            <Search class="h-5 w-5 text-slate-400" />
            <input
              v-model="caseQuery"
              type="text"
              placeholder="搜索案例名称 / 知识点，例如：动量守恒、TCP/IP、古诗词"
              class="w-full bg-transparent text-sm font-medium text-slate-700 outline-none placeholder:text-slate-400"
            />
          </label>
          <div class="flex flex-wrap gap-2">
            <button
              v-for="category in categoryOptions"
              :key="category"
              @click="selectedCategory = category"
              :class="selectedCategory === category ? 'liquid-glass-chip-active' : 'liquid-glass-chip'"
            >
              {{ category }}
            </button>
          </div>
        </div>
      </div>

      <div v-if="filteredShowcaseCases.length === 0" class="liquid-glass rounded-[34px] px-8 py-12 text-center text-sm font-medium text-slate-500">
        没有匹配到案例，试试更换关键词或切换筛选分类。
      </div>

      <div v-else class="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
        <article
          v-for="item in filteredShowcaseCases"
          :key="item.id"
          class="liquid-glass-button group overflow-hidden rounded-[32px] p-0 text-left"
          @click="openShowcaseCase(item)"
        >
          <div class="relative aspect-[1.18/1] overflow-hidden rounded-t-[32px]">
            <img :src="item.image" :alt="item.title" class="h-full w-full object-cover transition-transform duration-500 group-hover:scale-105" referrerpolicy="no-referrer" />
            <div class="absolute inset-0 bg-gradient-to-t from-slate-900/48 via-transparent to-white/10"></div>
            <div class="absolute left-5 top-5 flex items-center gap-2">
              <span class="rounded-full border border-white/80 bg-white/68 px-3 py-1 text-[11px] font-black tracking-[0.18em] text-slate-700 backdrop-blur-md">
                {{ item.category }}
              </span>
              <span v-if="item.origin === 'published'" class="rounded-full border border-emerald-200/70 bg-emerald-100/78 px-3 py-1 text-[11px] font-black tracking-[0.18em] text-emerald-700 backdrop-blur-md">
                新发布
              </span>
            </div>
          </div>
          <div class="space-y-4 px-5 py-5">
            <div>
              <h3 class="line-clamp-2 text-xl font-black leading-8 text-slate-900">{{ item.title }}</h3>
              <div class="mt-2 flex items-center gap-2 text-sm font-semibold text-sky-700">
                <UserCircle class="h-4 w-4" />
                {{ item.author }}
              </div>
            </div>
            <p class="line-clamp-3 text-sm leading-7 text-slate-500">{{ item.desc }}</p>
            <div class="flex flex-wrap gap-2">
              <span v-for="point in item.knowledgePoints.slice(0, 3)" :key="point" class="rounded-full border border-white/80 bg-white/68 px-3 py-1 text-xs font-bold text-slate-600 shadow-[inset_0_1px_0_rgba(255,255,255,0.65)]">
                {{ point }}
              </span>
            </div>
            <div class="flex items-center justify-between border-t border-white/60 pt-3 text-xs font-semibold text-slate-400">
              <span>{{ formatDate(item.publishedAt) }}</span>
              <span class="inline-flex items-center gap-1 text-slate-600">
                查看详情
                <ArrowUpRight class="h-3.5 w-3.5" />
              </span>
            </div>
          </div>
        </article>
      </div>
    </section>

    <section class="space-y-5">
      <div class="flex items-center justify-between">
        <div>
          <h2 class="text-2xl font-black text-slate-900">我的历史课件</h2>
          <p class="mt-1 text-sm text-slate-500">最近创建或更新的项目会出现在这里，可随时回到工作台继续编辑。</p>
        </div>
        <button @click="showAllHistory = true" class="liquid-glass-button rounded-full px-5 py-2 text-sm font-bold text-slate-700">
          查看全部
        </button>
      </div>
      <div class="grid gap-4">
        <div v-if="isHistoryLoading" class="liquid-glass rounded-[28px] px-6 py-5 text-sm font-medium text-slate-500">正在从后端加载历史项目...</div>
        <div v-else-if="recentHistory.length === 0" class="liquid-glass rounded-[28px] px-6 py-5 text-sm font-medium text-slate-500">后端暂时还没有课程项目，先创建一个吧。</div>
        <div
          v-for="lesson in recentHistory"
          :key="lesson.id"
          class="liquid-glass-button flex flex-col gap-4 rounded-[28px] px-5 py-5 text-left md:flex-row md:items-center md:justify-between"
        >
          <button class="flex items-center gap-4 text-left" @click="openProject(lesson)">
            <div class="flex h-14 w-14 items-center justify-center rounded-2xl bg-white/70 text-2xl shadow-[inset_0_1px_0_rgba(255,255,255,0.7)]">
              {{ iconBySubject[lesson.subject || ''] || '📘' }}
            </div>
            <div>
              <div class="text-lg font-black text-slate-900">{{ lesson.name }}</div>
              <div class="mt-1 text-sm text-slate-500">更新于 {{ formatDate(lesson.updated_at || lesson.created_at) }}</div>
            </div>
          </button>
          <div class="flex items-center gap-3 self-end md:self-auto">
            <span class="rounded-full border border-white/80 bg-white/65 px-3 py-1 text-xs font-bold text-slate-600">{{ lesson.subject || '未分类' }}</span>
            <button @click.stop="openProject(lesson)" class="liquid-glass-button rounded-full px-4 py-2 text-sm font-bold text-slate-700">继续编辑</button>
            <button @click.stop="deleteProject(lesson.id)" class="rounded-full border border-rose-100 bg-rose-50/70 px-4 py-2 text-sm font-bold text-rose-500 transition-colors hover:bg-rose-100/80">删除</button>
          </div>
        </div>
      </div>
    </section>

    <Transition name="fade">
      <div v-if="showAllHistory" class="fixed inset-0 z-[100] flex justify-end">
        <div class="absolute inset-0 bg-slate-950/18 backdrop-blur-sm" @click="showAllHistory = false"></div>
        <div class="liquid-glass relative h-full w-full max-w-3xl rounded-none rounded-l-[36px] px-6 py-6 shadow-[0_28px_80px_rgba(15,23,42,0.22)]">
          <div class="flex items-center justify-between border-b border-white/60 pb-4">
            <div>
              <div class="text-sm font-black uppercase tracking-[0.22em] text-slate-400">历史档案</div>
              <h3 class="mt-2 text-2xl font-black text-slate-900">全部项目历史</h3>
            </div>
            <button @click="showAllHistory = false" class="liquid-glass-button flex h-11 w-11 items-center justify-center rounded-full text-slate-500">
              <X class="h-5 w-5" />
            </button>
          </div>
          <div class="mt-6 space-y-4 overflow-y-auto pr-1 custom-scrollbar" style="max-height: calc(100vh - 140px);">
            <div v-for="item in historyList" :key="item.id" class="liquid-glass-soft flex flex-col gap-4 rounded-[26px] px-5 py-5 md:flex-row md:items-center md:justify-between">
              <div class="flex items-center gap-4">
                <div class="flex h-12 w-12 items-center justify-center rounded-2xl bg-white/72 text-xl shadow-[inset_0_1px_0_rgba(255,255,255,0.7)]">
                  {{ iconBySubject[item.subject || ''] || '📘' }}
                </div>
                <div>
                  <div class="text-base font-black text-slate-900">{{ item.name }}</div>
                  <div class="mt-1 text-sm text-slate-500">{{ formatDate(item.updated_at || item.created_at) }}</div>
                </div>
              </div>
              <div class="flex flex-wrap items-center gap-3">
                <span class="rounded-full border border-white/80 bg-white/68 px-3 py-1 text-xs font-bold text-slate-600">{{ item.subject || '未分类' }}</span>
                <button @click="openProject(item)" class="liquid-glass-button rounded-full px-4 py-2 text-sm font-bold text-slate-700">继续编辑</button>
                <button @click="deleteProject(item.id)" class="rounded-full border border-rose-100 bg-rose-50/70 px-4 py-2 text-sm font-bold text-rose-500 transition-colors hover:bg-rose-100/80">删除</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <Transition name="scale">
      <div v-if="selectedCase" class="fixed inset-0 z-[110] flex items-center justify-center p-6">
        <div class="absolute inset-0 bg-slate-950/24 backdrop-blur-md" @click="selectedCase = null"></div>
        <div class="liquid-glass relative flex w-full max-w-5xl flex-col overflow-hidden rounded-[38px] shadow-[0_28px_80px_rgba(15,23,42,0.22)] lg:flex-row">
          <div class="relative aspect-[1.2/1] lg:w-[48%] lg:aspect-auto">
            <img :src="selectedCase.image" :alt="selectedCase.title" class="h-full w-full object-cover" referrerpolicy="no-referrer" />
            <div class="absolute inset-0 bg-gradient-to-t from-slate-950/50 via-transparent to-white/10"></div>
            <div class="absolute left-6 top-6 rounded-full border border-white/80 bg-white/68 px-4 py-2 text-xs font-black tracking-[0.22em] text-slate-700 backdrop-blur-md">
              {{ selectedCase.category }}
            </div>
          </div>
          <div class="flex flex-1 flex-col justify-between gap-8 p-8 md:p-10">
            <div class="space-y-6">
              <div class="flex items-start justify-between gap-4">
                <div>
                  <h3 class="text-3xl font-black leading-tight text-slate-900">{{ selectedCase.title }}</h3>
                  <div class="mt-3 flex items-center gap-2 text-sm font-semibold text-sky-700">
                    <UserCircle class="h-4 w-4" />
                    {{ selectedCase.author }}
                  </div>
                </div>
                <button @click="selectedCase = null" class="liquid-glass-button flex h-11 w-11 items-center justify-center rounded-full text-slate-500">
                  <X class="h-5 w-5" />
                </button>
              </div>
              <p class="text-sm leading-8 text-slate-600">{{ selectedCase.desc }}</p>
              <div>
                <div class="text-xs font-black uppercase tracking-[0.22em] text-slate-400">知识点标签</div>
                <div class="mt-3 flex flex-wrap gap-2">
                  <span v-for="point in selectedCase.knowledgePoints" :key="point" class="rounded-full border border-white/80 bg-white/68 px-3 py-1.5 text-xs font-bold text-slate-600">
                    {{ point }}
                  </span>
                </div>
              </div>
              <div class="grid gap-4 md:grid-cols-2">
                <div class="liquid-glass-soft rounded-[24px] px-4 py-4">
                  <div class="text-xs font-black uppercase tracking-[0.22em] text-slate-400">发布时间</div>
                  <div class="mt-2 text-base font-black text-slate-900">{{ formatDate(selectedCase.publishedAt) }}</div>
                </div>
                <div class="liquid-glass-soft rounded-[24px] px-4 py-4">
                  <div class="text-xs font-black uppercase tracking-[0.22em] text-slate-400">案例来源</div>
                  <div class="mt-2 text-base font-black text-slate-900">{{ selectedCase.origin === 'published' ? '历史档案发布' : '平台精选模板' }}</div>
                </div>
              </div>
            </div>
            <div class="flex flex-col gap-3 sm:flex-row">
              <button @click="cloneShowcaseCase(selectedCase)" class="liquid-glass-button flex flex-1 items-center justify-center gap-2 rounded-[24px] bg-sky-500/12 px-6 py-4 text-sm font-black text-slate-800">
                <Sparkles class="h-4 w-4" />
                {{ selectedCase.sourceProjectId ? '回到原项目继续编辑' : '克隆灵感到工作台' }}
              </button>
              <button @click="selectedCase = null" class="liquid-glass-button rounded-[24px] px-6 py-4 text-sm font-bold text-slate-600">关闭</button>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <Transition name="fade">
      <div v-if="showToast" class="fixed bottom-8 left-1/2 z-[120] -translate-x-1/2">
        <div class="liquid-glass flex items-center gap-3 rounded-full px-5 py-3 shadow-[0_20px_40px_rgba(15,23,42,0.16)]">
          <div class="h-2.5 w-2.5 rounded-full bg-emerald-400"></div>
          <span class="text-sm font-bold text-slate-700">{{ toastMessage }}</span>
        </div>
      </div>
    </Transition>
  </div>
</template>