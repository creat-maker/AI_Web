<script setup lang="ts">
import { ref } from 'vue';
import PageHeader from '../components/PageHeader.vue';

const message = ref('');
const preferences = ref({
  notifyReport: true,
  notifyResource: true,
  compactMode: false
});

function save() {
  localStorage.setItem('edumind.accountPreferences', JSON.stringify(preferences.value));
  message.value = '账号偏好已保存。';
}
</script>

<template>
  <section class="page">
    <PageHeader title="账号设置" description="管理当前账号的通知与界面偏好。" />
    <p v-if="message" class="panel success-text">{{ message }}</p>
    <article class="data-card settings-card">
      <label><input v-model="preferences.notifyReport" type="checkbox" /> 接收报告生成提醒</label>
      <label><input v-model="preferences.notifyResource" type="checkbox" /> 接收资源更新提醒</label>
      <label><input v-model="preferences.compactMode" type="checkbox" /> 使用紧凑信息密度</label>
      <button type="button" @click="save">保存设置</button>
    </article>
  </section>
</template>

<style scoped>
.settings-card {
  display: grid;
  gap: 14px;
  max-width: 560px;
}

.settings-card label {
  display: flex;
  gap: 10px;
  align-items: center;
}

.success-text {
  color: #047857;
}
</style>
