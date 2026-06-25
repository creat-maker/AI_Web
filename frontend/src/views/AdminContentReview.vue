<script setup lang="ts">
import { computed, ref } from 'vue';
import DataCard from '../components/DataCard.vue';
import PageHeader from '../components/PageHeader.vue';
import StatCard from '../components/StatCard.vue';
import StatusBadge from '../components/StatusBadge.vue';

type ReviewStatus = '通过' | '需修改' | '人工复核' | '风险拦截';

interface ReviewItem {
  id: string;
  title: string;
  type: string;
  source: string;
  status: ReviewStatus;
  risk: string;
  basis: string;
  references: string[];
  dimensions: string[];
  reviewDetails: {
    factualAccuracy: string;
    referenceCompleteness: string;
    difficultyMatch: string;
    humanReviewAdvice: string;
  };
  opinion: string;
}

const statusFilter = ref<'全部' | ReviewStatus>('全部');
const message = ref('');
const selectedReviewId = ref('cr-001');
const actionLoading = ref('');

const dimensions = ['事实准确性', '知识点匹配度', '难度匹配度', '引用依据完整性', '敏感违规内容', '人工复核建议'];

const items = ref<ReviewItem[]>([
  {
    id: 'cr-001',
    title: 'Python 循环结构个性化补弱资源包',
    type: '资源包',
    source: 'ResourcePackageAgent',
    status: '通过',
    risk: '低风险',
    basis: 'Python 程序设计课程知识库 / 循环结构章节',
    references: ['Python 程序设计课程知识库 / 循环结构章节', '课堂练习：while 循环条件更新', '错题标签：break / continue 混淆'],
    dimensions: ['事实准确性', '知识点匹配度', '难度匹配度', '引用依据完整性'],
    reviewDetails: {
      factualAccuracy: '通过。资源对 while 循环终止条件、循环嵌套变量变化和 break / continue 的解释与课程知识库一致。',
      referenceCompleteness: '完整。每类资源都绑定课程知识库章节和错题标签，可追溯到知识点。',
      difficultyMatch: '匹配。难度从基础讲解到中等练习，符合李明“需巩固 + 代码实操偏好”的画像。',
      humanReviewAdvice: '建议教师抽查分层练习答案解析，确认示例代码输出和课堂版本一致。'
    },
    opinion: '资源覆盖 while 循环、break / continue 和循环嵌套，难度适合李明当前画像。'
  },
  {
    id: 'cr-002',
    title: 'AI 学伴回答：为什么我的 while 循环会死循环？',
    type: 'AI 学伴回答',
    source: 'TutorAgent',
    status: '需修改',
    risk: '复核优先级：中',
    basis: 'Python 程序设计课程知识库 / 循环结构章节',
    references: ['Python 程序设计课程知识库 / while 循环小节', '李明近期错题：while 循环变量忘记更新'],
    dimensions: ['事实准确性', '引用依据完整性', '人工复核建议'],
    reviewDetails: {
      factualAccuracy: '基本通过。死循环原因判断正确，但需要补充 continue 跳过变量更新的边界情况。',
      referenceCompleteness: '部分完整。已引用课程知识库，但学生错题证据需要在回答中更明确呈现。',
      difficultyMatch: '匹配。解释适合基础薄弱学生，但示例代码应更短。',
      humanReviewAdvice: '建议补一个 5 行以内的最小 while 示例，并标注变量更新行。'
    },
    opinion: '回答方向正确，但需要补充循环变量更新示例，并提醒学生先运行短代码验证。'
  },
  {
    id: 'cr-003',
    title: 'while 死循环讲解内容',
    type: '微课视频脚本',
    source: 'TeachingScriptAgent',
    status: '人工复核',
    risk: '复核优先级：中',
    basis: 'Python 程序设计课程知识库 / 循环结构章节',
    references: ['Python 程序设计课程知识库 / 循环结构章节', '课堂示例：猜数字循环'],
    dimensions: ['知识点匹配度', '难度匹配度', '人工复核建议'],
    reviewDetails: {
      factualAccuracy: '待人工确认。脚本中的变量更新位置正确，但旁白描述存在轻微歧义。',
      referenceCompleteness: '完整。已引用课程章节和课堂示例。',
      difficultyMatch: '基本匹配。视频脚本适合基础学生，但动画节奏需要放慢。',
      humanReviewAdvice: '建议教师复核旁白中“条件满足继续循环”的表述，避免学生误解。'
    },
    opinion: '建议教师复核示例代码，确认变量更新位置和循环条件表述无歧义。'
  },
  {
    id: 'cr-004',
    title: '未经引用的循环结构结论',
    type: '个性化推荐',
    source: 'EvaluationAgent',
    status: '风险拦截',
    risk: '高风险',
    basis: '缺少明确课程知识库引用',
    references: ['缺少明确课程知识库引用'],
    dimensions: ['引用依据完整性', '敏感违规内容', '人工复核建议'],
    reviewDetails: {
      factualAccuracy: '无法确认。内容没有绑定课程知识库来源。',
      referenceCompleteness: '不完整。缺少章节、知识点或错题来源引用。',
      difficultyMatch: '无法判断。没有学生画像或练习目标依据。',
      humanReviewAdvice: '禁止发布。需补充引用依据并重新提交审核。'
    },
    opinion: '缺少可追溯引用，不允许直接发布到学生端。'
  }
]);

const filteredItems = computed(() => items.value.filter((item) => statusFilter.value === '全部' || item.status === statusFilter.value));
const selectedReview = computed(() => items.value.find((item) => item.id === selectedReviewId.value) || items.value[0]);

const statusCount = computed(() => ({
  pass: items.value.filter((item) => item.status === '通过').length,
  revise: items.value.filter((item) => item.status === '需修改').length,
  human: items.value.filter((item) => item.status === '人工复核').length,
  block: items.value.filter((item) => item.status === '风险拦截').length
}));

function tone(status: ReviewStatus) {
  if (status === '通过') return 'success';
  if (status === '需修改') return 'warning';
  if (status === '人工复核') return 'purple';
  return 'danger';
}

function setStatus(id: string, status: ReviewStatus) {
  const item = items.value.find((row) => row.id === id);
  if (!item) return;
  actionLoading.value = `${id}-${status}`;
  selectedReviewId.value = id;
  message.value = '正在更新审核状态...';
  window.setTimeout(() => {
    item.status = status;
    item.opinion = `审核状态已更新为「${status}」。AI 生成内容仍需教师或管理员确认后发布。`;
    message.value = `${item.title} 已更新为「${status}」。`;
    actionLoading.value = '';
  }, 350);
}

function selectReview(id: string) {
  selectedReviewId.value = id;
  const item = items.value.find((row) => row.id === id);
  if (item) message.value = `正在查看「${item.title}」的审核详情和引用依据。`;
}

function runHeaderAction(key: string, doneMessage: string) {
  actionLoading.value = key;
  message.value = '正在处理，请稍候...';
  window.setTimeout(() => {
    actionLoading.value = '';
    message.value = doneMessage;
  }, 350);
}
</script>

<template>
  <section class="page admin-content-review">
    <PageHeader
      title="AI 内容审核中心"
      description="审核状态与后端 displayReviewStatus 对齐，AI 生成内容不直接发布。"
    >
      <template #actions>
        <button class="secondary" :disabled="actionLoading === 'export'" @click="runHeaderAction('export', '审核记录导出任务已准备。')">{{ actionLoading === 'export' ? '准备中...' : '导出审核记录' }}</button>
        <button :disabled="actionLoading === 'decision'" @click="runHeaderAction('decision', '可从导航进入教学决策中心查看平台汇总。')">{{ actionLoading === 'decision' ? '打开中...' : '进入教学决策中心' }}</button>
      </template>
    </PageHeader>
    <p v-if="message" class="panel muted">{{ message }}</p>

    <div class="stat-grid">
      <StatCard label="通过" :value="statusCount.pass" unit="项" hint="可进入发布流程" icon="通" tone="green" />
      <StatCard label="需修改" :value="statusCount.revise" unit="项" hint="返回资源生成环节" icon="改" tone="orange" />
      <StatCard label="人工复核" :value="statusCount.human" unit="项" hint="需教师或管理员确认" icon="人" tone="purple" />
      <StatCard label="风险拦截" :value="statusCount.block" unit="项" hint="禁止直接发布" icon="拦" tone="red" />
    </div>

    <DataCard title="审核原则" subtitle="事实、知识点、难度、引用和安全维度同时检查">
      <div class="principle-grid">
        <span v-for="item in dimensions" :key="item">{{ item }}</span>
      </div>
      <p class="basis-text">引用依据显式展示：Python 程序设计课程知识库 / 循环结构章节。</p>
      <p class="basis-text">讯飞安全服务配置状态：可配置；未配置时启用本地规则审核、引用覆盖度检查和人工复核流程。</p>
    </DataCard>

    <DataCard v-if="selectedReview" title="资源审核详情" :subtitle="selectedReview.title">
      <div class="review-detail-grid">
        <article>
          <span>事实准确性</span>
          <p>{{ selectedReview.reviewDetails.factualAccuracy }}</p>
        </article>
        <article>
          <span>引用依据完整性</span>
          <p>{{ selectedReview.reviewDetails.referenceCompleteness }}</p>
        </article>
        <article>
          <span>难度匹配度</span>
          <p>{{ selectedReview.reviewDetails.difficultyMatch }}</p>
        </article>
        <article>
          <span>人工复核建议</span>
          <p>{{ selectedReview.reviewDetails.humanReviewAdvice }}</p>
        </article>
      </div>
      <div class="reference-panel">
        <strong>引用依据</strong>
        <span v-for="reference in selectedReview.references" :key="reference">{{ reference }}</span>
      </div>
    </DataCard>

    <DataCard title="审核筛选" subtitle="统一状态：通过、需修改、人工复核、风险拦截">
      <div class="filter-row">
        <select v-model="statusFilter">
          <option>全部</option>
          <option>通过</option>
          <option>需修改</option>
          <option>人工复核</option>
          <option>风险拦截</option>
        </select>
      </div>
    </DataCard>

    <DataCard title="Python 循环结构资源审核列表" :subtitle="`${filteredItems.length} 项内容`">
      <div class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>内容标题</th>
              <th>类型</th>
              <th>生成来源</th>
              <th>引用依据</th>
              <th>审核维度</th>
              <th>状态</th>
              <th>审核意见</th>
              <th>模拟操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredItems" :key="item.id">
              <td><strong>{{ item.title }}</strong><p>{{ item.risk }}</p></td>
              <td>{{ item.type }}</td>
              <td>{{ item.source }}</td>
              <td>{{ item.basis }}</td>
              <td>
                <div class="tag-list">
                  <span v-for="tag in item.dimensions" :key="tag">{{ tag }}</span>
                </div>
              </td>
              <td><StatusBadge :label="item.status" :tone="tone(item.status)" /></td>
              <td>{{ item.opinion }}</td>
              <td>
                <div class="row-actions">
                  <button class="secondary" :disabled="actionLoading === `${item.id}-通过`" @click="setStatus(item.id, '通过')">{{ actionLoading === `${item.id}-通过` ? '处理中...' : '通过' }}</button>
                  <button class="secondary" :disabled="actionLoading === `${item.id}-需修改`" @click="setStatus(item.id, '需修改')">{{ actionLoading === `${item.id}-需修改` ? '处理中...' : '需修改' }}</button>
                  <button class="ghost" :disabled="actionLoading === `${item.id}-人工复核`" @click="setStatus(item.id, '人工复核')">{{ actionLoading === `${item.id}-人工复核` ? '处理中...' : '复核' }}</button>
                  <button class="danger" :disabled="actionLoading === `${item.id}-风险拦截`" @click="setStatus(item.id, '风险拦截')">{{ actionLoading === `${item.id}-风险拦截` ? '处理中...' : '拦截' }}</button>
                  <button class="ghost" @click="selectReview(item.id)">详情</button>
                </div>
              </td>
            </tr>
            <tr v-if="!filteredItems.length">
              <td colspan="8">暂无数据，系统将根据你的学习记录生成建议。</td>
            </tr>
          </tbody>
        </table>
      </div>
    </DataCard>
  </section>
</template>

<style scoped>
.principle-grid,
.tag-list,
.row-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.principle-grid span,
.tag-list span {
  border-radius: 999px;
  padding: 6px 10px;
  color: var(--color-primary-dark);
  background: var(--color-primary-light);
  font-size: 12px;
  font-weight: 700;
}

.basis-text {
  margin: 12px 0 0;
  color: var(--text-secondary);
}

.review-detail-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.review-detail-grid article {
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 12px;
  background: #fff;
}

.review-detail-grid span,
.reference-panel strong {
  color: var(--color-primary-dark);
  font-weight: 800;
}

.review-detail-grid p {
  margin: 8px 0 0;
  color: var(--color-text-sub);
  line-height: 1.6;
}

.reference-panel {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
  padding: 12px;
  border-radius: 8px;
  background: var(--color-primary-light);
}

.reference-panel strong {
  width: 100%;
}

.reference-panel span {
  border-radius: 999px;
  padding: 6px 10px;
  background: #fff;
  color: var(--color-text);
  font-size: 12px;
  font-weight: 700;
}

.filter-row {
  max-width: 220px;
}

.table-wrap {
  overflow-x: auto;
}

td p {
  margin: 6px 0 0;
  color: var(--text-muted);
  font-size: 12px;
}

@media (max-width: 820px) {
  .review-detail-grid {
    grid-template-columns: 1fr;
  }
}
</style>
