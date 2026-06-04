<script setup lang="ts">
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue';
import { BarChart, LineChart } from 'echarts/charts';
import { GridComponent, TooltipComponent } from 'echarts/components';
import * as echarts from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import DataCard from '../components/DataCard.vue';
import PageHeader from '../components/PageHeader.vue';
import ProgressBar from '../components/ProgressBar.vue';
import StatCard from '../components/StatCard.vue';
import StatusBadge from '../components/StatusBadge.vue';

echarts.use([BarChart, LineChart, GridComponent, TooltipComponent, CanvasRenderer]);

const trendEl = ref<HTMLDivElement | null>(null);
const distributionEl = ref<HTMLDivElement | null>(null);
let trendChart: echarts.ECharts | null = null;
let distributionChart: echarts.ECharts | null = null;

const records = [
  { title: 'Python 爬虫基础测验', score: 95, date: '2026-05-30', status: '通过' },
  { title: '数据结构章节测验', score: 88, date: '2026-05-18', status: '通过' },
  { title: '栈与队列小测', score: 76, date: '2026-05-15', status: '通过' },
  { title: '算法思维训练', score: 92, date: '2026-05-12', status: '通过' }
];

const weakPoints = [
  { name: '异常处理', value: 45 },
  { name: '递归调用', value: 33 },
  { name: '复杂度分析', value: 17 },
  { name: '文件操作', value: 5 }
];

function renderCharts() {
  if (trendEl.value) {
    trendChart = trendChart || echarts.init(trendEl.value);
    trendChart.setOption({
      color: ['#2f6bff'],
      tooltip: { trigger: 'axis' },
      grid: { left: 36, right: 14, top: 28, bottom: 28 },
      xAxis: { type: 'category', boundaryGap: false, data: ['04-20', '04-27', '05-04', '05-11', '05-18', '05-30'] },
      yAxis: { type: 'value', min: 0, max: 100, splitLine: { lineStyle: { color: '#edf2f8' } } },
      series: [{ type: 'line', smooth: true, areaStyle: { opacity: 0.08 }, data: [72, 76, 80, 84, 88, 95] }]
    });
  }
  if (distributionEl.value) {
    distributionChart = distributionChart || echarts.init(distributionEl.value);
    distributionChart.setOption({
      color: ['#7c5cff'],
      tooltip: { trigger: 'axis' },
      grid: { left: 36, right: 14, top: 28, bottom: 28 },
      xAxis: { type: 'category', data: ['90-100', '80-89', '70-79', '60-69', '<60'] },
      yAxis: { type: 'value', splitLine: { lineStyle: { color: '#edf2f8' } } },
      series: [{ type: 'bar', barWidth: 28, data: [2, 1, 1, 0, 0], itemStyle: { borderRadius: [8, 8, 0, 0] } }]
    });
  }
}

function resizeCharts() {
  trendChart?.resize();
  distributionChart?.resize();
}

onMounted(async () => {
  await nextTick();
  renderCharts();
  window.addEventListener('resize', resizeCharts);
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeCharts);
  trendChart?.dispose();
  distributionChart?.dispose();
});
</script>

<template>
  <section class="page exam-page">
    <PageHeader title="测验成绩" description="查看成绩统计、趋势、分布和薄弱知识点建议。">
      <template #actions>
        <button class="secondary">错题复盘</button>
        <button>开始练习</button>
      </template>
    </PageHeader>

    <div class="stat-grid">
      <StatCard label="平均分" value="86" unit="分" hint="较上次 +6" icon="均" />
      <StatCard label="最高分" value="98" unit="分" hint="Python 测验" icon="高" tone="green" />
      <StatCard label="测验次数" value="24" unit="次" hint="本学期" icon="测" tone="purple" />
      <StatCard label="通过率" value="92" unit="%" hint="4 次全部通过" icon="过" tone="cyan" />
    </div>

    <div class="two-column">
      <DataCard title="成绩趋势图" subtitle="最近测验成绩变化">
        <div ref="trendEl" class="chart-box"></div>
      </DataCard>
      <DataCard title="成绩分布图" subtitle="按分数段统计">
        <div ref="distributionEl" class="chart-box"></div>
      </DataCard>
    </div>

    <div class="two-column">
      <DataCard title="最近测验记录" subtitle="成绩、时间和状态">
        <div class="list">
          <article v-for="item in records" :key="item.title" class="item compact">
            <div>
              <strong>{{ item.title }}</strong>
              <p>{{ item.date }} · {{ item.score }} 分</p>
            </div>
            <StatusBadge :label="item.status" tone="success" />
          </article>
        </div>
      </DataCard>
      <DataCard title="薄弱知识点建议" subtitle="按错题和掌握度生成">
        <div class="weak-list">
          <div v-for="item in weakPoints" :key="item.name" class="weak-row">
            <span>{{ item.name }}</span>
            <ProgressBar :value="item.value" :tone="item.value > 40 ? 'warning' : 'primary'" />
            <strong>{{ item.value }}%</strong>
          </div>
        </div>
      </DataCard>
    </div>
  </section>
</template>

<style scoped>
.weak-list {
  display: grid;
  gap: 12px;
}

.weak-row {
  display: grid;
  grid-template-columns: 80px minmax(0, 1fr) 46px;
  gap: 10px;
  align-items: center;
}
</style>
