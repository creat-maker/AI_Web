<script setup lang="ts">
import DataCard from '../components/DataCard.vue';
import PageHeader from '../components/PageHeader.vue';
import ProgressBar from '../components/ProgressBar.vue';
import StatCard from '../components/StatCard.vue';
import StatusBadge from '../components/StatusBadge.vue';

const categories = [
  { label: '课程资料', value: 128, tone: 'info' as const },
  { label: '题库资源', value: 86, tone: 'success' as const },
  { label: '知识点', value: 215, tone: 'purple' as const },
  { label: '实验案例', value: 64, tone: 'warning' as const }
];

const resources = [
  { name: 'Python 课程讲义.pdf', type: 'PDF', course: 'Python 爬虫基础与实践', owner: '王老师', size: '12.6 MB', status: '已发布', updated: '05-30 10:25' },
  { name: 'HTTP 请求实验案例.ipynb', type: 'Jupyter', course: 'Python 爬虫基础与实践', owner: '张老师', size: '8.9 MB', status: '解析中', updated: '05-30 09:42' },
  { name: '数据结构题库.docx', type: 'DOCX', course: '数据结构与算法', owner: '陈老师', size: '5.4 MB', status: '待审核', updated: '05-29 18:20' },
  { name: 'AI 服务质量月报.xlsx', type: 'Excel', course: '平台运营', owner: 'Admin', size: '2.1 MB', status: '已发布', updated: '05-29 16:05' }
];

function statusTone(status: string) {
  if (status === '已发布') return 'success';
  if (status === '解析中' || status === '待审核') return 'warning';
  return 'neutral';
}
</script>

<template>
  <section class="page">
    <PageHeader title="知识库运营 / 资源库" description="管理平台课程资料、题库资源、知识点切片和存储容量。">
      <template #actions>
        <button>上传资源</button>
        <button class="secondary">批量解析</button>
      </template>
    </PageHeader>

    <div class="stat-grid">
      <StatCard label="资源总数" value="2,846" unit="份" icon="资" />
      <StatCard label="课程资料" value="1,280" unit="份" icon="课" tone="green" />
      <StatCard label="题库资源" value="860" unit="份" icon="题" tone="orange" />
      <StatCard label="知识点" value="12,873" unit="个" icon="知" tone="purple" />
      <StatCard label="存储容量" value="68.4" unit="GB" icon="存" tone="cyan" />
    </div>

    <div class="category-grid">
      <DataCard v-for="item in categories" :key="item.label">
        <div class="category-card">
          <StatusBadge :label="item.label" :tone="item.tone" />
          <strong>{{ item.value }}</strong>
          <span>平台资源分类</span>
        </div>
      </DataCard>
    </div>

    <div class="content-with-aside">
      <DataCard title="资源列表" subtitle="资源名称、类型、所属课程、上传者和解析状态">
        <div class="filter-row resource-filter">
          <input placeholder="搜索资源名称、课程、上传者..." />
          <select><option>全部分类</option><option>课程资料</option><option>题库资源</option><option>知识点</option></select>
          <select><option>全部状态</option><option>已发布</option><option>解析中</option><option>待审核</option></select>
        </div>
        <table class="table">
          <thead>
            <tr>
              <th>资源名称</th>
              <th>类型</th>
              <th>所属课程</th>
              <th>上传者</th>
              <th>大小</th>
              <th>状态</th>
              <th>更新时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in resources" :key="item.name">
              <td><strong>{{ item.name }}</strong></td>
              <td><StatusBadge :label="item.type" tone="info" /></td>
              <td>{{ item.course }}</td>
              <td>{{ item.owner }}</td>
              <td>{{ item.size }}</td>
              <td><StatusBadge :label="item.status" :tone="statusTone(item.status)" /></td>
              <td>{{ item.updated }}</td>
              <td>
                <div class="row-actions">
                  <button class="ghost">预览</button>
                  <button class="ghost">下载</button>
                  <button class="ghost">审核</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </DataCard>

      <DataCard title="存储使用情况" subtitle="容量、解析队列和风险提醒">
        <div class="storage-card">
          <div>
            <strong>68.4 GB / 100 GB</strong>
            <span>当前存储使用率 68%</span>
          </div>
          <ProgressBar :value="68" tone="primary" />
        </div>
        <div class="list">
          <div class="item compact"><strong>解析队列</strong><StatusBadge label="12 个任务" tone="warning" /></div>
          <div class="item compact"><strong>低质量切片</strong><StatusBadge label="36 条" tone="danger" /></div>
          <div class="item compact"><strong>今日上传</strong><StatusBadge label="42 份" tone="success" /></div>
        </div>
      </DataCard>
    </div>
  </section>
</template>

<style scoped>
.category-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 14px;
}

.category-card {
  display: grid;
  gap: 8px;
}

.category-card strong {
  font-size: 26px;
}

.category-card span {
  color: var(--color-text-sub);
}

.resource-filter {
  grid-template-columns: minmax(260px, 1fr) 160px 160px;
}

.row-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.storage-card {
  display: grid;
  gap: 10px;
  margin-bottom: 16px;
  border-radius: 16px;
  padding: 14px;
  background: var(--color-primary-light);
}

.storage-card strong,
.storage-card span {
  display: block;
}

.storage-card span {
  margin-top: 4px;
  color: var(--color-text-sub);
}

@media (max-width: 820px) {
  .resource-filter {
    grid-template-columns: 1fr;
  }
}
</style>
