<script setup lang="ts">
import { computed, ref } from 'vue';
import DataCard from '../components/DataCard.vue';
import PageHeader from '../components/PageHeader.vue';
import ProgressBar from '../components/ProgressBar.vue';
import StatCard from '../components/StatCard.vue';
import StatusBadge from '../components/StatusBadge.vue';

const selectedId = ref(1);

const reports = [
  {
    id: 1,
    title: '李明 Python 循环结构形成性评价报告',
    student: '李明',
    course: 'Python 程序设计',
    chapter: '循环结构',
    status: '已完成',
    quality: 92,
    createdAt: '2026-06-11 10:30',
    abstract: '系统发现李明在循环结构上还需要加强，当前主要问题集中在 while 循环条件更新、循环嵌套变量变化和 break / continue 区分。',
    accuracy: 62,
    wrongPoints: ['while 循环条件更新', '循环嵌套变量变化', 'break / continue 区分'],
    mistakeReasons: ['循环变量更新位置不稳定', '嵌套循环内外层变量混淆', '把 continue 误认为直接结束循环'],
    aiAdvice: '先完成变量变化表，再运行短代码验证。每次练习后记录一个主错因，避免只看答案不复盘。',
    nextPath: 'while 循环补全题 -> break / continue 对比题 -> 循环嵌套综合任务',
    resourceStrategy: '保留讲解文档和视频脚本，增加 3 道 while 循环补全题，降低嵌套循环任务难度。',
    teacherSuggestion: '推送循环结构补弱资源包，安排 10 分钟代码讲解，布置 3 道 while 循环补全题。'
  },
  {
    id: 2,
    title: '计科大三 1 班循环结构班级报告',
    student: '计科大三 1 班',
    course: 'Python 程序设计',
    chapter: '循环结构',
    status: '已完成',
    quality: 88,
    createdAt: '2026-06-10 18:20',
    abstract: '班级整体掌握度中等，薄弱点集中在 while 循环条件更新和循环嵌套变量追踪。',
    accuracy: 74,
    wrongPoints: ['while 循环条件更新', '循环嵌套变量变化'],
    mistakeReasons: ['部分学生忽略循环变量更新', '对内外层循环执行顺序不稳定'],
    aiAdvice: '下一轮课堂建议先讲变量变化表，再安排短代码即时练习。',
    nextPath: '班级讲评 -> 分层练习 -> 个别学生补弱任务',
    resourceStrategy: '对基础薄弱学生推送低门槛练习，对掌握较好学生推送嵌套循环挑战题。',
    teacherSuggestion: '课堂集中讲解 10 分钟，并对李明等需重点关注学生进行课后跟踪。'
  }
];

const dimensions = [
  { name: '概念理解', value: 66 },
  { name: '代码应用', value: 58 },
  { name: '答题稳定性', value: 61 },
  { name: '学习活跃度', value: 78 },
  { name: '资源利用率', value: 72 },
  { name: '知识迁移能力', value: 55 }
];

const selectedReport = computed(() => reports.find((item) => item.id === selectedId.value) || reports[0]);

const statCards = computed(() => [
  { label: '报告总数', value: reports.length, unit: '份', hint: '循环结构主题报告', icon: '报' },
  { label: '李明正确率', value: selectedReport.value.accuracy, unit: '%', hint: '形成性评价结果', icon: '准', tone: 'orange' as const },
  { label: '能力维度', value: dimensions.length, unit: '项', hint: '综合评分画像', icon: '能', tone: 'purple' as const },
  { label: '引用依据', value: 1, unit: '库', hint: 'Python 程序设计课程知识库', icon: '引', tone: 'green' as const }
]);
</script>

<template>
  <section class="page report-page">
    <PageHeader
      title="Python 循环结构形成性评价报告"
      description="报告对象聚焦李明，沉淀正确率、错因分析、能力维度、AI 建议、下一步路径和教师干预建议。"
    >
      <template #actions>
        <button class="secondary">导出报告</button>
        <button>重新生成评价</button>
      </template>
    </PageHeader>

    <div class="stat-grid">
      <StatCard v-for="item in statCards" :key="item.label" v-bind="item" />
    </div>

    <div class="report-layout">
      <DataCard title="报告列表" subtitle="当前报告重点围绕 Python 循环结构">
        <div class="report-list">
          <button
            v-for="report in reports"
            :key="report.id"
            :class="['report-row', { active: report.id === selectedId }]"
            type="button"
            @click="selectedId = report.id"
          >
            <strong>{{ report.title }}</strong>
            <span>{{ report.course }} / {{ report.chapter }} / {{ report.student }}</span>
            <small>{{ report.createdAt }} / 质量评分 {{ report.quality }}</small>
            <StatusBadge :label="report.status" tone="success" />
          </button>
        </div>
      </DataCard>

      <DataCard title="报告预览" :subtitle="selectedReport.title">
        <div class="preview-grid">
          <article class="preview-card wide">
            <span>报告摘要</span>
            <p>{{ selectedReport.abstract }}</p>
          </article>
          <article class="preview-card">
            <span>正确率</span>
            <strong>{{ selectedReport.accuracy }}%</strong>
            <p>循环结构专项测验</p>
          </article>
          <article class="preview-card">
            <span>引用依据</span>
            <strong>课程知识库</strong>
            <p>Python 程序设计 / 循环结构章节</p>
          </article>
        </div>
      </DataCard>
    </div>

    <div class="report-layout">
      <DataCard title="错题知识点与错因分析" subtitle="用于驱动下一步路径和资源调整">
        <div class="analysis-list">
          <article v-for="(point, index) in selectedReport.wrongPoints" :key="point" class="analysis-row">
            <StatusBadge :label="point" tone="warning" />
            <p>{{ selectedReport.mistakeReasons[index] }}</p>
          </article>
        </div>
      </DataCard>

      <DataCard title="能力维度评分" subtitle="形成性评价核心维度">
        <div class="dimension-list">
          <div v-for="item in dimensions" :key="item.name" class="dimension-row">
            <span>{{ item.name }}</span>
            <ProgressBar :value="item.value" :tone="item.value < 65 ? 'warning' : 'primary'" />
            <strong>{{ item.value }}</strong>
          </div>
        </div>
      </DataCard>
    </div>

    <DataCard title="AI 学习建议与后续调整" subtitle="AI 仅提供辅助建议，最终由教师确认">
      <div class="strategy-grid">
        <article>
          <strong>AI 学习建议</strong>
          <p>{{ selectedReport.aiAdvice }}</p>
        </article>
        <article>
          <strong>下一步路径</strong>
          <p>{{ selectedReport.nextPath }}</p>
        </article>
        <article>
          <strong>资源调整策略</strong>
          <p>{{ selectedReport.resourceStrategy }}</p>
        </article>
        <article>
          <strong>教师干预建议</strong>
          <p>{{ selectedReport.teacherSuggestion }}</p>
        </article>
      </div>
    </DataCard>
  </section>
</template>

<style scoped>
.report-layout {
  display: grid;
  grid-template-columns: minmax(0, 0.95fr) minmax(420px, 1.05fr);
  gap: 16px;
}

.report-list,
.preview-grid,
.analysis-list,
.dimension-list,
.strategy-grid {
  display: grid;
  gap: 12px;
}

.report-row {
  display: grid;
  gap: 6px;
  width: 100%;
  border: 1px solid var(--border-light);
  border-radius: 12px;
  padding: 14px;
  text-align: left;
  background: #fff;
}

.report-row.active {
  border-color: var(--color-primary);
  background: var(--color-primary-light);
}

.preview-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.preview-card,
.analysis-row,
.strategy-grid article {
  border: 1px solid var(--border-light);
  border-radius: 12px;
  padding: 14px;
  background: #fff;
}

.preview-card.wide {
  grid-column: 1 / -1;
}

.preview-card span {
  color: var(--text-muted);
  font-size: 13px;
}

.preview-card strong {
  display: block;
  margin-top: 8px;
  font-size: 24px;
  color: var(--text-main);
}

.preview-card p,
.analysis-row p,
.strategy-grid p {
  margin: 8px 0 0;
  color: var(--text-secondary);
  line-height: 1.65;
}

.dimension-row {
  display: grid;
  grid-template-columns: 112px minmax(0, 1fr) 42px;
  gap: 10px;
  align-items: center;
}

.strategy-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
}

@media (max-width: 1120px) {
  .report-layout,
  .preview-grid,
  .strategy-grid {
    grid-template-columns: 1fr;
  }
}
</style>
