<script setup lang="ts">
import PageHeader from '../components/PageHeader.vue';
import DataCard from '../components/DataCard.vue';
import ProgressBar from '../components/ProgressBar.vue';
import StatusBadge from '../components/StatusBadge.vue';
import StatCard from '../components/StatCard.vue';

const tasks = [
  { title: '完成爬虫案例练习', course: 'Python 爬虫基础与实践', due: '今天 23:59', progress: 75, status: '进行中' },
  { title: '数据结构章节测验', course: '数据结构与算法', due: '明天 18:00', progress: 20, status: '未开始' },
  { title: '阅读 RAG 系统原理', course: '人工智能导论', due: '明天 23:59', progress: 100, status: '已完成' }
];
</script>

<template>
  <section class="page">
    <PageHeader title="今日任务 / 日历" description="管理当天学习任务、截止时间和完成状态。">
      <template #actions><button>添加提醒</button></template>
    </PageHeader>
    <div class="stat-grid">
      <StatCard label="今日任务" value="4" unit="项" hint="2 项待完成" icon="任" />
      <StatCard label="已完成" value="2" unit="项" hint="继续保持" icon="完" tone="green" />
      <StatCard label="即将截止" value="1" unit="项" hint="今天 23:59" icon="截" tone="orange" />
    </div>
    <DataCard title="任务列表" subtitle="按截止时间排序">
      <div class="list">
        <article v-for="task in tasks" :key="task.title" class="item">
          <div class="item compact">
            <div><strong>{{ task.title }}</strong><p>{{ task.course }} · {{ task.due }}</p></div>
            <StatusBadge :label="task.status" :tone="task.status === '已完成' ? 'success' : task.status === '进行中' ? 'purple' : 'neutral'" />
          </div>
          <ProgressBar :value="task.progress" />
        </article>
      </div>
    </DataCard>
  </section>
</template>
