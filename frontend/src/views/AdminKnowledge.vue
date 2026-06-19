<script setup lang="ts">
import DataCard from '../components/DataCard.vue';
import PageHeader from '../components/PageHeader.vue';
import ProgressBar from '../components/ProgressBar.vue';
import StatCard from '../components/StatCard.vue';
import StatusBadge from '../components/StatusBadge.vue';
import { ref } from 'vue';

const categories = [
  { label: '课程资料', value: 128, tone: 'info' as const },
  { label: '题库资源', value: 86, tone: 'success' as const },
  { label: '知识点', value: 215, tone: 'purple' as const },
  { label: '实验案例', value: 64, tone: 'warning' as const }
];

const resources = [
  { name: 'Python 循环结构讲义.pdf', type: 'PDF', course: 'Python 程序设计', owner: '王老师', size: '12.6 MB', status: '已发布', updated: '05-30 10:25' },
  { name: 'while 死循环修复案例.ipynb', type: 'Jupyter', course: 'Python 程序设计', owner: '王老师', size: '8.9 MB', status: '解析中', updated: '05-30 09:42' },
  { name: 'break continue 专项练习.docx', type: 'DOCX', course: 'Python 程序设计', owner: '陈老师', size: '5.4 MB', status: '待审核', updated: '05-29 18:20' },
  { name: '循环嵌套变量变化表.xlsx', type: 'Excel', course: 'Python 程序设计', owner: 'Admin', size: '2.1 MB', status: '已发布', updated: '05-29 16:05' }
];

const smartResources = [
  {
    resourceId: 'loop-pack-001',
    title: 'Python 循环结构个性化补弱资源包',
    course: 'Python 程序设计',
    chapter: '循环结构',
    knowledgePoints: ['while 循环', '循环嵌套', 'break / continue'],
    resourceType: '资源包',
    difficulty: '基础到中等',
    suitableLearnerTags: ['基础薄弱', '代码实操偏好', '需重点练习'],
    sourceAgent: '多类型资源生成 Agent',
    reviewStatus: '通过',
    references: ['Python 程序设计课程知识库 / 循环结构章节'],
    usageCount: 28,
    recommendationReason: '匹配李明的薄弱知识点和代码案例 + 图解偏好。',
    loopStatus: {
      generated: '已生成',
      reviewed: '已审核',
      stored: '已入库',
      recommended: '已推荐',
      feedback: '李明已完成 3 / 7'
    }
  },
  {
    resourceId: 'loop-case-while-002',
    title: 'while 死循环修复案例',
    course: 'Python 程序设计',
    chapter: '循环结构',
    knowledgePoints: ['while 循环', '变量更新'],
    resourceType: '代码实操案例',
    difficulty: '基础',
    suitableLearnerTags: ['基础薄弱', '代码实操偏好'],
    sourceAgent: '多类型资源生成 Agent',
    reviewStatus: '通过',
    references: ['Python 程序设计课程知识库 / while 循环小节', '课堂示例：计数器循环'],
    usageCount: 12,
    recommendationReason: '用于修复 while 条件一直为 True 或变量未更新的问题。',
    loopStatus: {
      generated: '已生成',
      reviewed: '已审核',
      stored: '已入库',
      recommended: '已推送',
      feedback: '等待学习反馈'
    }
  }
];

const closedLoop = [
  { step: '生成', status: '已生成', detail: '资源生成规划 Agent 完成多类型资源输出' },
  { step: '审核', status: '已审核', detail: '内容安全与防幻觉审核 Agent 已通过' },
  { step: '入库', status: '已入库', detail: '绑定知识点后进入智能资源库' },
  { step: '推荐', status: '已推荐', detail: '已进入李明的个性化推荐队列' },
  { step: '学习反馈', status: '回收中', detail: '收集完成率、正确率和错因标签' }
];
const message = ref('');
const actionLoading = ref('');

function statusTone(status: string) {
  if (status === '已发布') return 'success';
  if (status === '解析中' || status === '待审核') return 'warning';
  return 'neutral';
}

function loopTone(status: string): 'success' | 'warning' | 'info' {
  if (/已|完成/.test(status)) return 'success';
  if (/等待|回收|待/.test(status)) return 'warning';
  return 'info';
}

function runAction(key: string, doneMessage: string) {
  actionLoading.value = key;
  message.value = '正在处理，请稍候...';
  window.setTimeout(() => {
    actionLoading.value = '';
    message.value = doneMessage;
  }, 400);
}
</script>

<template>
  <section class="page">
    <PageHeader title="知识库运营 / 资源库" description="管理平台课程资料、题库资源、知识点切片和存储容量。">
      <template #actions>
        <button :disabled="actionLoading === 'upload'" @click="runAction('upload', '资源上传入口已准备，请选择课程资料后继续。')">{{ actionLoading === 'upload' ? '准备中...' : '上传资源' }}</button>
        <button class="secondary" :disabled="actionLoading === 'parse'" @click="runAction('parse', '已提交批量解析任务，解析完成后会更新资源状态。')">{{ actionLoading === 'parse' ? '提交中...' : '批量解析' }}</button>
      </template>
    </PageHeader>
    <p v-if="message" class="panel muted">{{ message }}</p>

    <div class="stat-grid">
      <StatCard label="资源总数" value="2,846" unit="份" icon="资" />
      <StatCard label="课程资料" value="1,280" unit="份" icon="课" tone="green" />
      <StatCard label="题库资源" value="860" unit="份" icon="题" tone="orange" />
      <StatCard label="知识点" value="12,873" unit="个" icon="知" tone="purple" />
      <StatCard label="存储容量" value="68.4" unit="GB" icon="存" tone="cyan" />
    </div>

    <div class="category-grid">
      <DataCard v-for="item in categories" :key="item.label">
        <div class="category-card">
          <StatusBadge :label="item.label" :tone="item.tone" />
          <strong>{{ item.value }}</strong>
          <span>平台资源分类</span>
        </div>
      </DataCard>
    </div>

    <DataCard title="智能教学资源库" subtitle="展示 AI 资源从生成、审核、绑定知识点、入库、推荐到使用反馈的闭环。">
      <div class="closed-loop">
        <article v-for="(item, index) in closedLoop" :key="item.step">
          <span>{{ index + 1 }}</span>
          <strong>{{ item.step }}</strong>
          <StatusBadge :label="item.status" :tone="loopTone(item.status)" />
          <p>{{ item.detail }}</p>
        </article>
      </div>
      <table class="table smart-resource-table">
        <thead>
          <tr>
            <th>resourceId</th>
            <th>title</th>
            <th>course / chapter</th>
            <th>knowledgePoints</th>
            <th>resourceType</th>
            <th>difficulty</th>
            <th>suitableLearnerTags</th>
            <th>sourceAgent</th>
            <th>reviewStatus</th>
            <th>loopStatus</th>
            <th>references</th>
            <th>usageCount</th>
            <th>recommendationReason</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in smartResources" :key="item.resourceId">
            <td>{{ item.resourceId }}</td>
            <td><strong>{{ item.title }}</strong></td>
            <td>{{ item.course }} / {{ item.chapter }}</td>
            <td>{{ item.knowledgePoints.join('、') }}</td>
            <td>{{ item.resourceType }}</td>
            <td>{{ item.difficulty }}</td>
            <td>{{ item.suitableLearnerTags.join('、') }}</td>
            <td>{{ item.sourceAgent }}</td>
            <td><StatusBadge :label="item.reviewStatus" tone="success" /></td>
            <td>
              <div class="loop-status-list">
                <StatusBadge :label="`生成：${item.loopStatus.generated}`" :tone="loopTone(item.loopStatus.generated)" />
                <StatusBadge :label="`审核：${item.loopStatus.reviewed}`" :tone="loopTone(item.loopStatus.reviewed)" />
                <StatusBadge :label="`入库：${item.loopStatus.stored}`" :tone="loopTone(item.loopStatus.stored)" />
                <StatusBadge :label="`推荐：${item.loopStatus.recommended}`" :tone="loopTone(item.loopStatus.recommended)" />
                <StatusBadge :label="`反馈：${item.loopStatus.feedback}`" :tone="loopTone(item.loopStatus.feedback)" />
              </div>
            </td>
            <td>{{ item.references.join('；') }}</td>
            <td>{{ item.usageCount }}</td>
            <td>{{ item.recommendationReason }}</td>
          </tr>
          <tr v-if="!smartResources.length">
            <td colspan="13">暂无数据，系统将根据你的学习记录生成建议。</td>
          </tr>
        </tbody>
      </table>
    </DataCard>

    <div class="content-with-aside">
      <DataCard title="资源列表" subtitle="资源名称、类型、所属课程、上传者和解析状态">
        <div class="filter-row resource-filter">
          <input placeholder="搜索资源名称、课程、上传者..." />
          <select><option>全部分类</option><option>课程资料</option><option>题库资源</option><option>知识点</option></select>
          <select><option>全部状态</option><option>已发布</option><option>解析中</option><option>待审核</option></select>
        </div>
        <table class="table">
          <thead>
            <tr>
              <th>资源名称</th>
              <th>类型</th>
              <th>所属课程</th>
              <th>上传者</th>
              <th>大小</th>
              <th>状态</th>
              <th>更新时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in resources" :key="item.name">
              <td><strong>{{ item.name }}</strong></td>
              <td><StatusBadge :label="item.type" tone="info" /></td>
              <td>{{ item.course }}</td>
              <td>{{ item.owner }}</td>
              <td>{{ item.size }}</td>
              <td><StatusBadge :label="item.status" :tone="statusTone(item.status)" /></td>
              <td>{{ item.updated }}</td>
              <td>
                <div class="row-actions">
                  <button class="ghost" :disabled="actionLoading === `preview-${item.name}`" @click="runAction(`preview-${item.name}`, `${item.name} 预览已打开。`)">{{ actionLoading === `preview-${item.name}` ? '打开中...' : '预览' }}</button>
                  <button class="ghost" :disabled="actionLoading === `download-${item.name}`" @click="runAction(`download-${item.name}`, `${item.name} 下载任务已准备。`)">{{ actionLoading === `download-${item.name}` ? '准备中...' : '下载' }}</button>
                  <button class="ghost" :disabled="actionLoading === `review-${item.name}`" @click="runAction(`review-${item.name}`, `${item.name} 已进入审核队列。`)">{{ actionLoading === `review-${item.name}` ? '提交中...' : '审核' }}</button>
                </div>
              </td>
            </tr>
            <tr v-if="!resources.length">
              <td colspan="8">暂无数据，系统将根据你的学习记录生成建议。</td>
            </tr>
          </tbody>
        </table>
      </DataCard>

      <DataCard title="存储使用情况" subtitle="容量、解析队列和风险提醒">
        <div class="storage-card">
          <div>
            <strong>68.4 GB / 100 GB</strong>
            <span>当前存储使用率 68%</span>
          </div>
          <ProgressBar :value="68" tone="primary" />
        </div>
        <div class="list">
          <div class="item compact"><strong>解析队列</strong><StatusBadge label="12 个任务" tone="warning" /></div>
          <div class="item compact"><strong>低质量切片</strong><StatusBadge label="36 条" tone="danger" /></div>
          <div class="item compact"><strong>今日上传</strong><StatusBadge label="42 份" tone="success" /></div>
        </div>
      </DataCard>
    </div>
  </section>
</template>

<style scoped>
.category-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 14px;
}

.category-card {
  display: grid;
  gap: 8px;
}

.category-card strong {
  font-size: 26px;
}

.category-card span {
  color: var(--color-text-sub);
}

.resource-filter {
  grid-template-columns: minmax(260px, 1fr) 160px 160px;
}

.row-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.closed-loop {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 10px;
  margin-bottom: 14px;
}

.closed-loop article {
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 10px;
  background: #fff;
}

.closed-loop span {
  display: inline-grid;
  place-items: center;
  width: 28px;
  height: 28px;
  border-radius: 8px;
  color: var(--text-light);
  background: var(--color-primary);
  font-weight: 800;
}

.closed-loop strong {
  display: block;
  margin-top: 8px;
}

.closed-loop p {
  margin: 8px 0 0;
  color: var(--color-text-sub);
  line-height: 1.5;
}

.loop-status-list {
  display: flex;
  min-width: 260px;
  flex-wrap: wrap;
  gap: 6px;
}

.smart-resource-table {
  min-width: 1480px;
}

.storage-card {
  display: grid;
  gap: 10px;
  margin-bottom: 16px;
  border-radius: 16px;
  padding: 14px;
  background: var(--color-primary-light);
}

.storage-card strong,
.storage-card span {
  display: block;
}

.storage-card span {
  margin-top: 4px;
  color: var(--color-text-sub);
}

@media (max-width: 820px) {
  .resource-filter {
    grid-template-columns: 1fr;
  }
  .closed-loop {
    grid-template-columns: 1fr;
  }
}
</style>
