<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { api } from '../api/client';
import PageHeader from '../components/PageHeader.vue';
import DataCard from '../components/DataCard.vue';
import StatusBadge from '../components/StatusBadge.vue';

interface ProfileDimension {
  name: string;
  value: string;
}

interface ProfileDialogResult {
  studentName: string;
  courseName: string;
  summary: string;
  dimensions: ProfileDimension[];
  weakKnowledgePoints: string[];
  recommendedStrategy: string;
  mode: string;
}

interface ResourceItem {
  resourceType: string;
  title: string;
  content: string;
  reason: string;
  relatedKnowledgePoints: string[];
  difficulty: string;
  estimatedMinutes: number;
}

interface ResourcePackResult {
  packageTitle: string;
  courseName: string;
  weakPoints: string[];
  resourceCount: number;
  resources: ResourceItem[];
  mode: string;
}

interface RagCitation {
  sourceFile: string;
  chapter: string;
  section: string;
  snippet: string;
}

interface RagResult {
  answer: string;
  citations: RagCitation[];
  matchedChunks: Array<RagCitation & { score: number; knowledgePoints: string[] }>;
  confidence: number;
  recommendedExercises: string[];
  relatedKnowledgePoints: string[];
}

const demoAnswer = ref('我叫张三，最近 Python 文件处理和数据结构递归题比较吃力，平时每天大概有 30 分钟学习时间，更喜欢代码案例、分步骤讲义和少量练习题。');
const ragQuestion = ref('递归题总是写不出来，应该怎么分析？');
const loadingProfile = ref(false);
const loadingPack = ref(false);
const loadingRag = ref(false);
const loadingReview = ref(false);
const error = ref('');

const fallbackProfile: ProfileDialogResult = {
  studentName: '张三',
  courseName: 'Python 程序设计',
  summary: '张三当前画像已生成，建议先围绕 Python 文件读写与递归分析进行补强。',
  weakKnowledgePoints: ['Python 文件读写与异常处理', '递归边界与复杂度分析', '代码调试与边界条件'],
  recommendedStrategy: '先讲义补概念，再练习题巩固，最后用实验任务完成迁移应用',
  mode: 'local-fallback',
  dimensions: [
    { name: '学习目标', value: '补齐 Python 文件处理、递归分析和综合应用能力' },
    { name: '基础水平', value: '中等基础' },
    { name: '薄弱知识点', value: 'Python 文件读写与异常处理、递归边界与复杂度分析、代码调试与边界条件' },
    { name: '学习偏好', value: '偏好项目实践、代码案例和可操作任务' },
    { name: '时间安排', value: '每天 30 分钟专项练习，周末 1 次综合复盘' },
    { name: '学习风险', value: '中等风险：薄弱点集中，需要连续两周跟踪任务完成率' },
    { name: '推荐策略', value: '先讲义补概念，再练习题巩固，最后用实验任务完成迁移应用' }
  ]
};

const fallbackPack: ResourcePackResult = {
  packageTitle: 'Python 程序设计个性化资源包',
  courseName: 'Python 程序设计',
  weakPoints: fallbackProfile.weakKnowledgePoints,
  resourceCount: 5,
  mode: 'local-fallback',
  resources: [
    {
      resourceType: '个性化讲义',
      title: 'Python 文件处理分步讲义',
      content: '解释 with open、读写模式、异常处理和常见边界问题，并附 5 分钟自检清单。',
      reason: '先补齐概念和步骤，降低直接写代码的挫败感。',
      relatedKnowledgePoints: ['文件读写', '异常处理'],
      difficulty: '基础',
      estimatedMinutes: 18
    },
    {
      resourceType: '练习题',
      title: '文件处理与递归分层练习 8 题',
      content: '包含基础题、变式题和综合题，每题提供提示、标准答案和错因标签。',
      reason: '通过分层练习检查是否真正掌握薄弱知识点。',
      relatedKnowledgePoints: ['文件读写', '递归边界'],
      difficulty: '中等',
      estimatedMinutes: 25
    },
    {
      resourceType: '代码案例或实验任务',
      title: '学生成绩文件分析小实验',
      content: '读取 CSV 成绩文件，统计平均分和低分名单，并处理文件不存在、空文件等异常。',
      reason: '把知识点迁移到可展示的实践任务。',
      relatedKnowledgePoints: ['文件读写', '列表处理', '异常处理'],
      difficulty: '进阶',
      estimatedMinutes: 35
    },
    {
      resourceType: '思维导图文本',
      title: '递归分析思维导图',
      content: '中心主题：递归。一级节点：终止条件、状态转移、调用栈、复杂度、典型错误。',
      reason: '帮助学生建立结构化认知，便于复盘。',
      relatedKnowledgePoints: ['递归', '调用栈'],
      difficulty: '基础',
      estimatedMinutes: 12
    },
    {
      resourceType: '视频脚本或项目任务书',
      title: '8 分钟文件处理讲解脚本',
      content: '问题引入、核心概念、代码演示、课后任务四段式脚本，并附提交物和评分点。',
      reason: '可直接用于教师端资源生成展示，也便于学生端按步骤完成任务。',
      relatedKnowledgePoints: ['文件处理', '异常分支'],
      difficulty: '中等',
      estimatedMinutes: 20
    }
  ]
};

const profile = ref<ProfileDialogResult>(fallbackProfile);
const resourcePack = ref<ResourcePackResult>(fallbackPack);
const selectedType = ref(fallbackPack.resources[0].resourceType);
const ragResult = ref<RagResult>({
  answer: '根据《Python 程序设计》递归基础资料，建议先写递归出口，再写规模缩小的递推关系。做题时先画调用树，确认每次调用都接近最小规模问题。',
  citations: [
    {
      sourceFile: 'python_ch02_recursion.md',
      chapter: '第 2 章 函数与模块化',
      section: '递归基础',
      snippet: '递归函数必须包含递归出口和规模缩小的递推关系。'
    }
  ],
  matchedChunks: [],
  confidence: 0.86,
  recommendedExercises: ['用递归实现阶乘函数。', '画出 Fibonacci(5) 的递归调用树并说明重复计算。'],
  relatedKnowledgePoints: ['递归', '递归出口', '调用栈']
});
const reviewResult = ref({
  riskLevel: 'low',
  confidence: 0.9,
  citationCoverage: 0.8,
  hallucinationWarning: '',
  reviewStatus: 'pass',
  suggestions: ['内容引用充分，表达相对稳健，可用于演示。']
});

const selectedResource = computed(() => resourcePack.value.resources.find((item) => item.resourceType === selectedType.value) || resourcePack.value.resources[0]);

async function runProfileDialog() {
  loadingProfile.value = true;
  error.value = '';
  try {
    profile.value = await api.post<ProfileDialogResult>('/api/v1/profile-dialog/run', {
      studentId: 'demo-student-zhangsan',
      studentName: '张三',
      courseId: 'demo-course-python',
      courseName: 'Python 程序设计',
      answer: demoAnswer.value
    });
    selectedType.value = resourcePack.value.resources[0]?.resourceType || '个性化讲义';
  } catch (err) {
    error.value = err instanceof Error ? `后端画像接口暂不可用，已使用本地演示数据：${err.message}` : '后端画像接口暂不可用，已使用本地演示数据。';
    profile.value = fallbackProfile;
  } finally {
    loadingProfile.value = false;
  }
}

async function generateResourcePack() {
  loadingPack.value = true;
  error.value = '';
  try {
    resourcePack.value = await api.post<ResourcePackResult>('/api/v1/resources/generate-pack', {
      studentId: 'demo-student-zhangsan',
      courseId: 'demo-course-python',
      courseName: profile.value.courseName,
      weakPoints: profile.value.weakKnowledgePoints
    });
    selectedType.value = resourcePack.value.resources[0]?.resourceType || '个性化讲义';
  } catch (err) {
    error.value = err instanceof Error ? `后端资源生成接口暂不可用，已使用本地演示数据：${err.message}` : '后端资源生成接口暂不可用，已使用本地演示数据。';
    resourcePack.value = fallbackPack;
  } finally {
    loadingPack.value = false;
  }
}

async function askRag() {
  loadingRag.value = true;
  error.value = '';
  try {
    ragResult.value = await api.post<RagResult>('/api/v1/rag/ask', {
      question: ragQuestion.value,
      courseId: 'python-programming',
      studentId: 'demo-student-zhangsan'
    });
  } catch (err) {
    error.value = err instanceof Error ? `RAG 接口暂不可用，已使用本地演示回答：${err.message}` : 'RAG 接口暂不可用，已使用本地演示回答。';
  } finally {
    loadingRag.value = false;
  }
}

async function reviewAnswer() {
  loadingReview.value = true;
  error.value = '';
  try {
    reviewResult.value = await api.post<typeof reviewResult.value>('/api/v1/content-review/check', {
      courseId: 'python-programming',
      content: ragResult.value.answer,
      citations: ragResult.value.citations
    });
  } catch (err) {
    error.value = err instanceof Error ? `内容审核接口暂不可用，已保留本地审核结果：${err.message}` : '内容审核接口暂不可用，已保留本地审核结果。';
  } finally {
    loadingReview.value = false;
  }
}

async function runFullDemo() {
  await runProfileDialog();
  await generateResourcePack();
  await askRag();
  await reviewAnswer();
}

onMounted(runFullDemo);
</script>

<template>
  <section class="page assistant-page">
    <PageHeader title="智能答疑与画像生成" description="通过自然语言对话生成学习画像，并基于薄弱点生成 5 类个性化资源包。">
      <template #actions>
        <StatusBadge label="规则生成演示" tone="success" />
      </template>
    </PageHeader>

    <p v-if="error" class="panel warning-text">{{ error }}</p>

    <div class="assistant-layout">
      <DataCard title="对话式学习画像" subtitle="输入学生自然语言回答，生成目标、基础、薄弱点、偏好、时间、风险和策略。">
        <textarea v-model="demoAnswer" class="dialog-input" rows="5" />
        <div class="assistant-actions">
          <button @click="runProfileDialog" :disabled="loadingProfile">{{ loadingProfile ? '生成中...' : '生成画像' }}</button>
          <button class="secondary" @click="generateResourcePack" :disabled="loadingPack">{{ loadingPack ? '生成中...' : '生成资源包' }}</button>
        </div>
        <div class="profile-summary">
          <strong>{{ profile.summary }}</strong>
          <StatusBadge :label="profile.mode" tone="info" />
        </div>
        <div class="dimension-grid">
          <article v-for="item in profile.dimensions" :key="item.name" class="dimension-card">
            <span>{{ item.name }}</span>
            <p>{{ item.value }}</p>
          </article>
        </div>
      </DataCard>

      <aside class="assistant-side">
        <DataCard title="薄弱知识点" subtitle="资源生成将围绕这些知识点展开">
          <div class="tag-list">
            <StatusBadge v-for="item in profile.weakKnowledgePoints" :key="item" :label="item" tone="purple" />
          </div>
        </DataCard>

        <DataCard title="推荐策略" subtitle="从画像到资源包的规则链路">
          <p class="strategy-copy">{{ profile.recommendedStrategy }}</p>
        </DataCard>
      </aside>
    </div>

    <DataCard title="RAG 引用问答" subtitle="轻量关键词检索课程知识库，返回回答、引用来源、可信度和推荐练习。">
      <template #action>
        <StatusBadge :label="`可信度 ${(ragResult.confidence * 100).toFixed(0)}%`" tone="success" />
      </template>
      <div class="rag-question-row">
        <input v-model="ragQuestion" placeholder="输入课程问题，例如：递归题怎么分析？" />
        <button @click="askRag" :disabled="loadingRag">{{ loadingRag ? '检索中...' : 'RAG 提问' }}</button>
        <button class="secondary" @click="reviewAnswer" :disabled="loadingReview">{{ loadingReview ? '审核中...' : '防幻觉审核' }}</button>
      </div>
      <article class="rag-answer">
        <h3>回答</h3>
        <p>{{ ragResult.answer }}</p>
      </article>
      <div class="rag-grid">
        <article class="citation-card" v-for="item in ragResult.citations" :key="`${item.sourceFile}-${item.section}`">
          <StatusBadge :label="item.sourceFile" tone="info" />
          <strong>{{ item.chapter }} · {{ item.section }}</strong>
          <p>{{ item.snippet }}</p>
        </article>
      </div>
      <div class="exercise-list">
        <strong>推荐练习</strong>
        <span v-for="item in ragResult.recommendedExercises" :key="item">{{ item }}</span>
      </div>
      <div class="review-strip">
        <StatusBadge :label="`审核：${reviewResult.reviewStatus}`" :tone="reviewResult.riskLevel === 'high' ? 'danger' : reviewResult.riskLevel === 'medium' ? 'warning' : 'success'" />
        <span>风险 {{ reviewResult.riskLevel }} · 引用覆盖 {{ (reviewResult.citationCoverage * 100).toFixed(0) }}% · 审核可信度 {{ (reviewResult.confidence * 100).toFixed(0) }}%</span>
        <span v-if="reviewResult.hallucinationWarning">{{ reviewResult.hallucinationWarning }}</span>
      </div>
    </DataCard>

    <DataCard :title="resourcePack.packageTitle" subtitle="至少 5 类资源：讲义、练习题、代码案例/实验、思维导图、视频脚本/项目任务书。">
      <template #action>
        <StatusBadge :label="`${resourcePack.resourceCount} 类资源`" tone="success" />
      </template>
      <div class="resource-type-tabs">
        <button
          v-for="item in resourcePack.resources"
          :key="item.resourceType"
          :class="['secondary', { active: selectedType === item.resourceType }]"
          @click="selectedType = item.resourceType"
        >
          {{ item.resourceType }}
        </button>
      </div>

      <article v-if="selectedResource" class="resource-detail">
        <div class="resource-head">
          <div>
            <span class="eyebrow">{{ selectedResource.resourceType }}</span>
            <h3>{{ selectedResource.title }}</h3>
          </div>
          <StatusBadge :label="selectedResource.difficulty" tone="info" />
        </div>
        <p>{{ selectedResource.content }}</p>
        <div class="resource-meta">
          <span>预计 {{ selectedResource.estimatedMinutes }} 分钟</span>
          <span>{{ selectedResource.reason }}</span>
          <span>可信度 {{ (ragResult.confidence * 100).toFixed(0) }}%</span>
        </div>
        <div class="tag-list">
          <StatusBadge v-for="point in selectedResource.relatedKnowledgePoints" :key="point" :label="point" tone="neutral" />
        </div>
      </article>
    </DataCard>
  </section>
</template>

<style scoped>
.assistant-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 16px;
}

.assistant-side,
.dimension-grid,
.tag-list {
  display: grid;
  gap: 12px;
}

.dialog-input {
  width: 100%;
  box-sizing: border-box;
  resize: vertical;
  border: 1px solid var(--border-light);
  border-radius: 14px;
  padding: 14px;
  color: var(--text-main);
  background: #fff;
  line-height: 1.7;
}

.assistant-actions,
.resource-type-tabs,
.resource-meta,
.rag-question-row,
.review-strip {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 14px;
}

.profile-summary {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin: 16px 0;
  border-radius: 14px;
  padding: 14px;
  background: var(--color-primary-light);
}

.dimension-grid {
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}

.dimension-card {
  border: 1px solid var(--border-light);
  border-radius: 14px;
  padding: 14px;
  background: #fbfdff;
}

.dimension-card span,
.eyebrow {
  color: var(--color-primary-dark);
  font-size: 12px;
  font-weight: 800;
}

.dimension-card p,
.strategy-copy,
.resource-detail p {
  margin: 8px 0 0;
  color: var(--text-secondary);
  line-height: 1.7;
}

.resource-type-tabs .active {
  color: var(--text-light);
  background: linear-gradient(135deg, var(--color-primary-dark), var(--color-purple));
}

.resource-detail {
  margin-top: 16px;
  border: 1px solid var(--border-light);
  border-radius: 16px;
  padding: 16px;
  background: #fbfdff;
}

.rag-question-row {
  align-items: center;
}

.rag-question-row input {
  flex: 1 1 280px;
}

.rag-answer,
.citation-card {
  border: 1px solid var(--border-light);
  border-radius: 16px;
  padding: 16px;
  background: #fbfdff;
}

.rag-answer {
  margin-top: 16px;
}

.rag-answer h3 {
  margin: 0 0 8px;
}

.rag-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 12px;
  margin-top: 14px;
}

.citation-card {
  display: grid;
  gap: 8px;
}

.citation-card p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.65;
}

.exercise-list {
  display: grid;
  gap: 8px;
  margin-top: 14px;
  color: var(--text-secondary);
}

.exercise-list span {
  border-radius: 12px;
  padding: 10px 12px;
  background: var(--status-neutral-bg);
}

.review-strip {
  align-items: center;
  border-radius: 14px;
  padding: 12px;
  color: var(--text-secondary);
  background: var(--color-primary-light);
}

.resource-head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.resource-head h3 {
  margin: 4px 0 0;
  color: var(--text-main);
}

.resource-meta span {
  border-radius: 999px;
  padding: 6px 10px;
  color: var(--text-secondary);
  background: var(--status-neutral-bg);
  font-size: 12px;
  font-weight: 700;
}

@media (max-width: 1180px) {
  .assistant-layout {
    grid-template-columns: 1fr;
  }
}
</style>
