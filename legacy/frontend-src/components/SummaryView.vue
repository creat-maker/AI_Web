<script setup lang="ts">
import { computed, ref } from 'vue';
import {
  ClipboardCheck,
  Download,
  FileSpreadsheet,
  FileText,
  RotateCcw,
  Sparkles,
  UploadCloud,
} from 'lucide-vue-next';
import { renderMarkdown } from '../utils/content';
import { apiClient } from '@/api/client';
import ClassScoreChart from '../views/exam/components/ClassScoreChart.vue';
import TopErrorsList from '../views/exam/components/TopErrorsList.vue';
import UploadLoader from '../views/exam/components/UploadLoader.vue';
import StatsCards from '../views/exam/components/StatsCards.vue';
import PersonalizedModal from '../views/exam/components/PersonalizedModal.vue';
import Toast from '@/views/workspace/components/Toast.vue';
import {
  DEFAULT_EXAM_RESULT,
  DEFAULT_SMART_GROUPS,
  type ExamResultData,
  type KnowledgeMastery,
  type ScoreDistributionItem,
  type SmartGroup,
  type TopErrorItem,
} from '@/api/mocks/data';
import type { StagedAttachmentRecord } from '../types';

type ViewState = 'upload' | 'analyzing' | 'result';
type AnalysisMode = 'auto' | 'score_sheet' | 'answer_card' | 'free_paper';

interface ReviewItem {
  question: string;
  reason: string;
  confidence: number;
  suggestion: string;
}

interface ExamAnalyzeResponse {
  mode: AnalysisMode;
  status: 'completed' | 'needs_review' | 'failed';
  result: ExamResultData | null;
  reviewItems: ReviewItem[];
  extractedTextPreview?: string;
}

const analysisModeOptions: {
  id: AnalysisMode;
  label: string;
  desc: string;
  icon: typeof UploadCloud;
}[] = [
  { id: 'auto', label: '自动识别', desc: '系统判断材料类型', icon: UploadCloud },
  { id: 'score_sheet', label: '成绩单', desc: 'Excel / CSV 直接统计', icon: FileSpreadsheet },
  { id: 'answer_card', label: '标准答题卡', desc: '固定版式答题卡批阅', icon: ClipboardCheck },
  { id: 'free_paper', label: '原卷/作业', desc: '试卷照片和作业直传', icon: FileText },
];

const modeLabels: Record<AnalysisMode, string> = {
  auto: '自动识别',
  score_sheet: '成绩单模式',
  answer_card: '标准答题卡模式',
  free_paper: '原卷/作业模式',
};

const viewState = ref<ViewState>('result');
const showPersonalizedModal = ref(false);
const isDistributing = ref(false);
const showToast = ref(false);
const toastMessage = ref('');
const selectedUploadName = ref('');
const analysisSource = ref('示例数据');
const selectedMode = ref<AnalysisMode>('auto');
const resolvedMode = ref<AnalysisMode>('auto');
const reviewItems = ref<ReviewItem[]>([]);
const analysisStatus = ref<'completed' | 'needs_review' | 'failed'>('completed');
const uploadInput = ref<HTMLInputElement | null>(null);

const examResult = ref<ExamResultData>({ ...DEFAULT_EXAM_RESULT });
const smartGroups = ref<SmartGroup[]>([...DEFAULT_SMART_GROUPS]);

const completionText = computed(() => `${examResult.value.submittedCount}/${examResult.value.sampleSize} 已提交`);
const hasResult = computed(() => viewState.value === 'result');
const needsReview = computed(() => reviewItems.value.length > 0 || analysisStatus.value === 'needs_review');
const activeModeLabel = computed(() => modeLabels[resolvedMode.value] || '自动识别');

const showToastMessage = (msg: string) => {
  toastMessage.value = msg;
  showToast.value = true;
  window.setTimeout(() => { showToast.value = false; }, 3000);
};

const clampPercent = (value: number) => Math.max(0, Math.min(100, Math.round(value)));

const normalizePercent = (value: unknown, fallback: string) => {
  if (typeof value === 'string' && value.includes('%')) return value;
  const numericValue = Number(value);
  if (!Number.isFinite(numericValue)) return fallback;
  const percentValue = numericValue <= 1 ? numericValue * 100 : numericValue;
  return `${percentValue.toFixed(1)}%`;
};

const parsePercentNumber = (value: string) => {
  const numeric = Number(String(value).replace('%', ''));
  return Number.isFinite(numeric) ? numeric : 0;
};

const buildScoreDistribution = (scores: number[]): ScoreDistributionItem[] => {
  const ranges = [
    { range: '90-100分', test: (score: number) => score >= 90 },
    { range: '80-89分', test: (score: number) => score >= 80 && score < 90 },
    { range: '70-79分', test: (score: number) => score >= 70 && score < 80 },
    { range: '60-69分', test: (score: number) => score >= 60 && score < 70 },
    { range: '不及格', test: (score: number) => score < 60 },
  ];
  const maxCount = Math.max(...ranges.map((item) => scores.filter(item.test).length), 1);
  return ranges.map((item) => {
    const count = scores.filter(item.test).length;
    return { range: item.range, count, percent: Math.round((count / maxCount) * 100) };
  });
};

const splitTableLine = (line: string) => {
  if (line.includes('\t')) return line.split('\t');
  return line.split(/,(?=(?:(?:[^"]*"){2})*[^"]*$)/).map((cell) => cell.replace(/^"|"$/g, '').trim());
};

const isWrongAnswer = (value: string) => {
  const normalized = value.trim().toLowerCase();
  return ['0', '错', '错误', 'x', '×', 'false', 'f', 'no', 'n', '未得分'].includes(normalized);
};

const isCorrectAnswer = (value: string) => {
  const normalized = value.trim().toLowerCase();
  return ['1', '对', '正确', '√', 'true', 't', 'yes', 'y', '得分'].includes(normalized);
};

const analyzeStructuredScoreFile = async (file: File): Promise<ExamResultData | null> => {
  if (!/\.(csv|tsv|txt)$/i.test(file.name)) return null;
  const text = await file.text();
  const lines = text.split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
  if (lines.length < 2) return null;

  const headers = splitTableLine(lines[0]).map((item) => item.trim());
  const rows = lines.slice(1).map(splitTableLine).filter((row) => row.length >= 2);
  const nameIndex = headers.findIndex((h) => /姓名|学生|name/i.test(h));
  const scoreIndex = headers.findIndex((h) => /总分|得分|成绩|score/i.test(h));
  if (scoreIndex < 0) return null;

  const students = rows.map((row, index) => row[nameIndex] || `学生${index + 1}`);
  const scores = rows
    .map((row) => Number(row[scoreIndex]))
    .filter((score) => Number.isFinite(score));
  if (scores.length === 0) return null;

  const averageScore = Number((scores.reduce((sum, score) => sum + score, 0) / scores.length).toFixed(1));
  const passRate = `${((scores.filter((score) => score >= 60).length / scores.length) * 100).toFixed(1)}%`;
  const excellentRate = `${((scores.filter((score) => score >= 90).length / scores.length) * 100).toFixed(1)}%`;
  const highestScore = Math.max(...scores);
  const highestScorers = rows
    .filter((row) => Number(row[scoreIndex]) === highestScore)
    .map((row, index) => row[nameIndex] || `学生${index + 1}`)
    .join('、');

  const questionColumns = headers
    .map((header, index) => ({ header, index }))
    .filter(({ header, index }) => index !== nameIndex && index !== scoreIndex && /题|q\d+|question/i.test(header));

  const topErrors: TopErrorItem[] = questionColumns
    .map(({ header, index }) => {
      const wrongStudents = rows
        .filter((row) => isWrongAnswer(row[index] || '') || (!isCorrectAnswer(row[index] || '') && Number(row[index]) === 0))
        .map((row, rowIndex) => row[nameIndex] || students[rowIndex] || `学生${rowIndex + 1}`);
      const errorRate = rows.length ? (wrongStudents.length / rows.length) * 100 : 0;
      return {
        question: header,
        topic: `${header} 对应知识点需复盘`,
        errorRate: `${errorRate.toFixed(1)}%`,
        affectedStudents: wrongStudents.slice(0, 8),
        suggestion: errorRate >= 30 ? '建议列入下节课讲评，并推送同类变式题。' : '可作为课后订正检查项。',
      };
    })
    .filter((item) => parsePercentNumber(item.errorRate) > 0)
    .sort((a, b) => parsePercentNumber(b.errorRate) - parsePercentNumber(a.errorRate))
    .slice(0, 5);

  const mastery: KnowledgeMastery[] = (topErrors.length ? topErrors : DEFAULT_EXAM_RESULT.topErrors).slice(0, 4).map((item, index) => {
    const colors: KnowledgeMastery['color'][] = ['rose', 'amber', 'indigo', 'emerald'];
    return {
      name: item.topic,
      percent: clampPercent(100 - parsePercentNumber(item.errorRate)),
      color: colors[index] || 'indigo',
    };
  });

  return {
    reportTitle: `${file.name.replace(/\.[^.]+$/, '')} 学情分析报告`,
    sampleSize: rows.length,
    submittedCount: rows.length,
    questionCount: questionColumns.length || DEFAULT_EXAM_RESULT.questionCount,
    averageScore,
    passRate,
    excellentRate,
    highestScore,
    highestScorers,
    lowScoreCount: scores.filter((score) => score < 60).length,
    scoreDistribution: buildScoreDistribution(scores),
    knowledgeMastery: mastery.length ? mastery : DEFAULT_EXAM_RESULT.knowledgeMastery,
    topErrors: topErrors.length ? topErrors : DEFAULT_EXAM_RESULT.topErrors,
    aiSuggestion: `已从成绩单中识别 ${rows.length} 名学生成绩，班级平均分 ${averageScore}，及格率 ${passRate}，优秀率 ${excellentRate}。建议优先处理错误率最高的 ${topErrors[0]?.question || '关键题目'}，并对低于 60 分的 ${scores.filter((score) => score < 60).length} 名学生安排基础巩固任务。`,
    remediationPlan: [
      '先讲评错误率最高的 2 道题，要求学生写出错因标签。',
      '对 60 分以下学生推送基础概念和例题仿练。',
      '对 90 分以上学生推送综合应用题，保持拔高训练。',
    ],
  };
};

const inferModeFromFile = (file: File): AnalysisMode => {
  if (selectedMode.value !== 'auto') return selectedMode.value;
  if (/\.(csv|tsv|txt|xlsx)$/i.test(file.name)) return 'score_sheet';
  if (/答题卡|答题卷|涂卡|答题纸/.test(file.name)) return 'answer_card';
  return 'free_paper';
};

const normalizeParsedExamResult = (parsed: any, fallbackTitle: string): ExamResultData => ({
  reportTitle: String(parsed.reportTitle || parsed.title || fallbackTitle || DEFAULT_EXAM_RESULT.reportTitle),
  sampleSize: Number(parsed.sampleSize || parsed.studentCount || DEFAULT_EXAM_RESULT.sampleSize),
  submittedCount: Number(parsed.submittedCount || parsed.sampleSize || DEFAULT_EXAM_RESULT.submittedCount),
  questionCount: Number(parsed.questionCount || DEFAULT_EXAM_RESULT.questionCount),
  averageScore: Number(parsed.averageScore ?? DEFAULT_EXAM_RESULT.averageScore),
  passRate: normalizePercent(parsed.passRate, DEFAULT_EXAM_RESULT.passRate),
  excellentRate: normalizePercent(parsed.excellentRate, DEFAULT_EXAM_RESULT.excellentRate),
  highestScore: Number(parsed.highestScore ?? DEFAULT_EXAM_RESULT.highestScore),
  highestScorers: String(parsed.highestScorers || DEFAULT_EXAM_RESULT.highestScorers),
  lowScoreCount: Number(parsed.lowScoreCount ?? DEFAULT_EXAM_RESULT.lowScoreCount),
  scoreDistribution: Array.isArray(parsed.scoreDistribution) && parsed.scoreDistribution.length
    ? parsed.scoreDistribution.map((item: any) => ({
      range: String(item.range || item.label || ''),
      count: Number(item.count || 0),
      percent: Number(item.percent || 0),
    }))
    : DEFAULT_EXAM_RESULT.scoreDistribution,
  knowledgeMastery: Array.isArray(parsed.knowledgeMastery) && parsed.knowledgeMastery.length
    ? parsed.knowledgeMastery.map((item: any, index: number) => ({
      name: String(item.name || item.topic || `知识点${index + 1}`),
      percent: clampPercent(Number(item.percent ?? item.mastery ?? 0)),
      color: (['emerald', 'indigo', 'amber', 'rose'].includes(item.color) ? item.color : index === 0 ? 'rose' : index === 1 ? 'amber' : 'indigo') as KnowledgeMastery['color'],
    }))
    : DEFAULT_EXAM_RESULT.knowledgeMastery,
  topErrors: Array.isArray(parsed.topErrors) && parsed.topErrors.length
    ? parsed.topErrors.slice(0, 5).map((item: any, index: number) => ({
      question: String(item.question || item.title || `第${index + 1}题`),
      topic: String(item.topic || item.knowledge || item.knowledgePoint || '待识别知识点'),
      errorRate: normalizePercent(item.errorRate, '0.0%'),
      affectedStudents: Array.isArray(item.affectedStudents) ? item.affectedStudents.map(String).slice(0, 8) : [],
      suggestion: String(item.suggestion || item.strategy || '建议安排同类题讲评和二次订正。'),
    }))
    : DEFAULT_EXAM_RESULT.topErrors,
  aiSuggestion: String(parsed.aiSuggestion || parsed.summary || DEFAULT_EXAM_RESULT.aiSuggestion),
  remediationPlan: Array.isArray(parsed.remediationPlan) && parsed.remediationPlan.length
    ? parsed.remediationPlan.map(String).slice(0, 5)
    : DEFAULT_EXAM_RESULT.remediationPlan,
});

const updateGroupsFromErrors = (result: ExamResultData) => {
  smartGroups.value = result.topErrors.slice(0, 3).map((error, index) => {
    const students = error.affectedStudents?.length ? error.affectedStudents : DEFAULT_SMART_GROUPS[index]?.students || [];
    return {
      title: `${error.question} - 专项巩固组`,
      count: students.length,
      tags: `错误率 ${error.errorRate}`,
      students,
      focus: error.topic,
      action: error.suggestion || '推送同类变式练习并跟踪二次正确率。',
    };
  });
};

const runAiAnalysis = async (upload: StagedAttachmentRecord, fallbackTitle: string) => {
  const resp = await apiClient.post<string>('/api/avatar/generate', {
    session_id: `exam-analysis-${upload.temp_id}`,
    prompt: [
      `请基于学生答题卡/成绩单文件「${upload.original_name}」生成一份班级学情分析。`,
      '请直接返回 JSON，字段包含 reportTitle、sampleSize、submittedCount、questionCount、averageScore、passRate、excellentRate、highestScore、highestScorers、lowScoreCount、scoreDistribution、knowledgeMastery、topErrors、aiSuggestion、remediationPlan。',
      'topErrors 每项包含 question、topic、errorRate、affectedStudents、suggestion；knowledgeMastery 每项包含 name、percent、color。',
    ].join('\n'),
    generator_type: 'exam-analysis',
  });
  const text = typeof resp.data === 'string' ? resp.data : JSON.stringify(resp.data);
  const jsonMatch = text.match(/\{[\s\S]*\}/);
  if (!jsonMatch) {
    return { ...DEFAULT_EXAM_RESULT, reportTitle: fallbackTitle, aiSuggestion: text.slice(0, 500) };
  }
  return normalizeParsedExamResult(JSON.parse(jsonMatch[0]), fallbackTitle);
};

const runUnifiedExamAnalysis = async (file: File): Promise<ExamAnalyzeResponse> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('mode', selectedMode.value);
  const response = await apiClient.postForm<ExamAnalyzeResponse>('/api/v1/exam-analysis/analyze', formData);
  const payload = response.data;
  if (!payload || payload.status === 'failed' || !payload.result) {
    const reason = payload?.reviewItems?.[0]?.reason || '学情分析接口未返回有效结果';
    throw new Error(reason);
  }
  return payload;
};

const uploadAndAnalyze = async (file: File) => {
  selectedUploadName.value = file.name;
  viewState.value = 'analyzing';
  analysisSource.value = '正在分析';
  resolvedMode.value = inferModeFromFile(file);
  reviewItems.value = [];
  analysisStatus.value = 'completed';

  try {
    const payload = await runUnifiedExamAnalysis(file);
    resolvedMode.value = payload.mode;
    analysisStatus.value = payload.status;
    reviewItems.value = payload.reviewItems || [];
    examResult.value = normalizeParsedExamResult(payload.result, `${file.name} 学情分析报告`);
    analysisSource.value = `${modeLabels[payload.mode]}${payload.status === 'needs_review' ? ' · 待复核' : ' · 已完成'}`;
    updateGroupsFromErrors(examResult.value);
    viewState.value = 'result';
    showToastMessage(payload.status === 'needs_review' ? '已生成初步分析，请复核低置信度项' : '学情分析已生成');
  } catch (error) {
    const fallbackMode = inferModeFromFile(file);
    resolvedMode.value = fallbackMode;
    if (fallbackMode === 'score_sheet') {
      const localResult = await analyzeStructuredScoreFile(file);
      if (localResult) {
        examResult.value = localResult;
        reviewItems.value = [];
        analysisSource.value = '成绩单模式 · 本地统计';
        updateGroupsFromErrors(examResult.value);
        viewState.value = 'result';
        showToastMessage('后端暂不可用，已使用本地成绩单统计');
        return;
      }
    }
    showToastMessage(error instanceof Error ? error.message : '分析失败，已展示默认学情样例');
    examResult.value = { ...DEFAULT_EXAM_RESULT, reportTitle: `${file.name} 学情分析报告` };
    smartGroups.value = [...DEFAULT_SMART_GROUPS];
    reviewItems.value = [{
      question: '整份材料',
      reason: fallbackMode === 'free_paper' ? '原卷/作业直传需要 OCR 与老师复核' : '材料未完成自动解析',
      confidence: 0,
      suggestion: '请确认文件格式、后端服务和标准答案配置后重新分析。',
    }];
    analysisStatus.value = 'failed';
    analysisSource.value = `${modeLabels[fallbackMode]} · 默认样例`;
    viewState.value = 'result';
  }
};

const handleFileChange = async (event: Event) => {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  if (!file) return;
  await uploadAndAnalyze(file);
  input.value = '';
};

const handleFileDrop = async (event: DragEvent) => {
  const file = event.dataTransfer?.files?.[0];
  if (!file) return;
  await uploadAndAnalyze(file);
};

const triggerUploadSelect = () => {
  uploadInput.value?.click();
};

const resetUpload = () => {
  viewState.value = 'upload';
  selectedUploadName.value = '';
  analysisSource.value = '等待上传';
  reviewItems.value = [];
  analysisStatus.value = 'completed';
};

const distributePersonalized = async () => {
  isDistributing.value = true;
  try {
    await apiClient.post('/api/avatar/generate', {
      prompt: `基于以下错题与分组生成个性化练习：${JSON.stringify({ topErrors: examResult.value.topErrors, groups: smartGroups.value })}`,
      generator_type: 'personalized-exercise',
    });
    showPersonalizedModal.value = false;
    showToastMessage(`已为 ${examResult.value.sampleSize} 名学生生成分层练习`);
  } catch {
    showToastMessage('后端暂不可用，已在本页保留分组方案');
  } finally {
    isDistributing.value = false;
  }
};

const exportReport = () => {
  const result = examResult.value;
  const lines = [
    `# ${result.reportTitle}`,
    '',
    `- 数据来源：${analysisSource.value}`,
    `- 分析模式：${activeModeLabel.value}`,
    `- 提交情况：${result.submittedCount}/${result.sampleSize}`,
    `- 平均分：${result.averageScore}`,
    `- 及格率：${result.passRate}`,
    `- 优秀率：${result.excellentRate}`,
    `- 最高分：${result.highestScore}（${result.highestScorers}）`,
    '',
    '## 高频错题',
    ...result.topErrors.map((item, index) => `${index + 1}. ${item.question}：${item.topic}，错误率 ${item.errorRate}。${item.suggestion || ''}`),
    '',
    '## 教学建议',
    result.aiSuggestion,
    '',
    '## 补救计划',
    ...result.remediationPlan.map((item, index) => `${index + 1}. ${item}`),
    '',
    '## 复核项',
    ...(reviewItems.value.length
      ? reviewItems.value.map((item, index) => `${index + 1}. ${item.question}：${item.reason}，置信度 ${Math.round(item.confidence * 100)}%。${item.suggestion}`)
      : ['无']),
  ];
  const blob = new Blob([lines.join('\n')], { type: 'text/markdown;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${result.reportTitle}.md`;
  link.click();
  URL.revokeObjectURL(url);
  showToastMessage('报告已导出为 Markdown');
};
</script>

<template>
  <div class="max-w-6xl mx-auto space-y-8 pb-20">
    <section
      v-if="viewState === 'upload'"
      @click="triggerUploadSelect"
      @dragover.prevent
      @drop.prevent="handleFileDrop"
      class="bg-white p-16 rounded-[32px] border-2 border-dashed border-gray-200 text-center space-y-7 group hover:bg-indigo-50/30 transition-all cursor-pointer"
    >
      <input ref="uploadInput" type="file" class="hidden" accept=".csv,.tsv,.txt,.xlsx,.pdf,.docx,.png,.jpg,.jpeg,.webp" @change="handleFileChange" />
      <div class="w-20 h-20 bg-indigo-50 rounded-[24px] flex items-center justify-center text-indigo-600 mx-auto group-hover:scale-105 transition-transform shadow-inner">
        <UploadCloud class="w-10 h-10" />
      </div>
      <div class="space-y-3">
        <h2 class="text-3xl font-black text-gray-900">上传答题卡、成绩单或试卷照片</h2>
        <p class="text-gray-500 max-w-2xl mx-auto text-base leading-relaxed">
          支持成绩单、标准答题卡、原卷和作业直传。自动识别会根据文件类型选择处理方式，不确定项会进入复核。
        </p>
      </div>
      <div class="grid grid-cols-4 gap-3 max-w-4xl mx-auto">
        <button
          v-for="option in analysisModeOptions"
          :key="option.id"
          type="button"
          @click.stop="selectedMode = option.id"
          class="text-left rounded-2xl border p-4 transition-all bg-white"
          :class="selectedMode === option.id ? 'border-indigo-500 shadow-lg shadow-indigo-100 text-indigo-700' : 'border-gray-100 hover:border-indigo-200 text-gray-600'"
        >
          <component :is="option.icon" class="w-5 h-5 mb-3" />
          <div class="text-sm font-black">{{ option.label }}</div>
          <div class="text-[11px] text-gray-400 mt-1 leading-snug">{{ option.desc }}</div>
        </button>
      </div>
      <div class="flex items-center justify-center gap-4 pt-2">
        <button
          @click.stop="triggerUploadSelect"
          class="bg-indigo-600 text-white px-8 py-4 rounded-2xl font-black text-base shadow-xl shadow-indigo-100 hover:bg-indigo-700 transition-colors"
        >
          选择文件
        </button>
        <span class="text-gray-400 font-bold text-sm">或拖拽文件至此处</span>
      </div>
    </section>

    <UploadLoader
      v-else-if="viewState === 'analyzing'"
      message="织课 AI 正在生成学情分析"
      :sub-message="selectedUploadName ? `正在处理 ${selectedUploadName}` : '正在进行成绩统计与错因诊断'"
    />

    <div v-else class="space-y-8">
      <div class="flex flex-wrap items-center justify-between gap-4">
        <div>
          <div class="flex flex-wrap items-center gap-3 mb-2">
            <h2 class="text-2xl font-black text-gray-900">{{ examResult.reportTitle }}</h2>
            <span class="px-2.5 py-1 rounded-lg bg-emerald-50 text-emerald-700 text-xs font-black">{{ analysisSource }}</span>
            <span
              v-if="needsReview"
              class="px-2.5 py-1 rounded-lg bg-amber-50 text-amber-700 text-xs font-black"
            >
              {{ reviewItems.length }} 项待复核
            </span>
          </div>
          <p class="text-sm text-gray-500">
            {{ activeModeLabel }} · {{ completionText }} · 共 {{ examResult.questionCount }} 题 · 低分预警 {{ examResult.lowScoreCount }} 人
          </p>
        </div>
        <div class="flex items-center gap-3">
          <button
            @click="resetUpload"
            class="flex items-center gap-2 px-5 py-2.5 bg-gray-100 hover:bg-gray-200 rounded-xl text-sm font-bold text-gray-600 transition-colors"
          >
            <RotateCcw class="w-4 h-4" />
            重新上传
          </button>
          <button
            @click="exportReport"
            class="flex items-center gap-2 px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 rounded-xl text-sm font-bold text-white shadow-lg shadow-indigo-100 transition-all"
          >
            <Download class="w-4 h-4" />
            导出报告
          </button>
        </div>
      </div>

      <div v-if="needsReview" class="bg-amber-50 border border-amber-100 rounded-2xl p-6">
        <div class="flex items-start justify-between gap-4 mb-4">
          <div>
            <h3 class="text-base font-black text-amber-900">需要老师复核的识别结果</h3>
            <p class="text-xs text-amber-700/80 mt-1">答题卡和原卷作业不会强行全自动发布，低置信度内容会保留给老师确认。</p>
          </div>
          <span class="text-xs font-black text-amber-700 bg-white/70 px-3 py-1 rounded-lg">{{ reviewItems.length }} 项</span>
        </div>
        <div class="grid grid-cols-3 gap-3">
          <div
            v-for="item in reviewItems"
            :key="`${item.question}-${item.reason}`"
            class="rounded-xl bg-white/75 border border-amber-100 p-4"
          >
            <div class="flex items-center justify-between gap-3">
              <h4 class="text-sm font-black text-gray-900">{{ item.question }}</h4>
              <span class="text-xs font-black text-amber-600">{{ Math.round(item.confidence * 100) }}%</span>
            </div>
            <p class="text-xs text-gray-600 mt-2 leading-relaxed">{{ item.reason }}</p>
            <p class="text-xs text-amber-700 mt-2 leading-relaxed">{{ item.suggestion }}</p>
          </div>
        </div>
      </div>

      <StatsCards
        :average-score="examResult.averageScore"
        :pass-rate="examResult.passRate"
        :excellent-rate="examResult.excellentRate"
        :highest-score="examResult.highestScore"
        :highest-scorers="examResult.highestScorers"
        :sample-size="examResult.sampleSize"
        :low-score-count="examResult.lowScoreCount"
      />

      <div class="grid grid-cols-3 gap-6">
        <ClassScoreChart
          :average-score="examResult.averageScore"
          :pass-rate="examResult.passRate"
          :highest-score="examResult.highestScore"
          :highest-scorers="examResult.highestScorers"
          :score-distribution="examResult.scoreDistribution"
          :knowledge-mastery="examResult.knowledgeMastery"
          :sample-size="examResult.sampleSize"
        />
        <TopErrorsList
          :top-errors="examResult.topErrors"
          @generate-personalized="showPersonalizedModal = true"
        />
      </div>

      <div class="grid grid-cols-3 gap-6">
        <div class="col-span-2 bg-white p-7 rounded-2xl border border-gray-100 shadow-sm">
          <div class="flex items-center gap-3 mb-5">
            <div class="w-10 h-10 bg-indigo-600 rounded-2xl flex items-center justify-center text-white shadow-lg shadow-indigo-100">
              <Sparkles class="w-5 h-5" />
            </div>
            <div>
              <h3 class="text-lg font-black text-gray-900">AI 助教诊断与讲评建议</h3>
              <p class="text-xs text-gray-400">面向下一节课的可执行教学动作</p>
            </div>
          </div>
          <div v-if="examResult.aiSuggestion" class="rendered-markdown rendered-analysis-markdown text-gray-700 leading-relaxed text-sm min-w-0" v-html="renderMarkdown(examResult.aiSuggestion)"></div>
          <p v-else class="text-gray-500 text-sm">上传试卷后，AI 助教将自动生成针对性教学建议。</p>
        </div>

        <div class="bg-white p-7 rounded-2xl border border-gray-100 shadow-sm">
          <div class="flex items-center gap-2 mb-5">
            <FileSpreadsheet class="w-5 h-5 text-indigo-500" />
            <h3 class="text-lg font-black text-gray-900">补救计划</h3>
          </div>
          <div class="space-y-3">
            <div
              v-for="(item, index) in examResult.remediationPlan"
              :key="item"
              class="flex gap-3 rounded-xl bg-gray-50 p-3"
            >
              <span class="w-6 h-6 rounded-lg bg-white text-indigo-600 text-xs font-black flex items-center justify-center flex-shrink-0">{{ index + 1 }}</span>
              <p class="text-xs leading-relaxed text-gray-600 font-medium">{{ item }}</p>
            </div>
          </div>
        </div>
      </div>

      <div v-if="hasResult" class="bg-white p-7 rounded-2xl border border-gray-100 shadow-sm">
        <div class="flex items-center justify-between mb-5">
          <div>
            <h3 class="text-lg font-black text-gray-900">分层干预分组</h3>
            <p class="text-xs text-gray-400 mt-1">根据错题率和影响学生自动生成</p>
          </div>
          <button
            @click="showPersonalizedModal = true"
            class="px-4 py-2 rounded-xl bg-blue-50 text-blue-600 text-sm font-bold hover:bg-blue-100 transition-colors"
          >
            生成个性化练习
          </button>
        </div>
        <div class="grid grid-cols-3 gap-4">
          <div v-for="group in smartGroups" :key="group.title" class="rounded-2xl border border-gray-100 p-4 bg-gray-50/60">
            <div class="flex items-start justify-between gap-3">
              <h4 class="text-sm font-black text-gray-900 leading-snug">{{ group.title }}</h4>
              <span class="text-xs font-black text-indigo-600 whitespace-nowrap">{{ group.count }}人</span>
            </div>
            <p class="text-xs text-gray-500 mt-3 leading-relaxed">{{ group.focus }}</p>
            <div class="flex flex-wrap gap-1.5 mt-4">
              <span v-for="student in group.students.slice(0, 6)" :key="student" class="px-2 py-1 rounded-lg bg-white text-[10px] font-bold text-gray-500 border border-gray-100">
                {{ student }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <Transition
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="opacity-0 scale-95"
      enter-to-class="opacity-100 scale-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="opacity-100 scale-100"
      leave-to-class="opacity-0 scale-95"
    >
      <PersonalizedModal
        v-if="showPersonalizedModal"
        :smart-groups="smartGroups"
        :is-distributing="isDistributing"
        @close="showPersonalizedModal = false"
        @confirm="distributePersonalized"
      />
    </Transition>

    <Transition name="fade">
      <Toast v-if="showToast" :message="toastMessage" />
    </Transition>
  </div>
</template>
