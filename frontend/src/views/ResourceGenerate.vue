<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { api } from '../api/client';
import DataCard from '../components/DataCard.vue';
import MindmapViewer from '../components/MindmapViewer.vue';
import PageHeader from '../components/PageHeader.vue';
import ProgressBar from '../components/ProgressBar.vue';
import StatCard from '../components/StatCard.vue';
import StatusBadge from '../components/StatusBadge.vue';

interface GeneratedResource {
  id?: number;
  title: string;
  resource_type?: string;
  content?: string;
  difficulty?: string;
  source_agent?: string;
  created_at?: string;
}

interface MindmapNode {
  label: string;
  children?: MindmapNode[];
}

interface MindmapData {
  root: MindmapNode;
}

const resources = ref<GeneratedResource[]>([]);
const loading = ref(true);
const error = ref('');

const fallbackResources: GeneratedResource[] = [
  { title: 'Python 爬虫分层练习题', resource_type: 'quiz', source_agent: '资源生成 Agent', created_at: '2024-05-31 10:20' },
  { title: 'HTTP 请求知识点讲义', resource_type: 'handout', source_agent: '知识解析 Agent', created_at: '2024-05-31 09:48' },
  { title: '班级学习报告初稿', resource_type: 'task', source_agent: '报告生成 Agent', created_at: '2024-05-30 18:12' },
  { title: 'Python 爬虫案例练习', resource_type: 'example', source_agent: '资源生成 Agent', created_at: '2024-05-30 16:36' },
  {
    title: 'Python 爬虫知识结构思维导图',
    resource_type: 'mindmap',
    source_agent: '资源生成 Agent',
    created_at: '2024-05-30 15:20',
    content: JSON.stringify({
      root: {
        label: 'Python 爬虫',
        children: [
          { label: '核心概念', children: [{ label: 'HTTP 请求' }, { label: 'HTML 解析' }, { label: '关键流程' }] },
          { label: '知识关联', children: [{ label: '概念层：术语定义与使用场景' }, { label: '应用层：案例与练习的映射' }] },
          { label: '学习路径', children: [{ label: '1. 掌握核心概念节点' }, { label: '2. 通过案例连接概念与应用' }] },
        ],
      },
    }),
  },
];

const queue = [
  { name: '报告生成', progress: 72, status: '运行中' },
  { name: '资源安全检查', progress: 46, status: '排队中' },
  { name: '题库质量复核', progress: 88, status: '待审核' },
];

/* ── 预览弹窗 ── */
const previewResource = ref<GeneratedResource | null>(null);
const previewOpen = ref(false);

function openPreview(resource: GeneratedResource) {
  previewResource.value = resource;
  previewOpen.value = true;
}

function closePreview() {
  previewOpen.value = false;
  previewResource.value = null;
}

const isMindmap = computed(() => previewResource.value?.resource_type === 'mindmap');

const mindmapData = computed<MindmapData | null>(() => {
  const content = previewResource.value?.content;
  if (!content) return null;
  try {
    return JSON.parse(content) as MindmapData;
  } catch {
    return null;
  }
});

/* ── 类型标签映射 ── */
const typeLabelMap: Record<string, string> = {
  handout: '讲义',
  example: '案例',
  quiz: '测验',
  task: '任务',
  mindmap: '思维导图',
  practice: '练习',
};

function displayType(type?: string): string {
  return typeLabelMap[type ?? ''] ?? type ?? '资源';
}

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
    error.value = err instanceof Error ? err.message : '资源生成接口暂不可用，当前显示演示数据。';
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
      <DataCard title="资源生成记录" subtitle="资源名称、类型、来源和预览">
        <template #action>
          <button class="secondary" :disabled="loading" @click="loadResources">{{ loading ? '刷新中' : '刷新' }}</button>
        </template>
        <div class="filter-row resource-generate-filter">
          <input placeholder="搜索资源名称..." />
          <select>
            <option>全部类型</option>
            <option value="handout">讲义</option>
            <option value="example">案例</option>
            <option value="quiz">测验</option>
            <option value="task">任务</option>
            <option value="mindmap">思维导图</option>
          </select>
        </div>
        <table class="table">
          <thead>
            <tr>
              <th>资源名称</th>
              <th>类型</th>
              <th>来源</th>
              <th>难度</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in resources" :key="item.id ?? item.title">
              <td><strong>{{ item.title }}</strong></td>
              <td><StatusBadge :label="displayType(item.resource_type)" tone="info" /></td>
              <td>{{ item.source_agent ?? '-' }}</td>
              <td>{{ item.difficulty ?? '-' }}</td>
              <td>{{ item.created_at?.slice(0, 10) ?? '-' }}</td>
              <td>
                <div class="row-actions">
                  <button class="ghost" @click="openPreview(item)">预览</button>
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

    <!-- 预览弹窗 -->
    <Teleport to="body">
      <div v-if="previewOpen" class="modal-overlay" @click.self="closePreview">
        <div class="modal-content">
          <div class="modal-header">
            <h3>{{ previewResource?.title }}</h3>
            <button class="ghost" @click="closePreview">关闭</button>
          </div>
          <div class="modal-body">
            <!-- 思维导图渲染 -->
            <template v-if="isMindmap && mindmapData">
              <MindmapViewer :data="mindmapData.root" />
            </template>
            <!-- 其他类型：纯文本展示 -->
            <template v-else>
              <pre class="content-text">{{ previewResource?.content || '暂无内容' }}</pre>
            </template>
          </div>
        </div>
      </div>
    </Teleport>
  </section>
</template>

<style scoped>
.resource-generate-filter {
  grid-template-columns: minmax(260px, 1fr) 160px;
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

/* ── 弹窗样式 ── */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: #ffffff;
  border-radius: 20px;
  width: min(90vw, 720px);
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 24px 80px rgba(0, 0, 0, 0.12);
  border: none;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px 28px 16px;
  border-bottom: none;
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
}

.modal-body {
  padding: 8px 28px 28px;
  overflow-y: auto;
  flex: 1;
  line-height: 1.6;
}

.content-text {
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 0.9rem;
  line-height: 1.6;
  color: #475569;
  background: #fafbfc;
  padding: 20px;
  border-radius: 12px;
  margin: 0;
  border: none;
}

@media (max-width: 820px) {
  .resource-generate-filter {
    grid-template-columns: 1fr;
  }
  .modal-content {
    width: 95vw;
  }
}
</style>
