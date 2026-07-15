<script setup lang="ts">
import PageHeader from '../components/PageHeader.vue';
import { useRole } from '../composables/useRole';

const { currentRoleLabel, demoUserLabel } = useRole();
</script>

<template>
  <section class="page">
    <PageHeader title="个人中心" description="查看当前账号、角色和最近学习/管理信息。" />
    <div class="profile-grid">
      <article class="data-card">
        <h2>账号信息</h2>
        <p><strong>当前角色：</strong>{{ currentRoleLabel }}</p>
        <p><strong>当前对象：</strong>{{ demoUserLabel }}</p>
        <p class="muted">账号信息用于驱动端侧菜单、路由权限和学习数据视图。</p>
      </article>
      <article class="data-card">
        <h2>近期关注</h2>
        <ul>
          <li>Python 程序设计 / 循环结构</li>
          <li>学习资源、测验评价和报告生成链路</li>
          <li>系统运行状态与关键数据量</li>
        </ul>
      </article>
    </div>
  </section>
</template>

<style scoped>
.profile-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

@media (max-width: 820px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }
}
</style>
