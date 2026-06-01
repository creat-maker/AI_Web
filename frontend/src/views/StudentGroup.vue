<script setup lang="ts">
import PageHeader from '../components/PageHeader.vue';
import DataCard from '../components/DataCard.vue';
import StatusBadge from '../components/StatusBadge.vue';

const posts = [
  { author: '李四', title: 'HTTP 请求头怎么设置？', status: '讨论中' },
  { author: '王五', title: '爬虫项目分工文档', status: '已共享' },
  { author: '赵六', title: '数据解析问题复盘', status: '待回复' }
];
</script>

<template>
  <section class="page">
    <PageHeader title="学习小组" description="小组协作、话题讨论和文件共享。">
      <template #actions><button>发起讨论</button></template>
    </PageHeader>
    <DataCard title="小组动态" subtitle="同伴互助学习记录">
      <div class="list">
        <article v-for="post in posts" :key="post.title" class="item compact">
          <div><strong>{{ post.title }}</strong><p>{{ post.author }}</p></div>
          <StatusBadge :label="post.status" :tone="post.status === '已共享' ? 'success' : 'purple'" />
        </article>
      </div>
    </DataCard>
  </section>
</template>
