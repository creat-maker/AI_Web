<script setup lang="ts">
import PageHeader from '../components/PageHeader.vue';
import DataCard from '../components/DataCard.vue';
import StatusBadge from '../components/StatusBadge.vue';
import StatCard from '../components/StatCard.vue';

const categories = [
  { title: '课程讲义', count: 80, icon: '讲' },
  { title: '实验指导', count: 66, icon: '实' },
  { title: '参考资料', count: 245, icon: '参' },
  { title: '项目案例', count: 49, icon: '案' }
];

const files = [
  { name: '第5章_函数式编程讲义.pdf', type: 'PDF', course: 'Python 高级编程', date: '2026-05-30' },
  { name: '数据解析实战.ipynb', type: 'Jupyter', course: 'Python 爬虫基础与实践', date: '2026-05-29' },
  { name: '栈与队列练习题.docx', type: 'DOCX', course: '数据结构与算法', date: '2026-05-28' },
  { name: '课程项目评分表.xlsx', type: 'Excel', course: '软件工程实践', date: '2026-05-27' },
  { name: 'RAG系统原理课件.pptx', type: 'PPT', course: '人工智能导论', date: '2026-05-26' }
];

const recent = files.slice(0, 3);
const hot = [
  { name: 'Python 快速入门.pdf', count: '1.2k' },
  { name: 'PyTorch 快速入门.ipynb', count: '986' },
  { name: '函数专项练习.docx', count: '842' }
];
</script>

<template>
  <section class="page knowledge-page">
    <PageHeader title="知识库 / 课程资料" description="集中管理课程资料、最近打开和热门下载。">
      <template #actions>
        <button class="secondary">筛选</button>
        <button>搜索资料</button>
      </template>
    </PageHeader>

    <div class="stat-grid">
      <StatCard label="资料总数" value="440" unit="份" hint="覆盖所有课程" icon="资" />
      <StatCard label="最近打开" value="12" unit="份" hint="近 7 天" icon="开" tone="green" />
      <StatCard label="热门下载" value="36" unit="次" hint="本周下载" icon="热" tone="orange" />
      <StatCard label="已收藏" value="18" unit="份" hint="个人收藏" icon="藏" tone="purple" />
    </div>

    <DataCard title="资料搜索" subtitle="按课程、知识点、文件名检索">
      <input placeholder="搜索课程资料、知识点、文件名..." />
    </DataCard>

    <DataCard title="资料分类" subtitle="常用资料类型">
      <div class="category-grid">
        <article v-for="item in categories" :key="item.title" class="category-card">
          <span>{{ item.icon }}</span>
          <strong>{{ item.title }}</strong>
          <p>{{ item.count }} 份资料</p>
        </article>
      </div>
    </DataCard>

    <div class="knowledge-layout">
      <DataCard title="文件列表" subtitle="支持预览和下载">
        <div class="file-list">
          <article v-for="file in files" :key="file.name" class="file-row">
            <div>
              <strong>{{ file.name }}</strong>
              <p>{{ file.course }} · {{ file.date }}</p>
            </div>
            <StatusBadge :label="file.type" tone="info" />
            <div class="row-actions">
              <button class="ghost">预览</button>
              <button class="secondary">下载</button>
            </div>
          </article>
        </div>
      </DataCard>

      <div class="side-stack">
        <DataCard title="最近打开">
          <div class="list">
            <div v-for="file in recent" :key="file.name" class="item">
              <strong>{{ file.name }}</strong>
              <p>{{ file.course }}</p>
            </div>
          </div>
        </DataCard>
        <DataCard title="热门下载">
          <div class="list">
            <div v-for="file in hot" :key="file.name" class="item compact">
              <strong>{{ file.name }}</strong>
              <span>{{ file.count }}</span>
            </div>
          </div>
        </DataCard>
      </div>
    </div>
  </section>
</template>

<style scoped>
.category-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.category-card {
  border: 1px solid var(--color-border);
  border-radius: 16px;
  padding: 14px;
  background: #fbfdff;
}

.category-card span {
  display: inline-grid;
  place-items: center;
  width: 42px;
  height: 42px;
  border-radius: 14px;
  color: #fff;
  font-weight: 800;
  background: linear-gradient(135deg, var(--color-primary), var(--color-purple));
}

.category-card p {
  margin: 6px 0 0;
}

.knowledge-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 340px;
  gap: 16px;
}

.file-list,
.side-stack {
  display: grid;
  gap: 12px;
}

.file-row {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto auto;
  gap: 12px;
  align-items: center;
  border-bottom: 1px solid #eef2f8;
  padding-bottom: 12px;
}

.file-row:last-child {
  border-bottom: 0;
  padding-bottom: 0;
}

.file-row p {
  margin: 4px 0 0;
  font-size: 13px;
}

.row-actions {
  display: flex;
  gap: 8px;
}

@media (max-width: 1180px) {
  .category-grid,
  .knowledge-layout {
    grid-template-columns: 1fr;
  }
}
</style>
