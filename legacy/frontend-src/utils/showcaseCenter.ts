import { ref } from 'vue';
import type { ProjectDetail, ShowcaseCase } from '../types';

const STORAGE_KEY = 'zhike-ai-showcase-center';

const subjectCoverMap: Record<string, string> = {
  物理: 'https://picsum.photos/seed/physics-glass/900/700',
  数学: 'https://picsum.photos/seed/math-glass/900/700',
  计算机: 'https://picsum.photos/seed/cs-glass/900/700',
  化学: 'https://picsum.photos/seed/chem-glass/900/700',
  语文: 'https://picsum.photos/seed/chinese-glass/900/700',
  英语: 'https://picsum.photos/seed/english-glass/900/700',
};

const seedShowcaseCases: ShowcaseCase[] = [
  {
    id: 'seed-physics-momentum',
    title: '动量守恒实验的沉浸式课堂设计',
    category: '物理',
    author: '李老师教研组',
    desc: '把碰撞实验、误差分析与分层提问做成完整课堂链路，适合高一到高二物理探究课。',
    image: subjectCoverMap.物理,
    knowledgePoints: ['动量守恒', '碰撞实验', '误差分析', '探究式教学'],
    publishedAt: '2026-04-01T09:30:00.000Z',
    origin: 'seed',
  },
  {
    id: 'seed-math-function',
    title: '函数单调性的可视化推导案例',
    category: '数学',
    author: '王老师共创营',
    desc: '围绕导数变化趋势构建图像推理链，适用于高考复习和专题突破。',
    image: subjectCoverMap.数学,
    knowledgePoints: ['函数单调性', '导数应用', '图像分析', '高考专题'],
    publishedAt: '2026-03-28T14:10:00.000Z',
    origin: 'seed',
  },
  {
    id: 'seed-cs-network',
    title: '网络协议分层的项目化教学范式',
    category: '计算机',
    author: '陈老师实验班',
    desc: '将 TCP/IP、抓包实践和场景任务整合为项目式学习单元，适配中高职与高中信息技术。',
    image: subjectCoverMap.计算机,
    knowledgePoints: ['网络协议', 'TCP/IP', '抓包分析', '项目化教学'],
    publishedAt: '2026-03-22T11:45:00.000Z',
    origin: 'seed',
  },
  {
    id: 'seed-chem-bond',
    title: '化学键与物质结构的跨情境任务包',
    category: '化学',
    author: '张老师教科研',
    desc: '从微观粒子模型到生活材料案例，兼顾概念建模与课堂互动。',
    image: subjectCoverMap.化学,
    knowledgePoints: ['化学键', '物质结构', '粒子模型', '情境任务'],
    publishedAt: '2026-03-18T08:20:00.000Z',
    origin: 'seed',
  },
  {
    id: 'seed-chinese-poem',
    title: '古诗词群文阅读的任务驱动教案',
    category: '语文',
    author: '周老师名师工作室',
    desc: '围绕意象、情感和表达技巧设计连续活动，适合公开课与校本研修。',
    image: subjectCoverMap.语文,
    knowledgePoints: ['古诗词', '群文阅读', '意象分析', '任务驱动'],
    publishedAt: '2026-03-12T13:05:00.000Z',
    origin: 'seed',
  },
];

const showcaseCases = ref<ShowcaseCase[]>([]);
let showcaseInitialized = false;

const cloneCase = (item: ShowcaseCase): ShowcaseCase => ({
  ...item,
  knowledgePoints: [...item.knowledgePoints],
});

const normalizeShowcaseCase = (item: Partial<ShowcaseCase>, index: number): ShowcaseCase => ({
  id: String(item.id || `showcase-${index}`),
  title: String(item.title || `案例 ${index + 1}`),
  category: String(item.category || '综合'),
  author: String(item.author || '织课 AI 教研组'),
  desc: String(item.desc || '暂无案例简介'),
  image: String(item.image || `https://picsum.photos/seed/showcase-${index}/900/700`),
  knowledgePoints: Array.isArray(item.knowledgePoints)
    ? item.knowledgePoints.map((point) => String(point).trim()).filter(Boolean).slice(0, 6)
    : [],
  publishedAt: String(item.publishedAt || new Date().toISOString()),
  origin: item.origin === 'published' ? 'published' : 'seed',
  sourceProjectId: typeof item.sourceProjectId === 'number' ? item.sourceProjectId : null,
});

const persistShowcaseCases = () => {
  if (typeof window === 'undefined') return;
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(showcaseCases.value));
};

const initializeShowcaseCenter = () => {
  if (showcaseInitialized) return;
  showcaseInitialized = true;

  if (typeof window !== 'undefined') {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (raw) {
      try {
        const parsed = JSON.parse(raw);
        if (Array.isArray(parsed) && parsed.length > 0) {
          showcaseCases.value = parsed.map((item, index) => normalizeShowcaseCase(item, index));
          return;
        }
      } catch {
        window.localStorage.removeItem(STORAGE_KEY);
      }
    }
  }

  showcaseCases.value = seedShowcaseCases.map(cloneCase);
  persistShowcaseCases();
};

const extractKnowledgePoints = (project: ProjectDetail) => {
  const tokens = new Set<string>();

  const pushText = (value: unknown) => {
    if (typeof value !== 'string') return;
    value
      .split(/[\n,，。；;、|/]+/)
      .map((item) => item.trim())
      .filter((item) => item.length >= 2 && item.length <= 20)
      .forEach((item) => tokens.add(item));
  };

  pushText(project.subject || '');
  pushText(project.grade || '');
  pushText(project.description || '');

  const pptEntry = project.contents?.ppt;
  if (Array.isArray(pptEntry?.data)) {
    pptEntry.data.slice(0, 3).forEach((slide) => {
      if (slide && typeof slide === 'object') {
        pushText((slide as { title?: string }).title || '');
        const bullets = (slide as { bullets?: unknown }).bullets;
        if (Array.isArray(bullets)) {
          bullets.slice(0, 4).forEach((bullet) => pushText(typeof bullet === 'string' ? bullet : ''));
        }
      }
    });
  }

  const lessonPlan = project.contents?.['lesson-plan'];
  pushText(typeof lessonPlan?.raw_content === 'string' ? lessonPlan.raw_content : '');

  return Array.from(tokens)
    .filter((item) => item !== project.name)
    .slice(0, 6);
};

const buildPublishedCase = (project: ProjectDetail): ShowcaseCase => ({
  id: `project-${project.id}`,
  title: project.name,
  category: project.subject || '综合',
  author: `${project.grade || '校本'}教师团队`,
  desc: (project.description || '').trim() || `由 ${project.subject || '综合学科'} 项目沉淀出的可复用课堂案例，适合继续二次编辑与分享。`,
  image: subjectCoverMap[project.subject || ''] || `https://picsum.photos/seed/project-${project.id}/900/700`,
  knowledgePoints: extractKnowledgePoints(project),
  publishedAt: new Date().toISOString(),
  origin: 'published',
  sourceProjectId: project.id,
});

const publishProjectToShowcase = (project: ProjectDetail) => {
  initializeShowcaseCenter();
  const nextCase = buildPublishedCase(project);
  const existingIndex = showcaseCases.value.findIndex((item) => item.sourceProjectId === project.id || item.id === nextCase.id);

  if (existingIndex >= 0) {
    showcaseCases.value.splice(existingIndex, 1, nextCase);
  } else {
    showcaseCases.value.unshift(nextCase);
  }

  persistShowcaseCases();
  return nextCase;
};

const isProjectPublished = (projectId: number) => {
  initializeShowcaseCenter();
  return showcaseCases.value.some((item) => item.sourceProjectId === projectId);
};

export const useShowcaseCenter = () => {
  initializeShowcaseCenter();

  return {
    showcaseCases,
    initializeShowcaseCenter,
    publishProjectToShowcase,
    isProjectPublished,
  };
};