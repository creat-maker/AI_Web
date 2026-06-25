<script setup lang="ts">
import { ref } from 'vue';
import PageHeader from '../components/PageHeader.vue';

const query = ref('');
const items = [
  { title: '如何进入学生资源页', text: '使用学生端登录后，在左侧菜单选择学习资源，可按课程、类型和关键词过滤。' },
  { title: '如何创建课程', text: '教师端或管理员端进入课程管理，点击新建课程并提交表单，课程会写入后端。' },
  { title: '如何生成资源', text: '管理员端进入资源生成中心，选择课程和画像后生成资源包，学生端刷新即可查看。' },
  { title: '如何查看报告', text: '教师端进入报告中心，管理员端进入报告审核中心，可预览、导出和重新生成。' }
];

const filteredItems = () => {
  const word = query.value.trim().toLowerCase();
  if (!word) return items;
  return items.filter((item) => `${item.title} ${item.text}`.toLowerCase().includes(word));
};
</script>

<template>
  <section class="page">
    <PageHeader title="帮助中心" description="查看常见操作说明和关键业务入口。" />
    <article class="data-card">
      <input v-model="query" placeholder="搜索帮助内容，例如：课程、资源、报告" @keyup.enter.prevent />
      <div class="help-list">
        <article v-for="item in filteredItems()" :key="item.title" class="help-row">
          <strong>{{ item.title }}</strong>
          <p>{{ item.text }}</p>
        </article>
        <p v-if="!filteredItems().length" class="muted">未找到相关帮助内容。</p>
      </div>
    </article>
  </section>
</template>

<style scoped>
.help-list {
  display: grid;
  gap: 12px;
  margin-top: 16px;
}

.help-row {
  border: 1px solid var(--border-light);
  border-radius: 12px;
  padding: 14px;
  background: #fff;
}

.help-row p {
  margin: 6px 0 0;
  color: var(--text-secondary);
}
</style>
