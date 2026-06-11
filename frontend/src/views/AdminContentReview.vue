<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { api } from '../api/client';
import { adminReview } from '../api/mocks/competitionData';
import DataCard from '../components/DataCard.vue';
import PageHeader from '../components/PageHeader.vue';
import StatCard from '../components/StatCard.vue';
import StatusBadge from '../components/StatusBadge.vue';

type ReviewData = typeof adminReview;

const data = ref<ReviewData>(adminReview);
const error = ref('');
const loading = ref(true);
const statusFilter = ref('全部');
const auditFlow = ['资源 Agent 生成', '审核 Agent 初审', '管理员复核', '发布或驳回'];

const filteredItems = computed(() => data.value.items.filter((item) => statusFilter.value === '全部' || item.status === statusFilter.value));
const statusCount = computed(() => ({
  pending: data.value.items.filter((item) => item.status === '待审核').length,
  passed: data.value.items.filter((item) => item.status === '已通过').length,
  rejected: data.value.items.filter((item) => item.status === '已驳回').length
}));

function tone(status: string) {
  if (status === '已通过') return 'success';
  if (status === '已驳回') return 'danger';
  return 'warning';
}

function setStatus(id: string, status: string) {
  const item = data.value.items.find((row) => row.id === id);
  if (!item) return;
  item.status = status;
  item.review_opinion = status === '已通过' ? '模拟审核通过：内容已确认，可进入发布流程。' : status === '已驳回' ? '模拟驳回：请教师修订后重新提交。' : '已回到待审核队列。';
}

async function load() {
  loading.value = true;
  error.value = '';
  try {
    data.value = await api.get<ReviewData>('/api/v1/admin/content-review');
  } catch (err) {
    error.value = err instanceof Error ? `内容审核接口暂不可用，已使用本地演示数据：${err.message}` : '内容审核接口暂不可用，已使用本地演示数据。';
    data.value = adminReview;
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>

<template>
  <section class="page admin-content-review">
    <PageHeader title="AI 内容审核中心" description="展示 AI 生成资源的审核队列，体现生成内容需教师或管理员审核，不直接发布。">
      <template #actions>
        <RouterLink class="btn secondary" to="/dashboard">返回总览</RouterLink>
        <RouterLink class="btn" to="/admin/platform-quality">课程质量评价</RouterLink>
      </template>
    </PageHeader>

    <p v-if="loading" class="panel muted">正在加载 AI 内容审核列表...</p>
    <p v-if="error" class="panel warning-text">{{ error }}</p>

    <div class="stat-grid">
      <StatCard label="待审核" :value="statusCount.pending" unit="项" hint="需人工确认" icon="待" tone="orange" />
      <StatCard label="已通过" :value="statusCount.passed" unit="项" hint="可进入发布流程" icon="通" tone="green" />
      <StatCard label="已驳回" :value="statusCount.rejected" unit="项" hint="需修订后再提交" icon="驳" tone="red" />
      <StatCard label="审核策略" value="人工" hint="AI 辅助不替代审核" icon="审" tone="purple" />
    </div>

    <DataCard title="审核原则" :subtitle="data.policy">
      <div class="filter-row">
        <select v-model="statusFilter">
          <option>全部</option>
          <option>待审核</option>
          <option>已通过</option>
          <option>已驳回</option>
        </select>
      </div>
    </DataCard>

    <DataCard title="AI 生成资源审核流程" subtitle="展示资源从生成到发布的治理链路，AI 初审不替代管理员复核。">
      <div class="audit-flow">
        <article v-for="(step, index) in auditFlow" :key="step">
          <span>{{ index + 1 }}</span>
          <strong>{{ step }}</strong>
        </article>
      </div>
    </DataCard>

    <DataCard title="AI 生成资源审核列表" :subtitle="`${filteredItems.length} 项内容`">
      <div class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>资源标题</th>
              <th>资源类型</th>
              <th>生成来源</th>
              <th>风险标签</th>
              <th>审核状态</th>
              <th>审核意见</th>
              <th>模拟操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredItems" :key="item.id">
              <td><strong>{{ item.title }}</strong></td>
              <td>{{ item.resource_type }}</td>
              <td>{{ item.source }}</td>
              <td>
                <div class="tag-list">
                  <span v-for="tag in item.risk_tags" :key="tag">{{ tag }}</span>
                </div>
              </td>
              <td><StatusBadge :label="item.status" :tone="tone(item.status)" /></td>
              <td>{{ item.review_opinion }}</td>
              <td>
                <div class="row-actions">
                  <button class="secondary" @click="setStatus(item.id, '已通过')">通过</button>
                  <button class="danger" @click="setStatus(item.id, '已驳回')">驳回</button>
                  <button class="ghost" @click="setStatus(item.id, '待审核')">待审</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </DataCard>
  </section>
</template>

<style scoped>
.filter-row {
  max-width: 220px;
}

.table-wrap {
  overflow-x: auto;
}

.tag-list,
.row-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tag-list span {
  border-radius: 999px;
  padding: 5px 9px;
  color: var(--status-warning-text);
  background: var(--status-warning-bg);
  font-size: 12px;
}

.audit-flow {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.audit-flow article {
  display: grid;
  gap: 8px;
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 12px;
  background: #fff;
}

.audit-flow span {
  display: inline-grid;
  place-items: center;
  width: 30px;
  height: 30px;
  border-radius: 10px;
  color: var(--text-light);
  background: var(--color-primary);
  font-weight: 800;
}

@media (max-width: 900px) {
  .audit-flow {
    grid-template-columns: 1fr;
  }
}
</style>
