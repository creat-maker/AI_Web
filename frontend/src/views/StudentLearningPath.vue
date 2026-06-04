<script setup lang="ts">
import PageHeader from '../components/PageHeader.vue';
import DataCard from '../components/DataCard.vue';
import ProgressBar from '../components/ProgressBar.vue';
import StatCard from '../components/StatCard.vue';
import StatusBadge from '../components/StatusBadge.vue';

const nodes = [
  { title: '环境搭建与基础语法', desc: '完成 Python 环境与基础语法复盘', status: '已完成' },
  { title: '函数与 HTTP 请求', desc: '理解函数封装与 requests 基础', status: '已完成' },
  { title: '数据解析', desc: '掌握正则与 BeautifulSoup', status: '进行中' },
  { title: '数据存储与管理', desc: '完成 CSV / SQLite 数据保存', status: '未开始' },
  { title: '反爬策略与应对', desc: '了解请求头、频控和异常处理', status: '未开始' }
];

const resources = [
  { title: 'BeautifulSoup 速查手册', type: 'PDF', time: '12 分钟' },
  { title: '豆瓣电影采集案例', type: 'Jupyter', time: '25 分钟' },
  { title: '正则表达式练习题', type: 'DOCX', time: '10 分钟' }
];

const tasks = [
  { title: '完成数据解析章节练习', course: 'Python 爬虫基础与实践', status: '进行中' },
  { title: '整理 3 条异常处理笔记', course: 'Python 爬虫基础与实践', status: '未开始' },
  { title: '提交小型采集项目', course: 'Python 爬虫基础与实践', status: '未开始' }
];

function tone(status: string) {
  if (status === '已完成') return 'success';
  if (status === '进行中') return 'purple';
  return 'neutral';
}
</script>

<template>
  <section class="page student-path-page">
    <PageHeader title="学习路径" description="围绕当前学习方向展示路径节点、推荐资源和阶段任务。">
      <template #actions>
        <button class="secondary">调整路径</button>
        <button>继续学习</button>
      </template>
    </PageHeader>

    <div class="stat-grid">
      <StatCard label="当前方向" value="Python 爬虫" hint="工程实践成长路径" icon="向" />
      <StatCard label="路径进度" value="40" unit="%" hint="2 / 5 已完成" icon="进" tone="purple" />
      <StatCard label="阶段任务" value="3" unit="项" hint="当前节点待完成" icon="任" tone="orange" />
      <StatCard label="推荐资源" value="8" unit="份" hint="按薄弱点匹配" icon="资" tone="green" />
    </div>

    <DataCard title="当前学习方向" subtitle="Python 爬虫工程师成长路径">
      <div class="direction-card">
        <div>
          <strong>当前节点：数据解析</strong>
          <p>重点掌握 HTML 结构分析、正则表达式、BeautifulSoup 选择器和异常数据处理。</p>
        </div>
        <div>
          <span>路径完成度</span>
          <ProgressBar :value="40" />
        </div>
      </div>
    </DataCard>

    <DataCard title="路径节点步骤条" subtitle="已完成、进行中和未开始阶段清晰区分">
      <div class="path-step-grid">
        <article v-for="(node, index) in nodes" :key="node.title" :class="['path-step', node.status]">
          <span>{{ index + 1 }}</span>
          <strong>{{ node.title }}</strong>
          <p>{{ node.desc }}</p>
          <StatusBadge :label="node.status" :tone="tone(node.status)" />
        </article>
      </div>
    </DataCard>

    <div class="two-column">
      <DataCard title="推荐学习资源" subtitle="依据当前节点和薄弱点推荐">
        <div class="list">
          <article v-for="item in resources" :key="item.title" class="item compact">
            <div>
              <strong>{{ item.title }}</strong>
              <p>{{ item.type }} · 预计 {{ item.time }}</p>
            </div>
            <button class="secondary">打开</button>
          </article>
        </div>
      </DataCard>

      <DataCard title="阶段任务" subtitle="完成任务后自动推进路径">
        <div class="list">
          <article v-for="item in tasks" :key="item.title" class="item compact">
            <div>
              <strong>{{ item.title }}</strong>
              <p>{{ item.course }}</p>
            </div>
            <StatusBadge :label="item.status" :tone="tone(item.status)" />
          </article>
        </div>
      </DataCard>
    </div>
  </section>
</template>

<style scoped>
.direction-card {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 280px;
  gap: 16px;
  align-items: center;
}

.direction-card p {
  margin: 8px 0 0;
}

.path-step-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 12px;
}

.path-step {
  display: grid;
  gap: 8px;
  border: 1px solid var(--color-border);
  border-radius: 16px;
  padding: 14px;
  background: #fbfdff;
}

.path-step > span {
  display: inline-grid;
  place-items: center;
  width: 30px;
  height: 30px;
  border-radius: 10px;
  color: var(--text-secondary);
  background: var(--status-neutral-bg);
  font-weight: 800;
}

.path-step.已完成 > span {
  color: var(--status-success-text);
  background: var(--status-success-bg);
}

.path-step.进行中 {
  border-color: rgba(47, 107, 255, 0.55);
  background: var(--color-primary-light);
}

.path-step.进行中 > span {
  color: var(--text-light);
  background: linear-gradient(135deg, var(--color-primary), var(--color-purple));
}

.path-step p {
  margin: 0;
  font-size: 13px;
}

@media (max-width: 1180px) {
  .direction-card,
  .path-step-grid {
    grid-template-columns: 1fr;
  }
}
</style>
