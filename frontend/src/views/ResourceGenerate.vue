<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { api } from '../api/client';
import DataCard from '../components/DataCard.vue';
import PageHeader from '../components/PageHeader.vue';
import ProgressBar from '../components/ProgressBar.vue';
import StatCard from '../components/StatCard.vue';
import StatusBadge from '../components/StatusBadge.vue';

interface GeneratedResource {
  id?: number;
  title: string;
  resource_type?: string;
  source_agent?: string;
  created_at?: string;
}

const resources = ref<GeneratedResource[]>([]);
const loading = ref(true);
const error = ref('');

const fallbackResources: GeneratedResource[] = [
  { title: 'Python 爬虫分层练习题', resource_type: '习题', source_agent: '资源生成 Agent', created_at: '2024-05-31 10:20' },
  { title: 'HTTP 请求知识点讲义', resource_type: '知识点', source_agent: '知识解析 Agent', created_at: '2024-05-31 09:48' },
  { title: '班级学习报告初稿', resource_type: '报告', source_agent: '报告生成 Agent', created_at: '2024-05-30 18:12' },
  { title: 'Python 爬虫学习路径', resource_type: '学习路径', source_agent: '规划 Agent', created_at: '2024-05-30 16:36' }
];

const records = [
  { name: 'Python 爬虫分层练习题', type: '习题', owner: '王老师', status: '已完成', duration: '18s', time: '05-31 10:20' },
  { name: '课程效果报告初稿', type: '报告', owner: 'Admin', status: '生成中', duration: '32s', time: '05-31 10:12' },
  { name: '知识点诊断卡片', type: '知识点', owner: '张老师', status: '待审核', duration: '14s', time: '05-31 09:58' },
  { name: 'Web 前端课件提纲', type: '课件', owner: '李老师', status: '失败', duration: '9s', time: '05-30 20:40' }
];

const queue = [
  { name: '报告生成', progress: 72, status: '运行中' },
  { name: '资源安全检查', progress: 46, status: '排队中' },
  { name: '题库质量复核', progress: 88, status: '待审核' }
];

function statusTone(status: string) {
  if (status === '已完成') return 'success';
  if (status === '失败') return 'danger';
  if (status === '生成中' || status === '运行中') return 'purple';
  if (status === '待审核') return 'warning';
  return 'neutral';
}

async function loadResources() {
  loading.value = true;
  error.value = '';
  try {
    resources.value = await api.get<GeneratedResource[]>('/api/v1/resources');
  } catch (err) {
    error.value = err instanceof Error ? err.message : '资源生成接口暂不可用，当前显示演示队列。';
    resources.value = fallbackResources;
  } finally {
    loading.value = false;
  }
}

onMounted(loadResources);
</script>

<template>
  <section class="page">
    <PageHeader title="资源生成 / AI 资源管理" description="监控 AI 课件、习题、报告、知识点和学习路径生成任务。">
      <template #actions>
        <button>新建生成任务</button>
        <button class="secondary">模板管理</button>
      </template>
    </PageHeader>

    <p v-if="error" class="demo-banner">{{ error }}</p>

    <div class="stat-grid">
      <StatCard label="生成总数" :value="resources.length || 286" unit="份" icon="生" />
      <StatCard label="今日生成" value="42" unit="份" icon="今" tone="green" />
      <StatCard label="成功率" value="94.8" unit="%" icon="率" tone="cyan" />
      <StatCard label="失败任务" value="5" unit="项" icon="错" tone="red" />
      <StatCard label="平均耗时" value="18" unit="s" icon="耗" tone="orange" />
    </div>

    <div class="content-with-aside">
      <DataCard title="资源生成记录" subtitle="资源名称、类型、发起人、状态、耗时和时间">
        <template #action>
          <button class="secondary" :disabled="loading" @click="loadResources">{{ loading ? '刷新中' : '刷新' }}</button>
        </template>
        <div class="filter-row resource-generate-filter">
          <input placeholder="搜索资源名称、发起人..." />
          <select><option>全部类型</option><option>课件</option><option>习题</option><option>报告</option><option>知识点</option><option>学习路径</option></select>
          <select><option>全部状态</option><option>生成中</option><option>已完成</option><option>失败</option><option>待审核</option></select>
        </div>
        <table class="table">
          <thead>
            <tr>
              <th>资源名称</th>
              <th>类型</th>
              <th>发起人</th>
              <th>生成状态</th>
              <th>耗时</th>
              <th>时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in records" :key="row.name">
              <td><strong>{{ row.name }}</strong></td>
              <td><StatusBadge :label="row.type" tone="info" /></td>
              <td>{{ row.owner }}</td>
              <td><StatusBadge :label="row.status" :tone="statusTone(row.status)" /></td>
              <td>{{ row.duration }}</td>
              <td>{{ row.time }}</td>
              <td>
                <div class="row-actions">
                  <button class="ghost">预览</button>
                  <button class="ghost">审核</button>
                  <button class="ghost">日志</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </DataCard>

      <div class="side-stack">
        <DataCard title="AI 生成任务队列" subtitle="当前排队和运行状态">
          <div class="queue-list">
            <div v-for="item in queue" :key="item.name" class="queue-row">
              <div class="queue-head">
                <strong>{{ item.name }}</strong>
                <StatusBadge :label="item.status" :tone="statusTone(item.status)" />
              </div>
              <ProgressBar :value="item.progress" :tone="item.progress > 80 ? 'success' : item.progress < 50 ? 'warning' : 'primary'" />
            </div>
          </div>
        </DataCard>

        <DataCard title="风险提醒" subtitle="失败原因与治理建议">
          <div class="list">
            <div class="item compact"><strong>存储空间不足</strong><StatusBadge label="高风险" tone="danger" /></div>
            <div class="item compact"><strong>知识点引用缺失</strong><StatusBadge label="待复核" tone="warning" /></div>
            <div class="item compact"><strong>生成内容待审核</strong><StatusBadge label="12 份" tone="purple" /></div>
          </div>
        </DataCard>
      </div>
    </div>
  </section>
</template>

<style scoped>
.resource-generate-filter {
  grid-template-columns: minmax(260px, 1fr) 160px 160px;
}

.side-stack,
.queue-list,
.queue-row {
  display: grid;
  gap: 14px;
}

.queue-head,
.row-actions {
  display: flex;
  justify-content: space-between;
  gap: 8px;
  align-items: center;
}

.row-actions {
  justify-content: flex-start;
  flex-wrap: wrap;
}

@media (max-width: 820px) {
  .resource-generate-filter {
    grid-template-columns: 1fr;
  }
}
</style>
