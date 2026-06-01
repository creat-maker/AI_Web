<script setup lang="ts">
import PageHeader from '../components/PageHeader.vue';
import DataCard from '../components/DataCard.vue';
import StatusBadge from '../components/StatusBadge.vue';

const notes = [
  { title: '算法与数据结构的笔记', tag: '算法', time: '今天 10:24' },
  { title: 'Python 爬虫异常处理', tag: 'Python', time: '昨天 18:30' },
  { title: 'RAG 检索增强生成', tag: 'AI', time: '05-29 20:10' }
];
</script>

<template>
  <section class="page">
    <PageHeader title="笔记本" description="整理课程笔记、引用片段和个人复盘记录。">
      <template #actions><button>新建笔记</button></template>
    </PageHeader>
    <DataCard title="笔记列表" subtitle="按课程和知识点归档">
      <div class="list">
        <article v-for="note in notes" :key="note.title" class="item compact">
          <div><strong>{{ note.title }}</strong><p>{{ note.time }}</p></div>
          <StatusBadge :label="note.tag" tone="info" />
        </article>
      </div>
    </DataCard>
  </section>
</template>
