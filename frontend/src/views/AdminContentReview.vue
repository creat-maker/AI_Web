<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { api } from '../api/client';
import DataCard from '../components/DataCard.vue';
import PageHeader from '../components/PageHeader.vue';
import StatCard from '../components/StatCard.vue';
import StatusBadge from '../components/StatusBadge.vue';

interface ReviewItem {
  id: number;
  item_type: string;
  item_title: string;
  source_task_id?: number;
  status: string;
  actor_name?: string;
  reviewer_name?: string;
  review_comment?: string;
  created_at: string;
  reviewed_at?: string;
  published_at?: string;
  confidence?: number;
  risk_tip?: string;
  generation_basis?: string[];
  content?: {
    course?: string;
    student?: string;
    resources?: string[];
    risk_tip?: string;
    confidence?: number;
    generation_basis?: string[];
  };
}

const items = ref<ReviewItem[]>([]);
const loading = ref(false);
const message = ref('');
const error = ref('');
const statusFilter = ref('all');
const comment = ref('资源依据完整，建议发布后继续观察学习反馈。');

const fallbackItems: ReviewItem[] = [
  {
    id: 1,
    item_type: 'resource_pack',
    item_title: 'Python 循环结构个性化补弱资源包',
    source_task_id: 1,
    status: 'pending_review',
    actor_name: '王老师',
    created_at: new Date().toISOString(),
    confidence: 0.86,
    risk_tip: '引用完整，建议教师复核示例代码输出。',
    generation_basis: ['循环结构章节', 'while 循环错题', '代码实操偏好'],
    content: { course: 'Python 程序设计', student: '李*', resources: ['while 循环讲义', '循环嵌套练习', 'break / continue 代码案例'] }
  }
];

const filteredItems = computed(() =>
  items.value.filter((item) => statusFilter.value === 'all' || item.status === statusFilter.value)
);

const stats = computed(() => ({
  pending: items.value.filter((item) => item.status === 'pending_review').length,
  published: items.value.filter((item) => item.status === 'published' || item.status === 'approved').length,
  rejected: items.value.filter((item) => item.status === 'rejected').length,
  total: items.value.length
}));

function statusLabel(status: string) {
  const map: Record<string, string> = {
    pending_review: '待审核',
    approved: '已通过',
    published: '已发布',
    rejected: '已驳回',
    failed: '生成失败'
  };
  return map[status] || status;
}

function statusTone(status: string) {
  if (status === 'published' || status === 'approved') return 'success';
  if (status === 'rejected' || status === 'failed') return 'danger';
  if (status === 'pending_review') return 'warning';
  return 'info';
}

function typeLabel(type: string) {
  const map: Record<string, string> = {
    learning_path: '学习路径',
    resource_pack: '资源包',
    learning_report: '学情报告',
    tutor_qa: 'AI 答疑',
    student_profile: '学生画像'
  };
  return map[type] || type;
}

async function loadItems() {
  loading.value = true;
  error.value = '';
  try {
    items.value = await api.get<ReviewItem[]>('/api/v1/review-items');
  } catch (err) {
    error.value = err instanceof Error ? err.message : '审核中心暂不可用，当前展示本地复核队列。';
    items.value = fallbackItems;
  } finally {
    loading.value = false;
  }
}

async function approve(item: ReviewItem) {
  message.value = '';
  try {
    const updated = await api.post<ReviewItem>(`/api/v1/review-items/${item.id}/approve`, { comment: comment.value });
    Object.assign(item, updated);
    message.value = '审核通过，内容已发布到学生端，旧版本已进入历史版本。';
  } catch (err) {
    item.status = 'published';
    item.review_comment = comment.value;
    message.value = '本地复核状态已更新；接口不可用时不影响页面演示。';
  }
}

async function reject(item: ReviewItem) {
  message.value = '';
  try {
    const updated = await api.post<ReviewItem>(`/api/v1/review-items/${item.id}/reject`, { comment: comment.value || '驳回修改，学生端继续使用上一版内容。' });
    Object.assign(item, updated);
    message.value = '已驳回，学生端继续保留上一版已发布内容。';
  } catch {
    item.status = 'rejected';
    item.review_comment = comment.value || '驳回修改，学生端继续使用上一版内容。';
    message.value = '本地复核状态已更新；接口不可用时不影响页面演示。';
  }
}

async function createPendingTask() {
  loading.value = true;
  try {
    await api.post('/api/v1/tasks', { task_type: 'resource_pack', title: 'Python 循环结构个性化补弱资源包' });
    message.value = '已创建新的智能生成任务，并进入待审核。';
    await loadItems();
  } catch {
    items.value = fallbackItems;
    message.value = '已展示一条待审核任务。';
  } finally {
    loading.value = false;
  }
}

onMounted(loadItems);
</script>

<template>
  <section class="page admin-content-review">
    <PageHeader title="审核中心" description="AI 生成初稿进入待审核，教师或管理员复核后才发布到学生端。">
      <template #actions>
        <button class="secondary" :disabled="loading" @click="loadItems">{{ loading ? '刷新中...' : '刷新审核队列' }}</button>
        <button :disabled="loading" @click="createPendingTask">创建生成任务</button>
      </template>
    </PageHeader>

    <p v-if="message" class="panel success-text">{{ message }}</p>
    <p v-if="error" class="panel warning-text">{{ error }}</p>

    <div class="stat-grid">
      <StatCard label="待审核" :value="stats.pending" unit="项" icon="审" tone="orange" />
      <StatCard label="已发布" :value="stats.published" unit="项" icon="发" tone="green" />
      <StatCard label="已驳回" :value="stats.rejected" unit="项" icon="驳" tone="red" />
      <StatCard label="复核总数" :value="stats.total" unit="项" icon="总" tone="purple" />
    </div>

    <DataCard title="复核意见" subtitle="通过或驳回时写入审计日志">
      <div class="review-toolbar">
        <select v-model="statusFilter">
          <option value="all">全部状态</option>
          <option value="pending_review">待审核</option>
          <option value="published">已发布</option>
          <option value="rejected">已驳回</option>
        </select>
        <input v-model="comment" placeholder="填写审核意见" />
      </div>
    </DataCard>

    <DataCard title="Python 循环结构复核队列" :subtitle="`${filteredItems.length} 项内容`">
      <div class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>类型</th>
              <th>标题</th>
              <th>生成时间</th>
              <th>发起人</th>
              <th>状态</th>
              <th>置信度</th>
              <th>风险提示</th>
              <th>生成依据</th>
              <th>审核意见</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredItems" :key="item.id">
              <td>{{ typeLabel(item.item_type) }}</td>
              <td><strong>{{ item.item_title }}</strong><p>{{ item.content?.course || 'Python 程序设计' }} / {{ item.content?.student || '李*' }}</p></td>
              <td>{{ item.created_at }}</td>
              <td>{{ item.actor_name || '王老师' }}</td>
              <td><StatusBadge :label="statusLabel(item.status)" :tone="statusTone(item.status)" /></td>
              <td>{{ Math.round((item.confidence || item.content?.confidence || 0.86) * 100) }}%</td>
              <td>{{ item.risk_tip || item.content?.risk_tip || '引用完整，建议人工复核后发布。' }}</td>
              <td>{{ (item.generation_basis || item.content?.generation_basis || []).join('；') }}</td>
              <td>{{ item.review_comment || '待填写' }}</td>
              <td>
                <div class="row-actions">
                  <button class="secondary" :disabled="item.status !== 'pending_review'" @click="approve(item)">通过</button>
                  <button class="danger" :disabled="item.status !== 'pending_review'" @click="reject(item)">驳回</button>
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
.review-toolbar {
  display: grid;
  grid-template-columns: 180px minmax(260px, 1fr);
  gap: 12px;
}

.table-wrap {
  overflow-x: auto;
}

td p {
  margin: 6px 0 0;
  color: var(--text-muted);
  font-size: 12px;
}

.row-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

@media (max-width: 820px) {
  .review-toolbar {
    grid-template-columns: 1fr;
  }
}
</style>
