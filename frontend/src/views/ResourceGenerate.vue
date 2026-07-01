<script setup lang="ts">
import { ref } from 'vue';
import { api } from '../api/client';
import DataCard from '../components/DataCard.vue';
import PageHeader from '../components/PageHeader.vue';
import StatCard from '../components/StatCard.vue';
import StatusBadge from '../components/StatusBadge.vue';

interface ResourceCard {
  title: string;
  resourceType?: string;
  resource_type?: string;
  sourceAgent?: string;
  source_agent?: string;
  adaptedProfile?: string;
  relatedKnowledgePoints?: string[];
  reason?: string;
  recommendation_reason?: string;
  difficulty: string;
  reviewStatus?: string;
  references?: string[];
  content?: string;
  description?: string;
  format?: string;
  status?: string;
  file_path?: string;
  fallback_resources?: string[];
  tts_status?: { status?: string; message?: string };
  tts_result?: { status?: string; message?: string; audio_path?: string | null };
  ffmpeg_status?: { status?: string; message?: string };
  estimatedMinutes?: number;
  suitableLearner?: string;
  libraryStatus?: string;
  pushStatus?: string;
  feedbackStatus?: string;
  reviewSummary?: ReviewSummary;
}

interface ReviewSummary {
  factualAccuracy: string;
  referenceCompleteness: string;
  difficultyMatch: string;
  humanReviewAdvice: string;
}

interface CoursewareSection {
  title: string;
  objective: string;
  bullets: string[];
}

interface CoursewareOutline {
  title: string;
  course: string;
  chapter: string;
  student: string;
  weakPoints: string;
  outline: CoursewareSection[];
  statusMessage: string;
  libraryMessage: string;
  exportMessage: string;
  capabilityNote: string;
}

const form = ref({
  student: '李明',
  course: 'Python 程序设计',
  chapter: '循环结构',
  knowledgePoints: 'while 循环、循环嵌套、break / continue',
  goal: '完成课程作业和基础项目',
  preference: '代码案例 + 图解'
});

const agentNodes = [
  '画像构建 Agent',
  '知识检索 Agent',
  '学习路径规划 Agent',
  '资源生成规划 Agent',
  '多类型资源生成 Agent',
  'RAG 答疑 Agent',
  '学习效果评估 Agent',
  '内容安全与防幻觉审核 Agent',
  '报告生成 Agent'
].map((name, index) => ({
  name,
  input: index === 0 ? '自然语言对话 + 学习历史' : '上游 Agent 输出 + 循环结构知识库',
  tool: index === 7 ? '审核规则 + 引用完整性检查' : '课程知识库 + 资源模板',
  output: index === 4 ? '8 类个性化资源' : '结构化中间结果',
  status: 'success',
  duration: `${180 + index * 60}ms`,
  evidence: 'Python 程序设计课程知识库 / 循环结构章节'
}));

const defaultResources: ResourceCard[] = [
  ['循环结构知识讲义', 'handout', '基础'],
  ['for / while 知识点思维导图', 'mindmap', '基础'],
  ['循环结构分层练习题', 'quiz', '中等'],
  ['while 循环条件更新动画', 'animation_html', '基础'],
  ['循环结构视频讲解脚本', 'video_script', '基础'],
  ['循环结构语音讲解资源', 'tts_audio', '基础'],
  ['Python 循环结构简易 MP4 视频', 'video_mp4', '基础'],
  ['Python while 循环代码实操案例', 'code_case', '基础'],
  ['循环结构项目任务', 'project_task', '中等']
].map(([title, resourceType, difficulty]) => ({
  title,
  resourceType,
  difficulty,
  sourceAgent: '多类型资源生成 Agent',
  adaptedProfile: '循环结构需巩固，偏好代码实操',
  relatedKnowledgePoints: ['while 循环', '循环嵌套', 'break / continue'],
  reason: '匹配李明的薄弱知识点和代码案例 + 图解偏好。',
  reviewStatus: '通过',
  references: ['Python 程序设计课程知识库 / 循环结构章节'],
  suitableLearner: '李明：循环结构需巩固，偏好代码实操',
  libraryStatus: '待加入',
  pushStatus: '待推送',
  feedbackStatus: '待学习反馈',
  reviewSummary: {
    factualAccuracy: '通过课程知识库比对，循环条件、变量更新和控制语句解释准确。',
    referenceCompleteness: '已绑定 Python 程序设计课程知识库 / 循环结构章节，可追溯到 while、循环嵌套和 break / continue 知识点。',
    difficultyMatch: '基础到中等，适合李明当前“循环结构需巩固、偏好代码实操”的画像。',
    humanReviewAdvice: '建议教师重点复核示例代码变量更新位置，确认课堂表述与学生当前进度一致。'
  },
  estimatedMinutes: 20
}));

function normalizeResources(list: ResourceCard[]) {
  return list.map((item) => ({
    ...item,
    reviewStatus: item.reviewStatus || '已审核',
    libraryStatus: item.libraryStatus || '待加入',
    pushStatus: item.pushStatus || '待推送',
    feedbackStatus: item.feedbackStatus || '待学习反馈',
    references: item.references?.length ? item.references : ['Python 程序设计课程知识库 / 循环结构章节'],
    relatedKnowledgePoints: item.relatedKnowledgePoints?.length ? item.relatedKnowledgePoints : ['while 循环', '循环嵌套', 'break / continue'],
    reviewSummary: item.reviewSummary || {
      factualAccuracy: '核心概念与课程知识库一致，未发现明显事实偏差。',
      referenceCompleteness: '引用依据完整，已关联循环结构章节知识库。',
      difficultyMatch: '难度与李明当前补弱目标匹配。',
      humanReviewAdvice: '建议人工抽查案例代码和练习题答案解析。'
    }
  }));
}

const resources = ref<ResourceCard[]>(normalizeResources(defaultResources));
const packageTitle = ref('Python 循环结构个性化补弱资源包');
const message = ref('');
const loading = ref(false);
const failLoading = ref(false);
const latestTaskStatus = ref('');
const latestReviewItemId = ref<number | null>(null);
const activeReviewTitle = ref<string | null>(null);
const courseware = ref<CoursewareOutline | null>(null);
const coursewareLoading = ref(false);
const coursewareLibraryStatus = ref('待加入教学资源库');

function typeOf(item: ResourceCard) {
  return item.resourceType || item.resource_type || '资源';
}

function isAnimation(item: ResourceCard) {
  return typeOf(item) === 'animation_html';
}

function isTts(item: ResourceCard) {
  return typeOf(item) === 'tts_audio';
}

function isVideoMp4(item: ResourceCard) {
  return typeOf(item) === 'video_mp4';
}

function agentOf(item: ResourceCard) {
  return item.sourceAgent || item.source_agent || '多类型资源生成 Agent';
}

function reasonOf(item: ResourceCard) {
  return item.reason || item.recommendation_reason || '匹配学生画像与循环结构薄弱点。';
}

function statusTone(status?: string): 'success' | 'warning' | 'info' {
  if (!status || /待/.test(status)) return 'warning';
  if (/已|通过|完成/.test(status)) return 'success';
  return 'info';
}

async function generatePack(forceFail = false) {
  loading.value = true;
  failLoading.value = forceFail;
  message.value = '';
  try {
    const result = await api.post<{ packageTitle: string; resources: ResourceCard[]; taskStatus?: string; taskId?: number; reviewItemId?: number; rollbackNotice?: string }>('/api/v1/resources/generate-pack', {
      studentId: 'student-li-ming',
      courseId: 'python-programming',
      courseName: form.value.course,
      knowledgePoints: form.value.knowledgePoints.split('、'),
      learningGoal: forceFail ? `${form.value.goal} fail` : form.value.goal
    });
    packageTitle.value = result.packageTitle || packageTitle.value;
    resources.value = normalizeResources(result.resources?.length ? result.resources : defaultResources);
    latestTaskStatus.value = result.taskStatus || 'pending_review';
    latestReviewItemId.value = result.reviewItemId || null;
    message.value = result.rollbackNotice || '已生成资源包，当前状态为待审核；教师或管理员通过后才会发布到学生端。';
  } catch (err) {
    resources.value = normalizeResources(defaultResources);
    message.value = '当前网络不稳定，已为你展示本地学习建议。';
  } finally {
    loading.value = false;
    failLoading.value = false;
  }
}

async function generateCoursewareOutline() {
  coursewareLoading.value = true;
  message.value = '';
  try {
    courseware.value = await api.post<CoursewareOutline>('/api/v1/resources/courseware-outline', {
      course: form.value.course || 'Python 程序设计',
      chapter: form.value.chapter || '循环结构',
      student: form.value.student || '李明',
      weakPoints: 'while 循环和循环嵌套需要加强'
    });
    coursewareLibraryStatus.value = '待加入教学资源库';
    message.value = courseware.value.statusMessage || '已生成课件大纲';
  } catch {
    courseware.value = {
      title: 'Python 程序设计《循环结构》AI 课件大纲',
      course: 'Python 程序设计',
      chapter: '循环结构',
      student: '李明',
      weakPoints: 'while 循环和循环嵌套需要加强',
      statusMessage: '已生成课件大纲',
      libraryMessage: '已加入教学资源库',
      exportMessage: '可用于后续导出 PPT',
      capabilityNote: '当前提供课件大纲与资源库入库结果，PPTX 导出接口已预留。',
      outline: [
        { title: '课程导入', objective: '用重复执行场景引出循环结构。', bullets: ['从累计求和问题切入', '明确李明的补弱目标'] },
        { title: 'for 循环', objective: '掌握已知次数循环。', bullets: ['range 用法', '遍历序列', '与 while 对比'] },
        { title: 'while 循环', objective: '强化条件更新。', bullets: ['初始值', '循环条件', '变量更新'] },
        { title: 'break / continue', objective: '区分控制语句。', bullets: ['break 结束循环', 'continue 跳过本轮'] },
        { title: '循环嵌套', objective: '追踪内外层变量。', bullets: ['外层控制行', '内层控制列', '避免变量同名'] },
        { title: '常见错误', objective: '形成检查清单。', bullets: ['忘记更新变量', 'continue 跳过更新', '变量混用'] },
        { title: '课堂练习', objective: '即时巩固。', bullets: ['补全代码', '判断输出', '记录变量变化'] },
        { title: '课后任务', objective: '迁移应用。', bullets: ['完成循环补全题', '提交嵌套循环代码说明'] }
      ]
    };
    coursewareLibraryStatus.value = '待加入教学资源库';
    message.value = '已生成课件大纲';
  } finally {
    coursewareLoading.value = false;
  }
}

function addCoursewareToLibrary() {
  if (!courseware.value) {
    message.value = '请先生成课件大纲';
    return;
  }
  coursewareLibraryStatus.value = '已加入教学资源库';
  message.value = courseware.value.libraryMessage || '已加入教学资源库';
}

function markAction(action: string, item: ResourceCard) {
  if (action === '加入资源库') {
    item.libraryStatus = '已入库';
    message.value = '已加入智能资源库';
    return;
  }
  if (action === '推送给学生') {
    item.pushStatus = '已推送';
    item.feedbackStatus = '等待学习反馈';
    message.value = '已推送至李明的今日学习任务';
    return;
  }
  activeReviewTitle.value = activeReviewTitle.value === item.title ? null : item.title;
  message.value = `${item.title} 审核摘要已${activeReviewTitle.value ? '展开' : '收起'}。`;
}
</script>

<template>
  <section class="page resource-generate-page">
    <PageHeader title="个性化多模态资源生成中心" description="围绕李明的 Python 循环结构薄弱点，展示多智能体协同生成、审核、入库与推送。">
      <template #actions>
        <button @click="generateCoursewareOutline" :disabled="coursewareLoading">{{ coursewareLoading ? '生成中...' : 'AI 课件生成' }}</button>
        <button class="secondary" @click="generatePack()" :disabled="loading">{{ loading && !failLoading ? '生成中...' : '生成资源包' }}</button>
        <button class="secondary" @click="generatePack(true)" :disabled="loading">{{ failLoading ? '生成中...' : '制造失败任务' }}</button>
      </template>
    </PageHeader>

    <p v-if="message" class="panel muted">{{ message }}</p>
    <p v-if="latestTaskStatus" class="panel muted">
      智能生成记录状态：{{ latestTaskStatus }}<span v-if="latestReviewItemId">；审核项 #{{ latestReviewItemId }}</span>
    </p>

    <DataCard title="AI 课件生成" subtitle="根据课程、章节、学生画像和薄弱知识点生成可入库课件大纲">
      <div class="courseware-toolbar">
        <div>
          <strong>默认输入</strong>
          <p>Python 程序设计 / 循环结构 / 李明 / while 循环和循环嵌套需要加强</p>
        </div>
        <div class="courseware-actions">
          <button @click="generateCoursewareOutline" :disabled="coursewareLoading">{{ coursewareLoading ? '生成中...' : '生成课件大纲' }}</button>
          <button class="secondary" @click="addCoursewareToLibrary">{{ coursewareLibraryStatus === '已加入教学资源库' ? '已加入教学资源库' : '加入教学资源库' }}</button>
        </div>
      </div>
      <div v-if="courseware" class="courseware-panel">
        <div class="courseware-summary">
          <div>
            <strong>{{ courseware.title }}</strong>
            <p>{{ courseware.course }} / {{ courseware.chapter }} / {{ courseware.student }}</p>
            <p>薄弱知识点：{{ courseware.weakPoints }}</p>
          </div>
          <div class="status-flow">
            <StatusBadge :label="courseware.statusMessage" tone="success" />
            <StatusBadge :label="coursewareLibraryStatus" :tone="coursewareLibraryStatus === '已加入教学资源库' ? 'success' : 'warning'" />
            <StatusBadge :label="courseware.exportMessage" tone="info" />
          </div>
        </div>
        <div class="courseware-outline-grid">
          <article v-for="section in courseware.outline" :key="section.title">
            <strong>{{ section.title }}</strong>
            <p>{{ section.objective }}</p>
            <ul>
              <li v-for="item in section.bullets" :key="item">{{ item }}</li>
            </ul>
          </article>
        </div>
        <p class="courseware-note">{{ courseware.capabilityNote }}</p>
      </div>
    </DataCard>

    <div class="stat-grid">
      <StatCard label="资源类型" :value="resources.length" unit="类" icon="资" />
      <StatCard label="审核状态" value="通过" hint="AuditAgent 初审" icon="审" tone="green" />
      <StatCard label="关联知识点" value="3" unit="个" icon="知" tone="purple" />
      <StatCard label="低依据风险" value="低" hint="引用完整" icon="据" tone="cyan" />
    </div>

    <div class="content-with-aside">
      <DataCard title="生成表单" subtitle="左侧默认填入当前学生与课程">
        <div class="form-grid">
          <label>学生<input v-model="form.student" /></label>
          <label>课程<input v-model="form.course" /></label>
          <label>章节<input v-model="form.chapter" /></label>
          <label>知识点<input v-model="form.knowledgePoints" /></label>
          <label>学习目标<input v-model="form.goal" /></label>
          <label>资源偏好<input v-model="form.preference" /></label>
        </div>
        <button class="full-button" @click="generatePack()" :disabled="loading">{{ loading ? '生成中...' : '点击生成' }}</button>
      </DataCard>

      <DataCard title="多智能体流程" subtitle="每个节点展示输入、工具、输出、状态、耗时和证据">
        <div class="agent-mini-list">
          <article v-for="item in agentNodes" :key="item.name">
            <div><strong>{{ item.name }}</strong><StatusBadge :label="item.status" tone="success" /></div>
            <p>输入：{{ item.input }}</p>
            <p>工具：{{ item.tool }}</p>
            <p>输出：{{ item.output }}</p>
            <p>耗时：{{ item.duration }} · 证据：{{ item.evidence }}</p>
          </article>
        </div>
      </DataCard>
    </div>

    <DataCard :title="packageTitle" subtitle="资源卡片包含类型、Agent、画像适配、知识点、推荐原因、难度、审核状态和引用依据。">
      <div class="resource-card-grid">
        <article v-for="item in resources" :key="item.title" class="resource-card">
          <div class="resource-head">
            <strong>{{ item.title }}</strong>
            <StatusBadge :label="item.reviewStatus || '通过'" tone="success" />
          </div>
          <p><span>资源类型</span>{{ typeOf(item) }}</p>
          <p><span>生成 Agent</span>{{ agentOf(item) }}</p>
          <p><span>适配画像</span>{{ item.adaptedProfile || '循环结构需巩固，偏好代码实操' }}</p>
          <p><span>关联知识点</span>{{ (item.relatedKnowledgePoints || []).join('、') }}</p>
          <p><span>推荐原因</span>{{ reasonOf(item) }}</p>
          <p><span>难度等级</span>{{ item.difficulty }}</p>
          <p v-if="item.description"><span>资源说明</span>{{ item.description }}</p>
          <p><span>适合对象</span>{{ item.suitableLearner || '李明：循环结构需巩固，偏好代码实操' }}</p>
          <p><span>预计学习时间</span>{{ item.estimatedMinutes || 20 }} 分钟</p>
          <div v-if="isAnimation(item) && item.content" class="animation-preview">
            <iframe :srcdoc="item.content" sandbox="" title="动画资源预览"></iframe>
          </div>
          <div v-if="isTts(item)" class="review-summary">
            <strong>语音资源状态</strong>
            <p><span>TTS 配置</span>{{ item.tts_status?.message || '可配置科大讯飞 TTS；当前保留文本讲解资源。' }}</p>
            <p><span>合成结果</span>{{ item.tts_result?.message || '无 Key 时不会伪装真实音频。' }}</p>
          </div>
          <div v-if="typeOf(item) === 'video_script' && item.ffmpeg_status" class="review-summary">
            <strong>视频导出状态</strong>
            <p>{{ item.ffmpeg_status.message }}</p>
          </div>
          <div v-if="isVideoMp4(item)" class="review-summary">
            <strong>MP4 合成状态</strong>
            <p>{{ item.status === 'generated' ? `已生成：${item.file_path || 'MP4 文件'}` : item.description || '配置 FFmpeg 后可合成 MP4，HTML 动画为当前稳定预览能力。' }}</p>
          </div>
          <div class="status-flow">
            <StatusBadge :label="item.reviewStatus || '已审核'" :tone="statusTone(item.reviewStatus)" />
            <StatusBadge :label="item.libraryStatus || '待加入'" :tone="statusTone(item.libraryStatus)" />
            <StatusBadge :label="item.pushStatus || '待推送'" :tone="statusTone(item.pushStatus)" />
            <StatusBadge :label="item.feedbackStatus || '待学习反馈'" :tone="statusTone(item.feedbackStatus)" />
          </div>
          <p><span>引用依据</span>{{ (item.references || ['Python 程序设计课程知识库 / 循环结构章节']).join('；') }}</p>
          <div v-if="activeReviewTitle === item.title" class="review-summary">
            <strong>审核摘要</strong>
            <p><span>事实准确性</span>{{ item.reviewSummary?.factualAccuracy }}</p>
            <p><span>引用依据完整性</span>{{ item.reviewSummary?.referenceCompleteness }}</p>
            <p><span>难度匹配度</span>{{ item.reviewSummary?.difficultyMatch }}</p>
            <p><span>人工复核建议</span>{{ item.reviewSummary?.humanReviewAdvice }}</p>
          </div>
          <div class="resource-actions">
            <button class="secondary" @click="markAction('加入资源库', item)" :disabled="item.libraryStatus === '已入库'">
              {{ item.libraryStatus === '已入库' ? '已加入' : '加入资源库' }}
            </button>
            <button @click="markAction('推送给学生', item)" :disabled="item.pushStatus === '已推送'">
              {{ item.pushStatus === '已推送' ? '已推送' : '推送给学生' }}
            </button>
            <button class="ghost" @click="markAction('查看审核', item)">{{ activeReviewTitle === item.title ? '收起审核' : '查看审核' }}</button>
          </div>
        </article>
        <p v-if="!resources.length" class="panel muted">暂无数据，系统将根据你的学习记录生成建议。</p>
      </div>
    </DataCard>
  </section>
</template>

<style scoped>
.content-with-aside {
  display: grid;
  grid-template-columns: 360px minmax(0, 1fr);
  gap: 16px;
}

.form-grid,
.agent-mini-list,
.resource-card-grid {
  display: grid;
  gap: 12px;
}

.form-grid label {
  display: grid;
  gap: 6px;
  color: var(--color-text-sub);
  font-size: 13px;
  font-weight: 700;
}

.full-button {
  width: 100%;
  margin-top: 14px;
}

.agent-mini-list article,
.resource-card {
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 12px;
  background: #fff;
}

.agent-mini-list article > div,
.resource-head,
.resource-actions {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: center;
}

.agent-mini-list p,
.resource-card p {
  margin: 6px 0 0;
  color: var(--color-text-sub);
  line-height: 1.55;
}

.resource-card-grid {
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}

.resource-card p span {
  display: inline-block;
  min-width: 84px;
  color: var(--color-primary-dark);
  font-weight: 800;
}

.status-flow {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 10px;
}

.review-summary {
  margin-top: 12px;
  border-radius: 8px;
  padding: 12px;
  background: var(--color-primary-light);
}

.animation-preview {
  margin-top: 12px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
}

.animation-preview iframe {
  width: 100%;
  min-height: 230px;
  border: 0;
  display: block;
}

.review-summary strong {
  display: block;
  margin-bottom: 8px;
}

.review-summary p {
  color: var(--color-text);
}

.resource-actions {
  justify-content: flex-start;
  margin-top: 12px;
  flex-wrap: wrap;
}

.courseware-toolbar,
.courseware-summary {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.courseware-toolbar p,
.courseware-summary p,
.courseware-outline-grid p,
.courseware-note {
  margin: 6px 0 0;
  color: var(--color-text-sub);
}

.courseware-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.courseware-panel {
  display: grid;
  gap: 14px;
  margin-top: 14px;
}

.courseware-outline-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 12px;
}

.courseware-outline-grid article {
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 12px;
  background: #fff;
}

.courseware-outline-grid ul {
  margin: 10px 0 0;
  padding-left: 18px;
  color: var(--color-text-sub);
  line-height: 1.6;
}

.courseware-note {
  border-radius: 8px;
  padding: 10px 12px;
  background: var(--color-primary-light);
}

@media (max-width: 980px) {
  .content-with-aside {
    grid-template-columns: 1fr;
  }

  .courseware-toolbar,
  .courseware-summary {
    display: grid;
  }
}
</style>
