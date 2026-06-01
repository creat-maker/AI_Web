<script setup lang="ts">
import PageHeader from '../components/PageHeader.vue';
import DataCard from '../components/DataCard.vue';
import ProgressBar from '../components/ProgressBar.vue';
import StatCard from '../components/StatCard.vue';

const records = [
  { title: '完成今日任务', score: '+120' },
  { title: '测验通过', score: '+80' },
  { title: '参与讨论', score: '+50' }
];
</script>

<template>
  <section class="page">
    <PageHeader title="积分等级" description="查看学习积分、等级成长和积分明细。" />
    <div class="stat-grid">
      <StatCard label="学习积分" value="8,450" unit="分" hint="本周 +120" icon="分" />
      <StatCard label="当前等级" value="Lv.6" hint="学习达人" icon="级" tone="purple" />
      <StatCard label="排名" value="12" unit="名" hint="班级前 18%" icon="排" tone="green" />
    </div>
    <DataCard title="等级进度" subtitle="下一等级：Lv.7 学霸">
      <ProgressBar :value="68" />
    </DataCard>
    <DataCard title="积分明细">
      <div class="list"><div v-for="item in records" :key="item.title" class="item compact"><strong>{{ item.title }}</strong><span>{{ item.score }}</span></div></div>
    </DataCard>
  </section>
</template>
