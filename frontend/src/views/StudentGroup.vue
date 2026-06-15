<script setup lang="ts">
import PageHeader from '../components/PageHeader.vue';
import DataCard from '../components/DataCard.vue';
import StatusBadge from '../components/StatusBadge.vue';

const posts = [
  { author: '李明', title: 'while 循环为什么会停不下来？', status: '讨论中' },
  { author: '陈浩', title: '循环嵌套变量变化表', status: '已共享' },
  { author: '王悦', title: 'break 和 continue 区分复盘', status: '待回复' }
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
