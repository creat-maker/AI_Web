<script setup lang="ts">
import PageHeader from '../components/PageHeader.vue';
import DataCard from '../components/DataCard.vue';
import StatCard from '../components/StatCard.vue';

const badges = ['连续学习', '勤奋学习者', '测验达人', '探索先锋', '知识收藏家', '小组贡献者'];
</script>

<template>
  <section class="page">
    <PageHeader title="成就徽章" description="展示学习成就、获得记录和成长激励。" />
    <div class="stat-grid">
      <StatCard label="已获得" value="8" unit="枚" hint="本月 +3" icon="徽" />
      <StatCard label="连续学习" value="12" unit="天" hint="保持专注" icon="连" tone="green" />
      <StatCard label="下一徽章" value="3" unit="天" hint="进阶学习者" icon="升" tone="purple" />
    </div>
    <DataCard title="我的徽章">
      <div class="badge-grid">
        <article v-for="badge in badges" :key="badge" class="badge-card"><span>{{ badge.slice(0, 1) }}</span><strong>{{ badge }}</strong><p>已获得</p></article>
      </div>
    </DataCard>
  </section>
</template>

<style scoped>
.badge-grid { display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 12px; }
.badge-card { display: grid; justify-items: center; gap: 8px; border: 1px solid var(--color-border); border-radius: 16px; padding: 16px; background: #fbfdff; text-align: center; }
.badge-card span { display: inline-grid; place-items: center; width: 56px; height: 56px; border-radius: 18px; color: #fff; font-weight: 800; background: linear-gradient(135deg, var(--color-primary), var(--color-purple)); }
.badge-card p { margin: 0; }
@media (max-width: 980px) { .badge-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
</style>
