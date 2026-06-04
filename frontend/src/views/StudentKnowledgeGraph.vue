<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue';
import { GraphChart } from 'echarts/charts';
import { LegendComponent, TooltipComponent } from 'echarts/components';
import * as echarts from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { api } from '../api/client';
import { knowledgeGraph as fallbackGraph, statusMeta } from '../api/mocks/competitionData';
import DataCard from '../components/DataCard.vue';
import PageHeader from '../components/PageHeader.vue';
import ProgressBar from '../components/ProgressBar.vue';
import StatCard from '../components/StatCard.vue';
import StatusBadge from '../components/StatusBadge.vue';

echarts.use([GraphChart, LegendComponent, TooltipComponent, CanvasRenderer]);

type KnowledgeNode = typeof fallbackGraph.nodes[number];
type KnowledgeGraph = typeof fallbackGraph;

const graph = ref<KnowledgeGraph>(fallbackGraph);
const selected = ref<KnowledgeNode>(fallbackGraph.nodes[2]);
const graphEl = ref<HTMLDivElement | null>(null);
const loading = ref(true);
const error = ref('');
let chart: echarts.ECharts | null = null;

function renderGraph() {
  if (!graphEl.value) return;
  chart = chart || echarts.init(graphEl.value);
  const categories = Object.entries(statusMeta).map(([key, meta]) => ({ name: meta.label, itemStyle: { color: meta.color } }));
  chart.setOption({
    tooltip: {
      formatter: (params: any) => {
        const data = params.data || {};
        if (params.dataType === 'edge') return data.relation || '';
        return `${data.name}<br/>掌握率：${data.mastery}%<br/>状态：${data.status_label}`;
      }
    },
    legend: [{ bottom: 0, data: categories.map((item) => item.name) }],
    series: [
      {
        type: 'graph',
        layout: 'force',
        roam: true,
        top: 10,
        bottom: 46,
        symbolSize: (value: number) => Math.max(42, value * 0.72),
        categories,
        force: { repulsion: 260, edgeLength: [90, 160] },
        label: { show: true, color: '#0f172a', fontWeight: 700 },
        lineStyle: { color: '#94a3b8', width: 1.4, curveness: 0.12 },
        edgeLabel: { show: true, color: '#64748b', fontSize: 11, formatter: '{@relation}' },
        data: graph.value.nodes.map((node) => ({
          ...node,
          value: node.mastery,
          category: statusMeta[node.status]?.label || node.status_label,
          itemStyle: {
            color: statusMeta[node.status]?.color || '#64748b',
            borderColor: '#ffffff',
            borderWidth: 2
          }
        })),
        links: graph.value.links.map((link) => ({ ...link, value: link.relation }))
      }
    ]
  });
  chart.off('click');
  chart.on('click', (params: any) => {
    if (params.dataType !== 'node') return;
    const item = graph.value.nodes.find((node) => node.id === params.data.id);
    if (item) selected.value = item;
  });
}

async function loadGraph() {
  loading.value = true;
  error.value = '';
  try {
    graph.value = await api.get<KnowledgeGraph>('/api/v1/knowledge-graph');
    selected.value = graph.value.nodes.find((item) => item.status === 'weak') || graph.value.nodes[0];
  } catch (err) {
    error.value = err instanceof Error ? `后端知识图谱接口暂不可用，已使用本地演示数据：${err.message}` : '后端知识图谱接口暂不可用，已使用本地演示数据。';
    graph.value = fallbackGraph;
    selected.value = fallbackGraph.nodes[2];
  } finally {
    loading.value = false;
    await nextTick();
    renderGraph();
  }
}

function resize() {
  chart?.resize();
}

onMounted(() => {
  loadGraph();
  window.addEventListener('resize', resize);
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', resize);
  chart?.dispose();
});
</script>

<template>
  <section class="page knowledge-graph-page">
    <PageHeader title="课程知识图谱" description="围绕 Python 程序设计展示知识点依赖、掌握状态、推荐资源和下一步练习，形成可解释的个性化学习导航。">
      <template #actions>
        <RouterLink class="btn secondary" to="/student/learning-path">查看学习路径</RouterLink>
        <RouterLink class="btn" to="/student/smart-quiz">开始智能测验</RouterLink>
      </template>
    </PageHeader>

    <p v-if="loading" class="panel muted">正在加载课程知识图谱...</p>
    <p v-if="error" class="panel warning-text">{{ error }}</p>

    <div class="stat-grid">
      <StatCard label="课程" value="Python" hint="程序设计核心知识链" icon="Py" />
      <StatCard label="知识点" :value="graph.nodes.length" unit="个" hint="覆盖章节主干" icon="图" tone="purple" />
      <StatCard label="薄弱点" :value="graph.nodes.filter((item) => item.status === 'weak').length" unit="个" hint="用于驱动推荐" icon="弱" tone="orange" />
      <StatCard label="平均掌握率" :value="Math.round(graph.nodes.reduce((sum, item) => sum + item.mastery, 0) / graph.nodes.length)" unit="%" hint="规则演示，可替换模型" icon="率" tone="green" />
    </div>

    <div class="graph-layout">
      <DataCard title="Python 程序设计知识图谱" subtitle="节点大小代表掌握率，颜色代表学习状态；点击节点查看诊断和推荐。">
        <div ref="graphEl" class="graph-canvas"></div>
      </DataCard>

      <DataCard title="节点诊断卡" :subtitle="selected.name">
        <div class="node-detail">
          <div class="node-title-row">
            <strong>{{ selected.name }}</strong>
            <StatusBadge :label="selected.status_label" :tone="statusMeta[selected.status]?.tone || 'neutral'" />
          </div>
          <p>{{ selected.description }}</p>
          <div>
            <span class="muted-text">掌握率 {{ selected.mastery }}%</span>
            <ProgressBar :value="selected.mastery" :tone="selected.status === 'weak' ? 'warning' : selected.status === 'mastered' ? 'success' : 'primary'" />
          </div>
          <div class="detail-section">
            <span>推荐资源</span>
            <ul>
              <li v-for="item in selected.resources" :key="item">{{ item }}</li>
            </ul>
          </div>
          <div class="detail-section">
            <span>关联练习</span>
            <ul>
              <li v-for="item in selected.exercises" :key="item">{{ item }}</li>
            </ul>
          </div>
          <div class="ai-advice">
            <strong>AI 学习建议</strong>
            <p>{{ selected.ai_suggestion }}</p>
          </div>
        </div>
      </DataCard>
    </div>

    <DataCard title="闭环说明" :subtitle="graph.recommendation_policy">
      <div class="loop-strip">
        <span>学生画像</span>
        <span>知识图谱</span>
        <span>资源推荐</span>
        <span>智能测评</span>
        <span>错因分析</span>
        <span>教师干预</span>
        <span>平台治理</span>
      </div>
    </DataCard>
  </section>
</template>

<style scoped>
.graph-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.45fr) minmax(320px, 0.55fr);
  gap: 16px;
}

.graph-canvas {
  width: 100%;
  min-height: 520px;
}

.node-detail {
  display: grid;
  gap: 14px;
}

.node-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.node-title-row strong {
  font-size: 20px;
}

.detail-section {
  border-top: 1px solid var(--color-border);
  padding-top: 12px;
}

.detail-section span,
.muted-text {
  color: var(--color-text-sub);
  font-size: 13px;
}

.detail-section ul {
  margin: 8px 0 0;
  padding-left: 18px;
}

.ai-advice {
  border: 1px solid #bfdbfe;
  border-radius: 12px;
  padding: 12px;
  background: var(--color-primary-light);
}

.ai-advice p {
  margin: 8px 0 0;
}

.loop-strip {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 10px;
}

.loop-strip span {
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 10px;
  text-align: center;
  color: var(--color-primary-dark);
  background: #fff;
  font-weight: 700;
}

@media (max-width: 1100px) {
  .graph-layout,
  .loop-strip {
    grid-template-columns: 1fr;
  }
}
</style>
